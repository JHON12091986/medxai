#!/usr/bin/env bash
# ============================================================
# DULAL FINE-TUNE SETUP — Google Colab Notebook Generator
# M. Baizid Alam | NINA Project | aibony/nina
# Run this on your local machine to generate the Colab .ipynb
# ============================================================

set -e

OUTPUT="dulal_finetune_colab.ipynb"
echo "[+] Generating Colab notebook: $OUTPUT"

cat > "$OUTPUT" << 'NOTEBOOK'
{
 "nbformat": 4,
 "nbformat_minor": 0,
 "metadata": {
  "colab": {"gpuType": "T4"},
  "kernelspec": {"display_name": "Python 3", "name": "python3"},
  "accelerator": "GPU"
 },
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": ["# DULAL Fine-Tune — Qwen2.5-Coder-3B-Instruct\n### Nina Project | M. Baizid Alam\n**Runtime → T4 GPU (free tier)**"]
  },
  {
   "cell_type": "code",
   "metadata": {},
   "source": [
    "# STEP 1: Install dependencies\n",
    "!pip install -q unsloth transformers datasets trl peft\n",
    "!pip install -q llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121"
   ],
   "execution_count": null, "outputs": []
  },
  {
   "cell_type": "code",
   "metadata": {},
   "source": [
    "# STEP 2: Load base model (Qwen2.5-Coder-3B-Instruct via Unsloth)\n",
    "from unsloth import FastLanguageModel\n",
    "import torch\n",
    "\n",
    "model, tokenizer = FastLanguageModel.from_pretrained(\n",
    "    model_name='unsloth/Qwen2.5-Coder-3B-Instruct',\n",
    "    max_seq_length=8192,\n",
    "    load_in_4bit=True,\n",
    "    dtype=None,\n",
    ")\n",
    "print('Model loaded:', model.config.model_type)"
   ],
   "execution_count": null, "outputs": []
  },
  {
   "cell_type": "code",
   "metadata": {},
   "source": [
    "# STEP 3: Add LoRA adapters\n",
    "model = FastLanguageModel.get_peft_model(\n",
    "    model,\n",
    "    r=16,\n",
    "    target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],\n",
    "    lora_alpha=16,\n",
    "    lora_dropout=0,\n",
    "    bias='none',\n",
    "    use_gradient_checkpointing='unsloth',\n",
    "    random_state=42,\n",
    ")\n",
    "print('LoRA adapters added')"
   ],
   "execution_count": null, "outputs": []
  },
  {
   "cell_type": "code",
   "metadata": {},
   "source": [
    "# STEP 4: Prepare dataset\n",
    "# Replace this with your own Nina conversation logs in train.jsonl\n",
    "# Format: {\"messages\": [{\"role\":\"user\",\"content\":\"...\"},{\"role\":\"assistant\",\"content\":\"...\"}]}\n",
    "from datasets import load_dataset\n",
    "\n",
    "# OPTION A: Use a public coding dataset as base (replace with your nina logs)\n",
    "dataset = load_dataset('iamtarun/python_code_instructions_18k_alpaca', split='train[:2000]')\n",
    "\n",
    "# Format into chat template\n",
    "def format_sample(sample):\n",
    "    return {\n",
    "        'text': tokenizer.apply_chat_template(\n",
    "            [{\"role\":\"system\",\"content\":\"You are DULAL, Nina's local AI core. Output code only. No preamble.\"},\n",
    "             {\"role\":\"user\",\"content\":sample.get('instruction','')},\n",
    "             {\"role\":\"assistant\",\"content\":sample.get('output','')}],\n",
    "            tokenize=False, add_generation_prompt=False\n",
    "        )\n",
    "    }\n",
    "\n",
    "dataset = dataset.map(format_sample)\n",
    "print('Dataset ready:', len(dataset), 'samples')"
   ],
   "execution_count": null, "outputs": []
  },
  {
   "cell_type": "code",
   "metadata": {},
   "source": [
    "# STEP 5: Fine-tune with SFTTrainer\n",
    "from trl import SFTTrainer\n",
    "from transformers import TrainingArguments\n",
    "\n",
    "trainer = SFTTrainer(\n",
    "    model=model,\n",
    "    tokenizer=tokenizer,\n",
    "    train_dataset=dataset,\n",
    "    dataset_text_field='text',\n",
    "    max_seq_length=8192,\n",
    "    packing=False,\n",
    "    args=TrainingArguments(\n",
    "        per_device_train_batch_size=2,\n",
    "        gradient_accumulation_steps=4,\n",
    "        warmup_steps=10,\n",
    "        num_train_epochs=2,\n",
    "        learning_rate=2e-4,\n",
    "        fp16=not torch.cuda.is_bf16_supported(),\n",
    "        bf16=torch.cuda.is_bf16_supported(),\n",
    "        logging_steps=10,\n",
    "        optim='adamw_8bit',\n",
    "        weight_decay=0.01,\n",
    "        lr_scheduler_type='linear',\n",
    "        seed=42,\n",
    "        output_dir='./dulal-output',\n",
    "    ),\n",
    ")\n",
    "\n",
    "trainer.train()\n",
    "print('Training complete!')"
   ],
   "execution_count": null, "outputs": []
  },
  {
   "cell_type": "code",
   "metadata": {},
   "source": [
    "# STEP 6: Export to GGUF Q4_K_M (for Ollama on your MX150)\n",
    "model.save_pretrained_gguf(\n",
    "    'dulal-3b-gguf',\n",
    "    tokenizer,\n",
    "    quantization_method='q4_k_m'\n",
    ")\n",
    "print('GGUF exported to ./dulal-3b-gguf/')\n",
    "import os\n",
    "for f in os.listdir('./dulal-3b-gguf'):\n",
    "    print(' -', f)"
   ],
   "execution_count": null, "outputs": []
  },
  {
   "cell_type": "code",
   "metadata": {},
   "source": [
    "# STEP 7: Download GGUF to local machine\n",
    "from google.colab import files\n",
    "import glob\n",
    "\n",
    "gguf_files = glob.glob('./dulal-3b-gguf/*.gguf')\n",
    "print('Files to download:', gguf_files)\n",
    "for f in gguf_files:\n",
    "    files.download(f)\n",
    "print('Download started — check your browser downloads!')"
   ],
   "execution_count": null, "outputs": []
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## After Download — Run on Your Machine\n",
    "```bash\n",
    "# Move GGUF to nina folder\n",
    "mv ~/Downloads/dulal-3b-*.gguf ~/nina/\n",
    "\n",
    "# Update Modelfile.dulal — change FROM line:\n",
    "# FROM ./dulal-3b-q4_k_m.gguf\n",
    "# PARAMETER num_gpu 99  (full offload — 3B fits in 2GB!)\n",
    "\n",
    "# Register with Ollama\n",
    "cd ~/nina && ollama create dulal -f Modelfile.dulal\n",
    "\n",
    "# Test\n",
    "ollama run dulal 'write a fastapi health endpoint'\n",
    "```"
   ]
  }
 ]
}
NOTEBOOK

echo "[+] Notebook generated: $OUTPUT"
echo "[+] Upload this to https://colab.research.google.com"
echo "[+] Runtime → Change runtime type → T4 GPU → Free tier"
echo "[+] Run all cells top to bottom"
echo ""
echo "=== LOCAL STEPS AFTER COLAB ==="
echo "1. Download dulal-3b-q4_k_m.gguf from Colab"
echo "2. mv ~/Downloads/dulal-3b-*.gguf ~/nina/"
echo "3. Edit Modelfile.dulal: change FROM line + set num_gpu 99"
echo "4. ollama create dulal -f ~/nina/Modelfile.dulal"
echo "5. ollama run dulal 'hello'"
