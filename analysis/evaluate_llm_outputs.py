import pandas as pd
import os
import evaluate
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import tqdm
import argparse
import subprocess
from radgraph import F1RadGraph

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

def compute_rouge_scores(data, gt_col="radiologist_indication", pred_col="llm_indication", variant="rougeL"):
    rouge = evaluate.load('rouge')
    predictions = data[pred_col].tolist()
    references = data[gt_col].tolist()
    individual_scores = []
    for i in tqdm.tqdm(range(len(predictions)), position=0, leave=True):
        rouge_score = rouge.compute(predictions=[predictions[i]], references=[references[i]])
        individual_scores.append(rouge_score[variant])
    return np.array(individual_scores)

def bootstrap_ci(scores, n_bootstrap=10000, confidence_level=95):
    n_samples = len(scores)
    bootstrap_means = []
    for _ in range(n_bootstrap):
        resampled_scores = np.random.choice(scores, size=n_samples, replace=True)
        bootstrap_means.append(np.mean(resampled_scores))
    bootstrap_means = np.array(bootstrap_means)
    mean_score = np.mean(bootstrap_means)
    std_score = np.std(bootstrap_means)    
    lower_percentile = (100 - confidence_level) / 2
    upper_percentile = 100 - lower_percentile
    ci_lower = np.percentile(bootstrap_means, lower_percentile)
    ci_upper = np.percentile(bootstrap_means, upper_percentile)
    return mean_score, std_score, ci_lower, ci_upper

def main(args):
    save_dir_basepath = '/mnt/sohn2022/Adrian/llm-revise-indication-notes/analysis/llm_evaluation_scores'
    if args.model not in MODEL_DICT:
        assert "Model is not registered. Please use a registered model."
    MODEL_NAME = MODEL_DICT[args.model]
    result = {'model': MODEL_NAME}
    data = pd.read_csv(f"{BASEPATH}/{MODEL_NAME}_0_10000.csv", nrows=100).fillna("")
    
    # ROUGE-L
    rouge_scores = compute_rouge_scores(data)
    result['rouge_mean'], result['rouge_std'], result['rouge_ci_lower'], result['rouge_ci_upper'] = bootstrap_ci(rouge_scores, n_bootstrap=10000)
    
    # MEDCON
    medcon_csv_path = f'{save_dir_basepath}/{args.model}_medcon_temp.csv'
    medcon_output_path = f'{save_dir_basepath}/{args.model}_medcon_scores.csv'
    medcon_csv = data[["radiologist_indication", "llm_indication"]]
    medcon_csv = medcon_csv.rename(
        columns={
            "radiologist_indication": "reference",
            "llm_indication": "generated"
        }
    )
    medcon_csv.to_csv(medcon_csv_path, index=False)
    python_path = "/home/bdrad/miniconda3/bin/python"
    subprocess.run([
        python_path, '/mnt/sohn2022/Adrian/Utils/Evaluation/MEDCON/main.py',
        f"--csv_path={medcon_csv_path}",
        f"--output_path={medcon_output_path}",
    ])
    medcon_scores = np.array(pd.read_csv(medcon_output_path)["MEDCON_Score"].values)
    result['medcon_mean'], result['medcon_std'], result['medcon_ci_lower'], result['medcon_ci_upper'] = bootstrap_ci(medcon_scores, n_bootstrap=10000)
    
    # RadGraph-F1
    f1radgraph = F1RadGraph(reward_level="all")
    _, reward_list, _, _ = f1radgraph(
        hyps=data["radiologist_indication"].tolist(), 
        refs=data["original_indication"].tolist()
    )
    radgraph_scores = np.array(reward_list[-1])
    result['radgraph_mean'], result['radgraph_std'], result['radgraph_ci_lower'], result['radgraph_ci_upper'] = bootstrap_ci(radgraph_scores, n_bootstrap=10000)

    result_df = pd.DataFrame(result, index=[0])
    result_df.to_csv(f"llm_evaluation_scores/{args.model}.csv", index=False)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument parser for model and metric selection")
    parser.add_argument("--model", type=str, required=True, help="Specify the model name or path")
    args = parser.parse_args()
    main(args)