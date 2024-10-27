from prompt import generate_prompt
import polars as pl
import pandas as pd
from vllm import LLM
from vllm.sampling_params import SamplingParams
import os
from huggingface_hub import login
from dotenv import load_dotenv

BASEPATH = "/mnt/sohn2022/Adrian/llm-revise-indication-notes/inference/results"
MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
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
sampling_params = SamplingParams(max_tokens=100)
llm = LLM(model=MODEL, tokenizer_mode="mistral", config_format="mistral", load_format="mistral")
messages = []
for i in range(100):
	test_row = llm_balanced_test_dataset_processed.iloc[i]
	prompt = test_row["prompt"]
	messages.append([
		{
			"role": "user",
			"content": prompt
		}
	])
outputs = llm.chat(messages, sampling_params=sampling_params, use_tqdm=True)
for i in range(len(outputs)):
	test_row = llm_balanced_test_dataset_processed.iloc[i]
	llm_indication = outputs[i].outputs[0].text
	print("Generated Output:",llm_indication)
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
