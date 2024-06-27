import pandas as pd
import ast
import regex as re
import tqdm
from sklearn.model_selection import train_test_split

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

data = pd.read_csv('/mnt/sohn2022/mimic-iii-clinical-database-1.4/NOTEEVENTS.csv.gz')
data = data.dropna(subset=['CHARTDATE', 'HADM_ID'])
data = data.sort_values(by=['HADM_ID', 'CHARTDATE'])
data = data[data['CATEGORY'].isin(CATEGORIES)]
print(data['CATEGORY'].value_counts())

hadm_ids = data['HADM_ID'].unique()

clinical_notes_indication = pd.DataFrame(columns=[
    'SUBJECT_ID',
    'HADM_ID',
    'RADIOLOGY_REPORT_TEXT',
    'RADIOLOGY_REPORT_DESCRIPTION',
    'RADIOLOGY_REPORT_MEDICAL_CONDITION',
    'RADIOLOGY_REPORT_REASON_FOR_EXAM',
    'NOTE_CATEGORIES',
    'NOTE_TEXTS'
])

for hadm_id in tqdm.tqdm(hadm_ids[:100]):
    radiology_reports = data.loc[data['HADM_ID'] == hadm_id].loc[data['CATEGORY'] == 'Radiology']
    for i in range(len(radiology_reports)):
        radiology_row = radiology_reports.iloc[i]
        previous_notes = data[
            (data['HADM_ID'] == hadm_id) &\
            (data['CHARTTIME'] < radiology_row['CHARTTIME']) &\
            (data['CATEGORY'] != 'Radiology')]
        radiology_report_text = radiology_row['TEXT']
        radiology_report_description = radiology_row['DESCRIPTION']
        medical_condition_pattern = r'MEDICAL CONDITION: *(.*?) *REASON FOR THIS EXAMINATION:'
        medical_condition = extract_text(medical_condition_pattern, ' '.join(radiology_report_text.split()))
        reason_for_exam_pattern = r'REASON FOR THIS EXAMINATION: *(.*?)\s*__'
        reason_for_exam = extract_text(reason_for_exam_pattern, ' '.join(radiology_report_text.split()))
        note_categories, note_texts = [], []
        for j in range(len(previous_notes)):
            note_categories.append(previous_notes.iloc[j]['CATEGORY'])
            note_texts.append(previous_notes.iloc[j]['TEXT'])
        if note_texts:
            clinical_notes_indication.loc[len(clinical_notes_indication)] = {
                'SUBJECT_ID': radiology_row['SUBJECT_ID'],
                'HADM_ID': radiology_row['HADM_ID'],
                'RADIOLOGY_REPORT_TEXT': radiology_report_text,
                'RADIOLOGY_REPORT_DESCRIPTION': radiology_report_description,
                'RADIOLOGY_REPORT_INDICATION': medical_condition + " " + reason_for_exam,
                'NOTE_CATEGORIES': note_categories,
                'NOTE_TEXTS': note_texts
            }

unique_subject_ids = clinical_notes_indication['SUBJECT_ID'].unique()
subject_ids_train, subject_ids_val_test = train_test_split(unique_subject_ids, test_size=0.1, random_state=42)
subject_ids_val, subject_ids_val_test = train_test_split(subject_ids_val_test, test_size=0.5, random_state=42)
data['SPLIT'] = 'train' 
data.loc[data['SUBJECT_ID'].isin(subject_ids_val), 'Split'] = 'validation'
data.loc[data['SUBJECT_ID'].isin(subject_ids_val_test), 'Split'] = 'test'
clinical_notes_indication.to_csv('data/mimic_iii_indications.csv', index=False)