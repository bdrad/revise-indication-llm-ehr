# Define the arguments
MODEL="gpt3_5"
DATASET="mimic_iii"
MIMIC_III_CSV_FILE="/mnt/sohn2022/Adrian/clinical-notes-indication-generation/data/indication_dataset/mimic_iii_indications.csv"  
UCSF_IC_CSV_FILE="/path/to/ucsf_ic.csv"  
IMAGING_MODALITY="XR"     
CLINICAL_INFORMATION=True           

# Run the Python script with arguments
python -m evaluation.test \
  --model $MODEL \
  --dataset $DATASET \
  --mimic_iii_csv_file $MIMIC_III_CSV_FILE \
  --ucsf_ic_csv_file $UCSF_IC_CSV_FILE \
  --imaging_modality $IMAGING_MODALITY \
  --clinical_information 
