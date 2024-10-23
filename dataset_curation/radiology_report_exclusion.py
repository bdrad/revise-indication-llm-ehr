import os
import pandas as pd
import tqdm
import regex as re

start_shard = 2
print(f"Shard {start_shard}")
print('-'*20)
filtered_data_note_type = pd.read_parquet(f"filtered_data_note_type_shard{start_shard}.parquet")

# Radiology Report Exclusion
# We filter out all the radiology reports with an additional history of `None` and other miscellaneous preprocessing steps. We also make sure to filter out all notes that occur before the `deid_service_date` of the radiological exam. We assume that all previous notes that will not mention the radiology report to prevent data leakage.
print("="*20)
print("Clinical Indication Dataset")
print("="*20)
patient_mrns = filtered_data_note_type["patientdurablekey"].unique()
filtered_data_radiology_report = []
for i in tqdm.tqdm(range(len(patient_mrns))):
    patient_mrn = patient_mrns[i]
    patient_notes = filtered_data_note_type[filtered_data_note_type["patientdurablekey"] == patient_mrn]
    radiology_reports = patient_notes[
        (patient_notes["note_type"] == "Imaging") &
        (patient_notes["auth_prov_type"].isna()) & 
        (~patient_notes["note_text"].str.contains("RADIOLOGY PRELIMINARY INTERPRETATION")) &
        (~patient_notes["note_text"].str.contains("ADDITIONAL HISTORY: None")) &
        (patient_notes["note_text"].str.contains("ADDITIONAL HISTORY"))  
    ].copy()    
    if len(radiology_reports) > 0:
        radiology_reports.loc[:, "exam_type"] = radiology_reports["note_text"].str.split("  ").apply(lambda l: l[0]).str.replace(":", "", regex=False).str.strip()
        def extract_history(report_text):
            match = re.search(r'(?:CLINICAL HISTORY:|INDICATION \(as provided by referring clinician\):)\s*(.*?)\s*ADDITIONAL HISTORY:\s*(.*?)(?:\s*COMPARISON:|$)', report_text)
            if match:
                clinical_history = match.group(1).strip()
                additional_history = match.group(2).strip()
                return clinical_history, additional_history
            return None, None
        radiology_reports[['original_indication', 'radiologist_indication']] = radiology_reports['note_text'].apply(lambda x: pd.Series(extract_history(x)))
        radiology_reports = radiology_reports[
            (radiology_reports["exam_type"] != "") &
            (~radiology_reports["exam_type"].str.contains("\*")) &
            (~radiology_reports["radiologist_indication"].isna())
        ].drop_duplicates(subset=["deid_service_date"]).sort_values(by=["deid_service_date"], ascending=False)
    for j in range(len(radiology_reports)):
        radiology_report = radiology_reports.iloc[j]
        filtered_patient_notes = patient_notes[
            (patient_notes["deid_service_date"] < radiology_report["deid_service_date"]) & 
            (patient_notes["note_type"] != "Imaging")
        ].sort_values(by=["deid_service_date"], ascending=False).reset_index(drop=True)
        filtered_data_radiology_report.append(radiology_report.to_frame().T)
        filtered_data_radiology_report.append(filtered_patient_notes)
filtered_data_radiology_report = pd.concat(filtered_data_radiology_report).drop_duplicates(subset=["deid_note_key"])
n_filtered_radiology_reports = len(filtered_data_radiology_report[~filtered_data_radiology_report["exam_type"].isna()])
print("n_notes", len(filtered_data_radiology_report))
print("n_patients", filtered_data_radiology_report["patientdurablekey"].nunique())
print("n_radiology reports ", n_filtered_radiology_reports)
print('-'*20)
print("Clinical notes associated with a radiology report with an Additional History section of None or are written after the radiology report")
print("-"*20)
print("n_notes (excluded)", len(filtered_data_note_type) - len(filtered_data_radiology_report))
print("n_patients (excluded)", filtered_data_note_type["patientdurablekey"].nunique() - filtered_data_radiology_report["patientdurablekey"].nunique())
filtered_data_radiology_report.to_parquet(f"clinical_indication_dataset_shard{start_shard}.parquet")
