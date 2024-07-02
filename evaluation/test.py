import argparse
import pandas as pd
import json
import tqdm
import ast

from models.versa.chat import chat_gpt4o, chat_gpt4, chat_gpt4_turbo, chat_gpt3_5
from models.prompts import generate_prompt

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some arguments.")
    parser.add_argument("--model", type=str, required=True, choices=["gpt4", "gpt4o", "gpt4_turbo", "gpt3_5"], help="Model type to use.")
    parser.add_argument("--dataset", type=str, required=True, choices=["mimic_iii", "ucsf_ic"], help="Dataset to use.")
    parser.add_argument("--imaging_modality", type=str, required=True, choices=["XR", "CT", "MRI", "US"], help="Dataset to use.")
    parser.add_argument("--mimic_iii_csv_file", type=str, help="Path to MIMIC-III CSV file.")
    parser.add_argument("--ucsf_ic_csv_file", type=str, help="Path to UCSF-IC CSV file.")
    parser.add_argument("--clinical_information", action='store_true', help="Add clinical information.")
    
    args = parser.parse_args()

    if args.model == "gpt4":
        chat = chat_gpt4
    elif args.model == "gpt4o":
        chat = chat_gpt4o
    elif args.model == "gpt4_turbo":
        chat = chat_gpt4_turbo
    elif args.model == "gpt3_5":
        chat = chat_gpt3_5

    if args.dataset == "mimic_iii":
        data = pd.read_csv(args.mimic_iii_csv_file)
        data["NOTE_TEXTS"] = data["NOTE_TEXTS"].apply(ast.literal_eval)
        data = data[data['REPORT_TYPE'].str.startswith(args.imaging_modality)].reset_index(drop=True)
        data = data.dropna(subset=["RADIOLOGY_REPORT_INDICATION"]).drop_duplicates(subset=["SUBJECT_ID", "HADM_ID"])
    elif args.dataset == "ucsf_ic":
        data = pd.read_csv(args.ucsf_ic_csv_file)

    data = data.reset_index(drop=True)
    results = []
    for i in tqdm.tqdm(range(25)):
        row = data.iloc[i]
        prompt = generate_prompt(
            clinical_notes=row["NOTE_TEXTS"], 
            exam_type=row["REPORT_TYPE"],
            clinical_information=args.clinical_information
        )
        generated_indication = chat(prompt)
        result = {
            "SUBJECT_ID": int(row["SUBJECT_ID"]),
            "HADM_ID": int(row["HADM_ID"]),
            "REPORT_ID": row["REPORT_ID"],
            "RADIOLOGY_REPORT_DESCRIPTION": row["REPORT_TYPE"],
            "ORIGINAL_INDICATION": row["RADIOLOGY_REPORT_INDICATION"],
            "GENERATED_INDICATION": generated_indication
        }
        results.append(result)

    basepath = "/mnt/sohn2022/Adrian/clinical-notes-indication-generation"
    filename = f"{basepath}/data/results/{args.dataset}/base/{args.model}.json"
    if args.clinical_information:
        filename = f"{basepath}/data/results/{args.dataset}/clinical_information/{args.model}_{args.imaging_modality}.json"
    with open(filename, 'w') as outfile:
        json.dump(results, outfile, indent=4)