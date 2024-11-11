import pandas as pd
import os
import evaluate
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import tqdm
import argparse

BASEPATH = "/mnt/sohn2022/Adrian/llm-revise-indication-notes/inference/results/llm_balanced_test_dataset"

MODEL_DICT = {
    "mistral": "mistralai_Mistral-7B-Instruct-v0.3",
    "llama": "meta-llama_Meta-Llama-3.1-8B-Instruct",
    "qwen": "Qwen_Qwen2.5-7B-Instruct",
    "gemma": "google_gemma-2-9b-it",
    "biomistral": "BioMistral_BioMistral-7B",
    "meditron": "OpenMeditron_Meditron3-8B",
    "gpt4o": "gpt4o",
}

rouge = evaluate.load('rouge')
def compute_rougeL_bootstrap_individual_scores(data, gt_col="radiologist_indication", pred_col="llm_indication", n_bootstrap=10000):
    predictions = data[pred_col].tolist()
    references = data[gt_col].tolist()
    n_samples = len(predictions)    
    individual_scores = []
    for i in tqdm.tqdm(range(len(predictions)), position=0, leave=True):
        rouge_score = rouge.compute(predictions=[predictions[i]], references=[references[i]])
        individual_scores.append(rouge_score['rougeL'] * 100)  
    
    individual_scores = np.array(individual_scores)    
    bootstrap_means = []
    for _ in range(n_bootstrap):
        resampled_scores = np.random.choice(individual_scores, size=n_samples, replace=True)
        bootstrap_means.append(np.mean(resampled_scores))
    
    bootstrap_means = np.array(bootstrap_means)    
    mean_score = np.mean(bootstrap_means)
    std_score = np.std(bootstrap_means)
    ci_lower = np.percentile(bootstrap_means, 2.5)
    ci_upper = np.percentile(bootstrap_means, 97.5)
    return mean_score, std_score, ci_lower, ci_upper

def main(args):
    result = {}
    if args.model not in MODEL_DICT:
        assert "Model is not registered. Please use a registered model."
    MODEL_NAME = MODEL_DICT[args.model]
    data = pd.read_csv(f"{BASEPATH}/{MODEL_NAME}_0_10000.csv", nrows=100).fillna("")
    mean_score, std_score, ci_lower, ci_upper = compute_rougeL_bootstrap_individual_scores(data, n_bootstrap=10000)
    result['model'] = MODEL_NAME
    result['rouge_mean'] = mean_score
    result['rouge_std'] = std_score
    result['rouge_ci_lower'] = ci_lower
    result['rouge_ci_upper'] = ci_upper
    result_df = pd.DataFrame(result, index=[0])
    result_df.to_csv(f"llm_evaluation_scores/{args.model}.csv", index=False)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument parser for model and metric selection")
    parser.add_argument("--model", type=str, required=True, help="Specify the model name or path")
    args = parser.parse_args()
    main(args)