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