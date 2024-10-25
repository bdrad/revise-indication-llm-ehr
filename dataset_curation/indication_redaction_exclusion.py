import os
import pandas as pd
import tqdm
import regex as re

start_shard = 6
print(f"Shard {start_shard}")
print('-'*20)
clinical_indication_dataset = pd.read_parquet(f"clinical_indication_dataset_shard{start_shard}.parquet")

print("="*20)
print("Radiology Report without Redaction of Original Indication and Revised Indication")
print("="*20)
patient_mrns = clinical_indication_dataset["patientdurablekey"].unique()
filtered_data_report_redactions = []
for i in tqdm.tqdm(range(len(patient_mrns))):
    patient_mrn = patient_mrns[i]
    patient_notes = clinical_indication_dataset[clinical_indication_dataset["patientdurablekey"] == patient_mrn]
    radiology_reports = patient_notes[
        (~patient_notes["exam_type"].isna()) & 
        (~patient_notes["original_indication"].astype(str).str.contains("\*")) &
        (~patient_notes["radiologist_indication"].astype(str).str.contains("\*"))
    ].copy()    
    for j in range(len(radiology_reports)):
        radiology_report = radiology_reports.iloc[j]
        filtered_patient_notes = patient_notes[
            (patient_notes["deid_service_date"] < radiology_report["deid_service_date"]) & 
            (patient_notes["note_type"] != "Imaging")
        ].sort_values(by=["deid_service_date"], ascending=False).reset_index(drop=True)
        filtered_data_report_redactions.append(radiology_report.to_frame().T)
        filtered_data_report_redactions.append(filtered_patient_notes)
filtered_data_report_redactions = pd.concat(filtered_data_report_redactions).drop_duplicates(subset=["deid_note_key"])
n_indication_redaction_radiology = len(filtered_data_report_redactions[~filtered_data_report_redactions["exam_type"].isna()])
n_clinical_indication_radiology = len(clinical_indication_dataset[~clinical_indication_dataset["exam_type"].isna()])
print("n_notes", len(filtered_data_report_redactions))
print("n_patients", filtered_data_report_redactions["patientdurablekey"].nunique())
print("n_radiology reports ", n_indication_redaction_radiology)
print('-'*20)
print('Clinical notes associated with a radiology report that has indications with redactions')
print("-"*20)
print("n_notes (excluded)", len(clinical_indication_dataset) - len(filtered_data_report_redactions))
print("n_patients (excluded)", clinical_indication_dataset["patientdurablekey"].nunique() - filtered_data_report_redactions["patientdurablekey"].nunique())
print("n_radiology reports (excluded)", n_clinical_indication_radiology - n_indication_redaction_radiology)
filtered_data_report_redactions.to_parquet(f"clinical_indication_dataset_without_redactions_shard{start_shard}.parquet")
