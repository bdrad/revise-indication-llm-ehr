#!/bin/bash

MODELS=("mistral" "llama" "qwen" "gemma" "biomistral" "meditron" "gpt4o" "referring_physician")
for model in "${MODELS[@]}"; do
    printf '=%.0s' {1..20} 
	echo
	echo "$model" 
	printf '=%.0s' {1..20} 
    echo
    python evaluate_llm_outputs.py --model "$model"
done