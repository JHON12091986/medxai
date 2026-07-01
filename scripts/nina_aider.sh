#!/usr/bin/env bash
set -e

# Load from .env
if [ -f .env ]; then
  VAL=$(grep -E '^(export )?OPENROUTER_API_KEY=' .env | head -n 1 | cut -d= -f2- | tr -d '"' | tr -d "'" | xargs || true)
  if [ -z "$VAL" ]; then
    VAL=$(grep -E '^(export )?OPENROUTERAPIKEY=' .env | head -n 1 | cut -d= -f2- | tr -d '"' | tr -d "'" | xargs || true)
  fi
  
  if [ -n "$VAL" ]; then
    export OPENROUTER_API_KEY="$VAL"
  else
    echo "Warning: OPENROUTER_API_KEY or OPENROUTERAPIKEY not found in .env"
  fi
else
  echo "Warning: .env file not found"
fi

# Activate venv if it exists
if [ -d venv ]; then
  source venv/bin/activate
elif [ -d .venv ]; then
  source .venv/bin/activate
fi

# Launch aider in current git repo
exec aider "$@"
