#!/usr/bin/env bash
set -euo pipefail

echo "Writing GPU configuration drop-in..."
sudo mkdir -p /etc/systemd/system/ollama.service.d

sudo tee /etc/systemd/system/ollama.service.d/gpu.conf >/dev/null <<'EOF'
[Service]
Environment="OLLAMA_NUM_GPU=1"
Environment="CUDA_VISIBLE_DEVICES=0"
Environment="OLLAMA_GPU_OVERHEAD=52428800"
Environment="LLAMA_ARG_FIT_TARGET=50"
EOF

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Restarting Ollama service..."
sudo systemctl restart ollama

echo "Done! GPU fix applied successfully."
