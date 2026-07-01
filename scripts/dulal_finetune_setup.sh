#!/usr/bin/env bash
# ============================================================
# DULAL FINE-TUNE SETUP — Google Colab Notebook Generator
# M. Baizid Alam | NINA Project | aibony/nina
# Run: bash ~/nina/scripts/dulal_finetune_setup.sh
# Output: ~/nina/dulal_finetune_colab.ipynb
# ============================================================

set -e

OUTPUT="$(dirname "$0")/../dulal_finetune_colab.ipynb"
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
   "source": ["# DULAL Fine-Tune — Qwen2.5-Coder-3B-Instruct\n### Nina Project | M. Baizid Alam\n**Runtime → T4 GPU (free tier)**\n\n> Base: `unsloth/Qwen2.5-Coder-3B-Instruct` | Export: GGUF Q4_K_M for MX150 full offload"]
  },
  {
   "cell_type": "code",
   "metadata": {},
   "source": [
    "# STEP 1: Install dependencies\n",
    "!pip install -q unsloth transformers datasets trl peft\n",
    "!pip install -q 'unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git'\n",
    "print('Dependencies installed')"
   ],
   "execution_count": null, "outputs": []
  },
  {
   "cell_type": "code",
   "metadata": {},
   "source": [
    "# STEP 2: Load base model\n",
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
    "# STEP 3: Add LoRA adapters (fits T4 16GB easily)\n",
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
    "# -----------------------------------------------------------------------\n",
    "# OPTION A (default): Public Python coding dataset — baseline DULAL\n",
    "# OPTION B: Upload your Nina conversation logs as train.jsonl and\n",
    "#   replace dataset loading below with:\n",
    "#   dataset = load_dataset('json', data_files='train.jsonl', split='train')\n",
    "#   Format: {\"messages\":[{\"role\":\"system\",\"content\":\"...\"},{\"role\":\"user\",\"content\":\"...\"},{\"role\":\"assistant\",\"content\":\"...\"}]}\n",
    "# -----------------------------------------------------------------------\n",
    "from datasets import load_dataset\n",
    "\n",
    "SYSTEM_PROMPT = (\n",
    "    'You are DULAL, the local intelligence core of NINA, a personal AI '\n",
    "    'infrastructure built by M. Baizid Alam on ASUS VivoBook X530FN, '\n",
    "    'Ubuntu 26.04, Python 3.14.4. Output code only. No preamble. '\n",
    "    'If unsure, say ESCALATE.'\n",
    ")\n",
    "\n",
    "dataset = load_dataset('iamtarun/python_code_instructions_18k_alpaca', split='train[:3000]')\n",
    "\n",
    "def format_sample(sample):\n",
    "    return {\n",
    "        'text': tokenizer.apply_chat_template(\n",
    "            [\n",
    "                {\"role\": \"system\", \"content\": SYSTEM_PROMPT},\n",
    "                {\"role\": \"user\",   \"content\": sample.get('instruction', '')},\n",
    "                {\"role\": \"assistant\", \"content\": sample.get('output', '')}\n",
    "            ],\n",
    "            tokenize=False,\n",
    "            add_generation_prompt=False\n",
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
    "# STEP 5: Fine-tune (~25-40 min on T4)\n",
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
    "        logging_steps=25,\n",
    "        optim='adamw_8bit',\n",
    "        weight_decay=0.01,\n",
    "        lr_scheduler_type='linear',\n",
    "        seed=42,\n",
    "        output_dir='./dulal-output',\n",
    "        save_strategy='no',\n",
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
    "# STEP 6: Export to GGUF Q4_K_M (optimized for MX150 2GB VRAM)\n",
    "model.save_pretrained_gguf(\n",
    "    'dulal-3b-gguf',\n",
    "    tokenizer,\n",
    "    quantization_method='q4_k_m'\n",
    ")\n",
    "import os\n",
    "files = os.listdir('./dulal-3b-gguf')\n",
    "print('GGUF files:', files)"
   ],
   "execution_count": null, "outputs": []
  },
  {
   "cell_type": "code",
   "metadata": {},
   "source": [
    "# STEP 7: Download to your machine\n",
    "from google.colab import files\n",
    "import glob\n",
    "\n",
    "for f in glob.glob('./dulal-3b-gguf/*.gguf'):\n",
    "    print('Downloading:', f)\n",
    "    files.download(f)\n",
    "print('Check your browser downloads!')"
   ],
   "execution_count": null, "outputs": []
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## After Download — Run on your ASUS\n",
    "```bash\n",
    "# 1. Move GGUF\n",
    "mv ~/Downloads/dulal-3b-*.gguf ~/nina/\n",
    "\n",
    "# 2. Update Modelfile.dulal — change these TWO lines:\n",
    "#    FROM ./dulal-3b-q4_k_m.gguf\n",
    "#    PARAMETER num_gpu 99\n",
    "\n",
    "# 3. Rebuild\n",
    "cd ~/nina && ollama create dulal -f Modelfile.dulal\n",
    "\n",
    "# 4. Test\n",
    "ollama run dulal 'write a fastapi health endpoint'\n",
    "```\n",
    "> 3B Q4_K_M = ~1.8GB VRAM — fits fully in MX150 2GB. Expect 12-18 tok/s."
   ]
  }
 ]
}
NOTEBOOK

echo ""
echo "✅ Done! Notebook: $OUTPUT"
echo ""
echo "=== NEXT STEPS ==="
echo "1. git pull  (to get this script)"
echo "2. bash ~/nina/scripts/dulal_finetune_setup.sh"
echo "3. Upload dulal_finetune_colab.ipynb to colab.research.google.com"
echo "4. Runtime → T4 GPU → Run all"
echo "5. Download .gguf → mv to ~/nina/ → ollama create dulal"
