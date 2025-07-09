MODELS=(
  "mistralai/Mistral-7B-Instruct-v0.3"
  "meta-llama/Meta-Llama-3.1-8B-Instruct"
  "BioMistral/BioMistral-7B"
  "OpenMeditron/Meditron3-8B"
  "Qwen/Qwen2.5-7B-Instruct"
)

for MODEL in "${MODELS[@]}"; do
    echo "Running evaluation for model: $MODEL"
    python huggingface/run.py --model "$MODEL"
done

REASONING_MODELS=(
  "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
  "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
)

for MODEL in "${REASONING_MODELS[@]}"; do
    echo "Running evaluation for model: $MODEL"
    python huggingface/run.py --model "$MODEL" --reasoning
done

