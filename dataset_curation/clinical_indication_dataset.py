import os
import pandas as pd
import tqdm
import regex as re

RANDOM_STATE = 123

# Clinical Indication Dataset
clinical_indication_dataset = []
for i in tqdm.tqdm(range(1, 7)):
    clinical_indication_dataset.append(pd.read_parquet(f"clinical_indication_dataset_shard{i}.parquet"))
clinical_indication_dataset = pd.concat(clinical_indication_dataset)
print("Clinical Indication Dataset")
print("="*20)
n_radiology_clinical_indication_dataset = len(clinical_indication_dataset[~clinical_indication_dataset["exam_type"].isna()])
print("n_notes", len(clinical_indication_dataset))
print("n_patients", clinical_indication_dataset["patientdurablekey"].nunique())
print("n_radiology reports ", n_radiology_clinical_indication_dataset)

def categorize_body_group(exam_type):
    categories = {
        "Head": ["HEAD", "BRAIN", "STROKE PROTOCOL", "NEURO"],
        "Abdomen/Pelvis": ["ABDOMEN", "PELVIS", "PROSTATE", "RENAL", "MRCP", "UROGRAM"],
        "MSK": ["KNEE", "HIP", "SHOULDER", "EXTREMITY", "SPINE", "LUMBAR", 
                "CERVICAL", "SCOLIOSIS", "JOINT"],
        "Chest": ["CHEST", "CARDIAC", "PULMONARY EMBOLISM", "CTA", "HEART"],
        "Neck": ["FACE", "NECK", "CRANIOFACIAL", "MAXILLOFACIAL", "ORBIT", "TEMPORAL BONE", 
                 "SINUS", "THYROID", "MANDIBLE", "SKULL"]
    }
    
    for category, keywords in categories.items():
        if any(keyword in exam_type for keyword in keywords):
            return category
    return "Other"
def categorize_imaging_modality(exam_type):
    categories = {
        "MRI": ["MR", "MRI"],
        "CT": ["CT", "CTA"],
        "XR": ["XR"],
        "US": ["US"]
    }
    
    for category, keywords in categories.items():
        if any(keyword in exam_type for keyword in keywords):
            return category
    return "Other"

clinical_indication_dataset.loc[clinical_indication_dataset["exam_type"].notna(), "body_group"] = clinical_indication_dataset.loc[clinical_indication_dataset["exam_type"].notna()]["exam_type"].apply(categorize_body_group)
clinical_indication_dataset.loc[clinical_indication_dataset["exam_type"].notna(), "imaging_modality"] = clinical_indication_dataset.loc[clinical_indication_dataset["exam_type"].notna()]["exam_type"].apply(categorize_imaging_modality)

print(clinical_indication_dataset["body_group"].value_counts())
print(clinical_indication_dataset["body_group"].value_counts(normalize=True)*100)
print(clinical_indication_dataset["imaging_modality"].value_counts())
print(clinical_indication_dataset["imaging_modality"].value_counts(normalize=True)*100)

NUM_PER_BODY_SYSTEM = 2000
radiology_reports = clinical_indication_dataset[
    (~clinical_indication_dataset["exam_type"].isna()) & 
    (clinical_indication_dataset["body_group"] != "Other")
]
llm_dataset_sampled_reports = radiology_reports.groupby('body_group').sample(n=NUM_PER_BODY_SYSTEM, random_state=RANDOM_STATE)
llm_balanced_test_dataset = []
for i in tqdm.tqdm(range(len(llm_dataset_sampled_reports))):
    radiology_report = llm_dataset_sampled_reports.iloc[i]
    patient_mrn = radiology_report["patientdurablekey"]
    patient_notes = clinical_indication_dataset[clinical_indication_dataset["patientdurablekey"] == patient_mrn].copy()    
    filtered_patient_notes = patient_notes[
        (patient_notes["deid_service_date"] < radiology_report["deid_service_date"]) & 
        (patient_notes["note_type"] != "Imaging")
    ].sort_values(by=["deid_service_date"], ascending=False).reset_index(drop=True)
    llm_balanced_test_dataset.append(radiology_report.to_frame().T)
    llm_balanced_test_dataset.append(filtered_patient_notes)
llm_balanced_test_dataset = pd.concat(llm_balanced_test_dataset)
print("LLM Balanced Test Dataset")
print("="*20)
print("n_notes", len(llm_balanced_test_dataset))
print("n_patients", llm_balanced_test_dataset["patientdurablekey"].nunique())
print("n_radiology reports", len(llm_balanced_test_dataset[~llm_balanced_test_dataset["exam_type"].isna()]))

NUM_NOTES = 10
llm_balanced_test_dataset_processed = pd.DataFrame(columns=[
    "exam_type",
    "imaging_modality",
    "body_group",
    "report_text",
    "original_indication",
    "radiologist_indication",
    "enc_dept_names",
    "note_types",
    "auth_prov_types",
    "deid_service_dates",
    "note_texts"
])
for i in tqdm.tqdm(range(len(llm_dataset_sampled_reports))):
    radiology_report = llm_dataset_sampled_reports.iloc[i]
    patient_mrn = radiology_report["patientdurablekey"]
    patient_notes = clinical_indication_dataset[clinical_indication_dataset["patientdurablekey"] == patient_mrn].copy()    
    filtered_patient_notes = patient_notes[
        (patient_notes["deid_service_date"] < radiology_report["deid_service_date"]) & 
        (patient_notes["note_type"] != "Imaging")
    ].sort_values(by=["deid_service_date"], ascending=False).reset_index(drop=True)
    enc_dept_names = filtered_patient_notes[:NUM_NOTES][["enc_dept_name"]].squeeze().tolist()
    note_types = filtered_patient_notes[:NUM_NOTES][["note_type"]].squeeze().tolist()
    auth_prov_types = filtered_patient_notes[:NUM_NOTES][["auth_prov_type"]].squeeze().tolist()
    deid_service_dates = filtered_patient_notes[:NUM_NOTES][["deid_service_date"]].squeeze().tolist()
    note_texts = filtered_patient_notes[:NUM_NOTES][["note_text"]].squeeze().tolist()
    row = {
        "exam_type": radiology_report["exam_type"],
        "imaging_modality": radiology_report["imaging_modality"],
        "body_group": radiology_report["body_group"],
        "report_text": radiology_report["note_text"],
        "original_indication": radiology_report["original_indication"],
        "radiologist_indication": radiology_report["radiologist_indication"],
        "enc_dept_names": enc_dept_names,
        "note_types": note_types,
        "auth_prov_types": auth_prov_types,
        "deid_service_dates": deid_service_dates,
        "note_texts": note_texts
    }
    llm_balanced_test_dataset_processed.loc[
        len(llm_balanced_test_dataset_processed)
    ] = row
llm_balanced_test_dataset_processed.to_parquet("llm_balanced_test_dataset_processed.parquet")