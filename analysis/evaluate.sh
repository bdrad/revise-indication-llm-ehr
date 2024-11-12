#!/bin/bash

MODELS=("mistral" "llama" "qwen" "gemma" "biomistral" "meditron" "gpt4o")
for model in "${MODELS[@]}"; do
    printf '=%.0s' {1..20} 
    echo
    python evaluate_llm_outputs.py --model "$model"
done