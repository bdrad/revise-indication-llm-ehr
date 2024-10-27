from prompt import generate_prompt
import polars as pl
import pandas as pd
import os
from huggingface_hub import login
from dotenv import load_dotenv
from transformers import pipeline
import tqdm

BASEPATH = "/mnt/sohn2022/Adrian/llm-revise-indication-notes/inference/results"
# MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"
MODEL_NAME = MODEL.replace("/", "_")

load_dotenv("/mnt/sohn2022/Adrian/Utils/Credentials/.env")
token = os.getenv("HUGGINGFACE_TOKEN")
login(token=token)

llm_balanced_test_dataset_results = pd.DataFrame(columns=[
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

llm_balanced_test_dataset_processed = pl.read_parquet("../dataset_curation/llm_balanced_test_dataset_processed.parquet").to_pandas()
llm_balanced_test_dataset_processed["prompt"] = llm_balanced_test_dataset_processed.apply(
    lambda row: generate_prompt(
        row["exam_type"], 
        row["original_indication"], 
        row["note_texts"]
    ), 
axis=1)
chatbot = pipeline("text-generation", model=MODEL, device="cuda:0")
for i in tqdm.tqdm(range(10)):
	test_row = llm_balanced_test_dataset_processed.iloc[i]
	prompt = test_row["prompt"]
	messages = [
		{"role": "user", "content": prompt},
	]
	llm_indication = chatbot(
		messages, 
		max_new_tokens=200
	)[0]["generated_text"][1]["content"]
	print("Generated Output:", llm_indication)
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
	llm_balanced_test_dataset_results.loc[len(llm_balanced_test_dataset_results)] = results_row

llm_balanced_test_dataset_results.to_csv(f"results/llm_balanced_test_dataset/{MODEL_NAME}.csv", index=False)
