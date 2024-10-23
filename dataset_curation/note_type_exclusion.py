import os
import pandas as pd
import tqdm
import regex as re


start_shard = 6
end_shard = 7

print("="*20)
print("UCSF Information Commons De-identified Clinical Notes Additional History Subset")
print("="*20)
parquet_files = []
for i in range(start_shard, end_shard):
    print(f"Shard {i}")
    print('-'*20)
    notes_shard_basepath = f"/mnt/sohn2022/UCSF_secure_data_info_commons_clinical_notes/additional_history/notes/shard{i}"
    for file in tqdm.tqdm(os.listdir(notes_shard_basepath)):
        if ".parquet" in file:
            parquet_files.append(pd.read_parquet(os.path.join(notes_shard_basepath, file)))
    
data = pd.concat(parquet_files)
print('-'*20)
print("n_notes", len(data))
print("n_patients", data["patientdurablekey"].nunique())

# Note Type Exclusion
# We remove all clinical notes that are telephone encounters of patient instructions or have a `note_type` of `None`. We also filter out notes that have < 20 words, regardless of type.

print("="*20)
print("Note Type Exclusion")
print("="*20)
filtered_data_note_type = data[
    ~(data["note_type"].isna()) & 
    ~(data["note_type"].isin(["Telephone Encounter", "Patient Instructions"])) & 
    ~(data["note_type"].isna()) &
    ~(data["note_text"].apply(lambda s: len(s.split()) < 20))
]
print("n_notes", len(filtered_data_note_type))
print("n_patients", filtered_data_note_type["patientdurablekey"].nunique())
print("-"*20)
print("Telephone notes, instructions to patients, and other notes with less than 20 words")
print("-"*20)
print("n_notes (excluded)", len(data) - len(filtered_data_note_type))
print("n_patients (excluded)", data["patientdurablekey"].nunique() - filtered_data_note_type["patientdurablekey"].nunique())

filtered_data_note_type.to_parquet(f"filtered_data_note_type_shard{start_shard}.parquet")


# # # Radiology Report without Redaction of Original Indication and Revised Indication

# # print("="*20)
# # print("Clinical Indication Dataset without Redaction")
# # print("="*20)
# # patient_mrns = filtered_data_radiology_report["patientdurablekey"].unique()
# # filtered_data_report_redactions = []
# # for i in tqdm.tqdm(range(len(patient_mrns))):
# #     patient_mrn = patient_mrns[i]
# #     patient_notes = filtered_data_radiology_report[filtered_data_radiology_report["patientdurablekey"] == patient_mrn]
# #     radiology_reports = patient_notes[
# #         (~patient_notes["exam_type"].isna()) & 
# #         (~patient_notes["original_indication"].astype(str).str.contains("\*")) &
# #         (~patient_notes["radiologist_indication"].astype(str).str.contains("\*"))
# #     ].copy()    
# #     for j in range(len(radiology_reports)):
# #         radiology_report = radiology_reports.iloc[j]
# #         filtered_patient_notes = patient_notes[
# #             (patient_notes["deid_service_date"] < radiology_report["deid_service_date"]) & 
# #             (patient_notes["note_type"] != "Imaging")
# #         ].sort_values(by=["deid_service_date"], ascending=False).reset_index(drop=True)
# #         filtered_data_report_redactions.append(radiology_report.to_frame().T)
# #         filtered_data_report_redactions.append(filtered_patient_notes)
# # filtered_data_report_redactions = pd.concat(filtered_data_report_redactions).drop_duplicates(subset=["deid_note_key"])
# # n_radiology_report_redactions = len(filtered_data_report_redactions[~filtered_data_report_redactions["exam_type"].isna()])
# # print("n_notes", len(filtered_data_report_redactions))
# # print("n_patients", filtered_data_report_redactions["patientdurablekey"].nunique())
# # print("n_radiology reports ", n_radiology_report_redactions)
# # print("-"*20)
# # print("Clinical notes associated with a radiology report that has indications with redactions")
# # print("-"*20)
# # print("n_notes (excluded)", len(filtered_data_radiology_report) - len(filtered_data_report_redactions))
# # print("n_patients (excluded)", filtered_data_radiology_report["patientdurablekey"].nunique() - filtered_data_report_redactions["patientdurablekey"].nunique())
# # print("n_radiology reports (excluded)", n_filtered_radiology_reports - n_radiology_report_redactions)
# # filtered_data_report_redactions.to_parquet("clinical_indication_dataset_without_redactions.parquet")

