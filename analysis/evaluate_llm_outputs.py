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
    "referring_physician": "gpt4o"
}

def compute_rouge_scores(data, pred_col="llm_indication", gt_col="radiologist_indication", variant="rougeL"):
    rouge = evaluate.load('rouge')
    predictions = data[pred_col].tolist()
    references = data[gt_col].tolist()
    individual_scores = []
    for i in tqdm.tqdm(range(len(predictions)), position=0, leave=True):
        rouge_score = rouge.compute(predictions=[predictions[i]], references=[references[i]])
        individual_scores.append(rouge_score[variant])
    return np.array(individual_scores)

def main(args):
    save_dir_basepath = '/mnt/sohn2022/Adrian/llm-revise-indication-notes/analysis/llm_evaluation_scores'
    if args.model not in MODEL_DICT:
        assert "Model is not registered. Please use a registered model."
    MODEL_NAME = MODEL_DICT[args.model]

    data = pd.read_csv(f"{BASEPATH}/{MODEL_NAME}_0_10000.csv").fillna("")
    
    # ROUGE-L
    if args.model == "referring_physician":
        rouge_scores = compute_rouge_scores(data, pred_col="original_indication")
    else:
        rouge_scores = compute_rouge_scores(data)
    
    # MEDCON
    medcon_csv_path = f'{save_dir_basepath}/{args.model}_medcon_temp.csv'
    medcon_output_path = f'{save_dir_basepath}/{args.model}_medcon_scores.csv'
    if args.model == "referring_physician":
        medcon_csv = data[["radiologist_indication", "original_indication"]]
        medcon_csv = medcon_csv.rename(
            columns={
                "original_indication": "generated",
                "radiologist_indication": "reference"
            }
        )
    else:
        medcon_csv = data[["radiologist_indication", "llm_indication"]]
        medcon_csv = medcon_csv.rename(
            columns={
                "llm_indication": "generated",
                "radiologist_indication": "reference",
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
    
    # RadGraph-F1
    if args.model == "referring_physician":
        f1radgraph = F1RadGraph(reward_level="all")
        _, reward_list, _, _ = f1radgraph(
            hyps=data["original_indication"].tolist(), 
            refs=data["radiologist_indication"].tolist()
        )
    else:
        f1radgraph = F1RadGraph(reward_level="all")
        _, reward_list, _, _ = f1radgraph(
            hyps=data["llm_indication"].tolist(), 
            refs=data["radiologist_indication"].tolist()
        )
    radgraph_scores = np.array(reward_list[-1])

    model_scores = pd.DataFrame({
        "rouge": rouge_scores,
        "medcon": medcon_scores,
        "radgraph": radgraph_scores
    })
    data = pd.concat([data, model_scores], axis=1)
    data.to_csv(f"llm_evaluation_scores/{args.model}.csv", index=False)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument parser for model and metric selection")
    parser.add_argument("--model", type=str, required=True, help="Specify the model name or path")
    args = parser.parse_args()
    main(args)