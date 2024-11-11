from prompt import generate_prompt
from utils import chat

import polars as pl
import pandas as pd
import os
from huggingface_hub import login
from dotenv import load_dotenv
from transformers import pipeline
import tqdm
import torch

DATASET = "llm_balanced_test_dataset"
BASEPATH = "/mnt/sohn2022/Adrian/llm-revise-indication-notes/inference/results"
MODEL = MODEL_NAME = "gpt4o"

print(MODEL)
print("="*20)
MODEL_NAME = MODEL.replace("/", "_")

load_dotenv("/mnt/sohn2022/Adrian/Utils/Credentials/.env")
token = os.getenv("HUGGINGFACE_TOKEN")
login(token=token)

dataset_results = pd.DataFrame(columns=[
	"patientdurablekey",
	"exam_type",
	"body_group",
	"imaging_modality",
	"report_deid_note_key",
    "report_text",
    "original_indication",
    "radiologist_indication",
	"llm_indication"
])
dataset_processed = pl.read_parquet(f"/mnt/sohn2022/Adrian/llm-revise-indication-notes/dataset_curation/{DATASET}_processed.parquet").to_pandas()
dataset_processed["prompt"] = dataset_processed.apply(
    lambda row: generate_prompt(
        row["exam_type"], 
        row["original_indication"], 
        row["note_texts"]
    ), 
axis=1).str.replace(r"\*\*\*\*\*", "", regex=True)

start_idx = 9000
# end_idx = len(dataset_processed)
end_idx = 10000

for i in tqdm.tqdm(range(start_idx, end_idx)):
	test_row = dataset_processed.iloc[i]
	prompt = test_row["prompt"]
	messages = [
		{"role": "user", "content": prompt},
	]
	llm_indication = chat(prompt, MODEL)
	results_row = {
		"patientdurablekey": test_row["patientdurablekey"],
		"exam_type": test_row["exam_type"],
		"body_group": test_row["body_group"],
		"imaging_modality": test_row["imaging_modality"],
		"report_deid_note_key": test_row["report_deid_note_key"],
		"report_text": test_row["report_text"],
		"original_indication": test_row["original_indication"],
		"radiologist_indication": test_row["radiologist_indication"],
		"llm_indication": llm_indication
	}
	dataset_results.loc[len(dataset_results)] = results_row

dataset_results.to_csv(f"{BASEPATH}/{DATASET}/{MODEL_NAME}_{start_idx}_{end_idx}.csv", index=False)
