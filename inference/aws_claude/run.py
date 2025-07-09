from prompt import generate_prompt
from utils import chat_claude3_5

import polars as pl
import pandas as pd
import os
from huggingface_hub import login
from dotenv import load_dotenv
from transformers import pipeline
import tqdm
import torch

# DATASET = "llm_automated_evaluation_dataset"
DATASET = "reader_evaluation_dataset"
BASEPATH = "/mnt/sohn2022/Adrian/rad-llm-pmhx/inference/results"
MODEL = MODEL_NAME = "claude3_5"

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

start_idx = 0
end_idx = len(dataset_processed)

for i in tqdm.tqdm(range(start_idx, end_idx)):
	test_row = dataset_processed.iloc[i]
	prompt = test_row["prompt"]
	messages = [
		{"role": "user", "content": prompt},
	]
	llm_indication = chat_claude3_5(prompt)
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
