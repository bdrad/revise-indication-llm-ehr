import pandas as pd
import ast
import regex as re
import tqdm
from sklearn.model_selection import train_test_split
import uuid

def extract_text(pattern, text):
    match = re.search(pattern, text)
    if match:
        result = match.group(1)
        return result.strip()
    return ''

CATEGORIES = [
    'Nursing/other',
    'Nursing',
    'Physician ',
    'Radiology'
]

DESCRIPTION_TO_EXAM_TYPE = {
    "Abdomen": "XR ABDOMEN",
    "PORTABLE ABDOMEN": "XR ABDOMEN",
    "ABDOMEN (SUPINE & ERECT) PORT": "XR ABDOMEN",
    "ABDOMEN (SUPINE & ERECT)": "XR ABDOMEN",
    "Chest": "XR CHEST",
    "CHEST (PORTABLE AP)": "XR CHEST",
    "CHEST (PA & LAT)": "XR CHEST",
    "CHEST PORT. LINE PLACEMENT": "XR CHEST",
    "CHEST (PRE-OP PA & LAT)": "XR CHEST",
    "P BABYGRAM (CHEST ONLY) PORT": "XR CHEST",
    "BABYGRAM (CHEST ONLY)": "XR CHEST",
    "CHEST (SINGLE VIEW)": "XR CHEST",
    
    "CT ABDOMEN W/CONTRAST": "CT ABDOMEN/PELVIS",
    "CT ABDOMEN W/O CONTRAST": "CT ABDOMEN/PELVIS",
    "CT ABD W&W/O C": "CT ABDOMEN/PELVIS",
    "CT PELVIS W/CONTRAST": "CT ABDOMEN/PELVIS",
    "CT PELVIS W/O CONTRAST": "CT ABDOMEN/PELVIS",
    "CT ABD & PELVIS WITH CONTRAST": "CT ABDOMEN/PELVIS",
    "CT ABD & PELVIS W/O CONTRAST": "CT ABDOMEN/PELVIS",
    
    "CT CHEST W/CONTRAST": "CT CHEST",
    "CT CHEST W/O CONTRAST": "CT CHEST",
    "CTA CHEST W&W/O C&RECONS, NON-CORONARY": "CT CHEST",
    
    "CT HEAD W/O CONTRAST": "CT HEAD",
    "CT HEAD W/ & W/O CONTRAST": "CT HEAD",
    "CTA HEAD W&W/O C & RECONS": "CT HEAD",
    
    "CT C-SPINE W/O CONTRAST": "CT SPINE",
    
    "MR HEAD W & W/O CONTRAST": "MRI HEAD",
    "MR HEAD W/O CONTRAST": "MRI HEAD",
    "MR HEAD W/ CONTRAST": "MRI HEAD",
    
    "MR CERVICAL SPINE W/O CONTRAST": "MRI SPINE",
    "MR CERVICAL SPINE": "MRI SPINE",
    "MR C-SPINE W& W/O CONTRAST": "MRI SPINE",
    "MR L-SPINE W & W/O CONTRAST": "MRI SPINE",
    "MR THORACIC SPINE W/O CONTRAST": "MRI SPINE",
    
    "ABDOMEN U.S. (COMPLETE STUDY)": "US ABDOMEN",
    "NEONATAL HEAD PORTABLE": "US HEAD",
    "RENAL U.S.": "US KIDNEY",
    "LIVER OR GALLBLADDER US (SINGLE ORGAN)": "US LIVER",
    "BILAT LOWER EXT VEINS": "US LOWER EXTREMITY"
}

data = pd.read_csv('/mnt/sohn2022/mimic-iii-clinical-database-1.4/NOTEEVENTS.csv.gz')
data = data.dropna(subset=['CHARTDATE', 'HADM_ID'])
data = data.sort_values(by=['HADM_ID', 'CHARTDATE'])
data = data[data['CATEGORY'].isin(CATEGORIES)]
print(data['CATEGORY'].value_counts())

hadm_ids = data['HADM_ID'].unique()

clinical_notes_indication = pd.DataFrame(columns=[
    'SUBJECT_ID',
    'HADM_ID',
    'REPORT_ID',
    'RADIOLOGY_REPORT_TEXT',
    'RADIOLOGY_REPORT_DESCRIPTION',
    'REPORT_TYPE',
    'RADIOLOGY_REPORT_INDICATION',
    'NOTE_CATEGORIES',
    'NOTE_TEXTS'
])

for hadm_id in tqdm.tqdm(hadm_ids[:1000]):
    radiology_reports = data.loc[data['HADM_ID'] == hadm_id].loc[data['CATEGORY'] == 'Radiology']
    for i in range(len(radiology_reports)):
        radiology_row = radiology_reports.iloc[i]
        previous_notes = data[
            (data['HADM_ID'] == hadm_id) &\
            (data['CHARTTIME'] < radiology_row['CHARTTIME'])
            # (data['CATEGORY'] != 'Radiology')
        ]
        radiology_report_text = radiology_row['TEXT']
        radiology_report_description = radiology_row['DESCRIPTION']
        report_text = " ".join(radiology_reports.iloc[i]['TEXT'].split('FINAL REPORT')[-1].split())
        indication_pattern = r'(HISTORY|INDICATION|CLINICAL HISTORY|CLINICAL INDICATION):\s*([\s\S]*?)(?=[A-Z\s]+:)'
        indication_match = re.search(indication_pattern, report_text, re.IGNORECASE)
        indication = indication_match.group(2) if indication_match else ""

        note_categories, note_texts = [], []
        for j in range(len(previous_notes)):
            note_categories.append(previous_notes.iloc[j]['CATEGORY'])
            note_texts.append(previous_notes.iloc[j]['TEXT'])
        if note_texts:
            report_type = DESCRIPTION_TO_EXAM_TYPE.get(radiology_report_description, "DEFAULT")
            clinical_notes_indication.loc[len(clinical_notes_indication)] = {
                'SUBJECT_ID': radiology_row['SUBJECT_ID'],
                'HADM_ID': radiology_row['HADM_ID'],
                'REPORT_ID': str(uuid.uuid4()),
                'RADIOLOGY_REPORT_TEXT': radiology_report_text,
                'RADIOLOGY_REPORT_DESCRIPTION': radiology_report_description,
                'REPORT_TYPE': report_type,
                'RADIOLOGY_REPORT_INDICATION': indication,
                'NOTE_CATEGORIES': note_categories,
                'NOTE_TEXTS': note_texts
            }

unique_subject_ids = clinical_notes_indication['SUBJECT_ID'].unique()
subject_ids_train, subject_ids_val_test = train_test_split(unique_subject_ids, test_size=0.1, random_state=42)
subject_ids_val, subject_ids_val_test = train_test_split(subject_ids_val_test, test_size=0.5, random_state=42)
data['SPLIT'] = 'train' 
data.loc[data['SUBJECT_ID'].isin(subject_ids_val), 'Split'] = 'validation'
data.loc[data['SUBJECT_ID'].isin(subject_ids_val_test), 'Split'] = 'test'
clinical_notes_indication.to_csv('/mnt/sohn2022/Adrian/clinical-notes-indication-generation/data/indication_dataset/mimic_iii_indications.csv', index=False)