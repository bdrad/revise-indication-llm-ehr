from prompt import generate_prompt
import polars as pl
import pandas as pd
import os
from huggingface_hub import login
from dotenv import load_dotenv
from transformers import pipeline
import tqdm
import torch
import argparse

DATASET = "reader_evaluation_dataset"
BASEPATH = "/mnt/sohn2022/Adrian/rad-llm-pmhx/inference/results"

def main(args):
    MODEL = args.model

    print(MODEL)
    print("="*20)
    MODEL_NAME = MODEL.replace("/", "_")

    load_dotenv("/mnt/sohn2022/Adrian/Utils/Credentials/.env")
    token = os.getenv("HUGGINGFACE_TOKEN")
    login(token=token)

    dataset_results = pd.DataFrame(columns=[
        "patientdurablekey",
        "exam_type",
        "body_system",
        "pathophysiological_category",
        "imaging_modality",
        "radiology_deid_note_key",
        "radiology_text",
        "original_history",
        "additional_history",
        "llm_indication"
    ])
    dataset_processed = pd.read_parquet(
        f"/mnt/sohn2022/Adrian/rad-llm-pmhx/dataset/{DATASET}.parquet"
    )
    dataset_processed["prompt"] = dataset_processed.apply(
        lambda row: generate_prompt(
            row["exam_type"], 
            row["original_history"], 
            row["note_texts"]
        ), 
    axis=1).str.replace(r"\*\*\*\*\*", "", regex=True)
    chatbot = pipeline(
        "text-generation",
        model=MODEL, 
        device="cuda",
        torch_dtype=torch.float16
    )

    start_idx = 0
    end_idx = len(dataset_processed)

    for i in tqdm.tqdm(range(start_idx, end_idx)):
        test_row = dataset_processed.iloc[i]
        prompt = test_row["prompt"]
        messages = [
            {"role": "user", "content": prompt},
        ]
        max_new_tokens = 200
        if args.reasoning:
            max_new_tokens = 500

        llm_indication = chatbot(
            messages, 
            max_new_tokens=max_new_tokens,
            pad_token_id=chatbot.tokenizer.eos_token_id
        )[0]["generated_text"][1]["content"]

        if args.reasoning and "</think>" in llm_indication:
            llm_indication = llm_indication.split("</think>")[1].strip()

        results_row = {
            "patientdurablekey": test_row["patientdurablekey"],
            "exam_type": test_row["exam_type"],
            "body_system": test_row["body_system"],
            "pathophysiological_category": test_row["pathophysiological_category"],
            "imaging_modality": test_row["imaging_modality"],
            "radiology_deid_note_key": test_row["radiology_deid_note_key"],
            "radiology_text": test_row["radiology_text"],
            "original_history": test_row["original_history"],
            "additional_history": test_row["additional_history"],
            "llm_indication": llm_indication
        }
        dataset_results.loc[len(dataset_results)] = results_row

    dataset_results.to_csv(f"{BASEPATH}/{DATASET}/{MODEL_NAME}_{start_idx}_{end_idx}.csv", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Automated Evaluation")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-7B-Instruct", help="Model to use for evaluation")
    parser.add_argument("--reasoning", action="store_true", help="Enable reasoning model for evaluation")
    args = parser.parse_args()
    main(args)