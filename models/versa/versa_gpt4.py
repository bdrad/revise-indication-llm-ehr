import os
import re
import json
import base64
import requests
import time
import urllib.parse
from dotenv import load_dotenv
import pandas as pd
import ast
import tqdm
# In[13]:


def generate_example(i):
     return '\nClinical History:\n'+ generate_summary(sample_data.iloc[i]) + '\nIndication:\n' + sample_histories[i]

def notes_to_prompt(notes):
    note_prompt = ''
    for i, note in enumerate(notes):
        note_prompt += f'\nNOTE {i+1}\n' + note[:1000] 
    return note_prompt
    
def generate_summary(row):
    note_prompt = ''
    notes = row['NOTE_TEXTS'][:10]
    for i, note in enumerate(notes):
        note_prompt += f'\nNOTE {i+1}\n' + note[:1000]   
    prompt = (
        "Summarize these clinical notes into one paragraph, noting patient age, gender, ethnicity.\n"+\
        "Also note relevant medical conditions, lab tests, procedures, and clinical history."+\
        "\nNotes:"+\
        note_prompt+\
        '\nSummary:\n'
    )  
    return chat(prompt)


# In[4]:


data = pd.read_csv('data/processed_notes.csv')
data['NOTE_TEXTS'] = data['NOTE_TEXTS'].apply(ast.literal_eval)


sample_data = data.drop_duplicates(subset=['SUBJECT_ID']).dropna(subset=['RADIOLOGY_REPORT_MEDICAL_CONDITION', 'RADIOLOGY_REPORT_REASON_FOR_EXAM'])
sample_data['RADIOLOGY_REPORT_INDICATION'] = sample_data['RADIOLOGY_REPORT_MEDICAL_CONDITION'] + " " + sample_data['RADIOLOGY_REPORT_REASON_FOR_EXAM']
sample_data = sample_data[sample_data['NOTE_TEXTS'].apply(len) >= 5].reset_index(drop=True)


sample_data = sample_data[sample_data['RADIOLOGY_REPORT_DESCRIPTION'].str.contains('CT HEAD')].reset_index(drop=True)


# In[10]:


# results = []
# for i in tqdm.tqdm(range(25)):
#     row = sample_data.iloc[i]
#     notes = notes_to_prompt(row['NOTE_TEXTS'][:15])
#     neurologic_conditions = chat("Identify the single most critical head-related medical condition. Example: brain tumor metastases\n" + notes)
#     print(neurologic_conditions)
#     clinical_notes_prompt = "Write a clinical indication (a one-sentence summary describing the patient's medical condition with gender, age, procedures done (s/p), diseases to rule out (r/o)) for a "+\
#     row['RADIOLOGY_REPORT_DESCRIPTION']+\
#     f"\nInclude the patient's pre-existing condition of {neurologic_conditions}\n"+\
#     '\nNotes:\n' + notes+ '\nIndication:\n'
#     generated_indication = chat(clinical_notes_prompt)
#     results.append({
#         'SUBJECT_ID': row['SUBJECT_ID'],
#         'HADM_ID': row['HADM_ID'],
#         'ORIGINAL_INDICATION': row['RADIOLOGY_REPORT_INDICATION'],
#         'GENERATED_INDICATION': generated_indication
#     })


# In[15]:


results = []
for i in tqdm.tqdm(range(50)):
    row = sample_data.iloc[i]
    notes = notes_to_prompt(row['NOTE_TEXTS'])
    clinical_notes_prompt = "Write a clinical indication (a one-sentence summary less than 20 words describing the patient's medical condition with gender, age, relevant surgical procedures done, and conditions to rule out for a "+\
    row['RADIOLOGY_REPORT_DESCRIPTION']+\
    "\nYou may OPTIONALLY consider history of/rule out of stroke, trauma, seizures, bleed, intraventricular hemorrhage (IVH), tumor mass, intracranial process, interval change AS APPROPRIATE.\n"+\
    '\nNotes:\n' + notes+ '\nIndication:\n'
    generated_indication = chat(clinical_notes_prompt)
    results.append({
        'SUBJECT_ID': row['SUBJECT_ID'],
        'HADM_ID': row['HADM_ID'],
        'ORIGINAL_INDICATION': row['RADIOLOGY_REPORT_INDICATION'],
        'GENERATED_INDICATION': generated_indication
    })


# In[20]:


get_ipython().system('pip install datasets')
import evaluate
rouge = evaluate.load('rouge')

results = pd.DataFrame(results)
results['ORIGINAL_INDICATION'] = results['ORIGINAL_INDICATION'].str.replace('No contraindications for IV contrast', '')
rouge_scores = rouge.compute(predictions=results['GENERATED_INDICATION'], references=results['ORIGINAL_INDICATION'])

print(rouge_scores)


# In[60]:


i = 0

print('ORIGINAL')
print(results.iloc[i]['ORIGINAL_INDICATION'])
print('GENERATED')
print(results.iloc[i]['GENERATED_INDICATION'])


# In[69]:


sample_data_results = pd.concat([results, sample_data[:25][['RADIOLOGY_REPORT_TEXT', 'RADIOLOGY_REPORT_DESCRIPTION']]], axis=1)
sample_data_results.to_csv('versa_clinical_indications.csv', index=False)


# In[52]:


for note in sample_data.iloc[i]['NOTE_TEXTS']:
    print(note)


# In[64]:


sample_data[:25][['RADIOLOGY_REPORT_TEXT', 'RADIOLOGY_REPORT_DESCRIPTION']]


# In[67]:





# In[ ]:


# risk factors in the past
# what treatments have they gotten
# different diseases 


# In[ ]:


# NEONATAL HEAD PORTABLE
# IVH or Intracranial anomaly
# PVL or periventricular leukomalacia
# IVH
# periventricular leukomalacia
# intracranial hemorrhage
# IVH
# Intracranial hemorrhage
# PVL or other abnormality
# intracranial hemorrhage 
# r/o pvl
# r/o IVH
# assess for ivh


# Bleeding in the brain
# Hydrocephalus
# periventricular leukomalacia --> brainmatter malforms --> hypoxic injury (US)
# 

# CT HEAD
# Assess for recent hemorrhage or infarction
# Assess for hemorrhage
# Subdural hematoma
# subdurals
# SDH
# infarct, hemorrhage
# subdural drain removal
# Acute intracranial processes
# Assess interval change from prior CT

# Bleeds
# Stroke, contrast, usually MRI
# Acute intracranial processes --> anything? --> Not that useful
# Fall/Trauma

# increase specificity/sensitivity 
# if everyone looks up notes --> time savings
# if no time to read notes --> specificity/sensitivity
# + generated history --> increase? specificty/sensitivyt decrease? time savings


# In[ ]:


# Plan

# RAG to select 5 notes for current generation

# Add to the prompt the type of study being ordered


# In[ ]:


# How long indications are (histogram) and statistics


# In[1492]:


radiology_reports = data[data['CATEGORY'].str.contains('Radiology')]


# In[1495]:


radiology_reports['DESCRIPTION'].value_counts()[:50]

