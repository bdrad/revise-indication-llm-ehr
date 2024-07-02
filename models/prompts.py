from typing import List

DEFAULT_PROMPT = (
    f"Write a clinical indication (a one-sentence summary less than 20 words describing the patient's medical condition with gender, age, "
    "and any relevant surgical conditions."
)    

CLINICAL_INFORMATION = {
    "XR ABDOMEN": 
        "You may optionally pay closer attention to, as appropriate, one or more of the following given the patient's past history of:\n"
        "- Abdominal pain\n"
        "- Bowel obstruction\n"
        "- Perforated viscus\n"
        "- Ascites\n"
        "- Foreign body\n",
    "XR CHEST": 
        "You may optionally pay closer attention to, as appropriate, one or more of the following given the patient's past history of:\n"
        "- Pneumonia\n"
        "- Lung cancer\n"
        "- Pleural effusion\n"
        "- Tuberculosis\n"
        "- Chronic obstructive pulmonary disease (COPD)\n"
        "- Heart failure\n"
        "- Line placement (e.g., central venous catheters, endotracheal tubes)\n",
    "CT ABDOMEN/PELVIS": 
        "Make sure to add the patient's past history of/consider ruling out of:\n"
        "- Appendicitis\n"
        "- Diverticulitis\n"
        "- Abdominal tumors\n"
        "- Kidney stones\n"
        "- Liver cirrhosis\n"
        "- Abdominal aortic aneurysm\n"
        "- Inflammatory bowel disease (IBD)\n",
    "CT CHEST": 
        "Make sure to add the patient's past history of/consider ruling out of:\n"
        "- Pulmonary embolism\n"
        "- Lung nodules\n"
        "- Chest trauma\n"
        "- Aortic dissection\n"
        "- Mediastinal masses\n"
        "- Interstitial lung disease\n"
        "- Pneumothorax\n",
    "CT HEAD": 
        "Make sure to add the patient's past history of/consider ruling out of:\n"
        "- Stroke\n"
        "- Intracranial hemorrhage\n"
        "- Brain metastases\n"
        "- Brain tumors\n"
        "- Traumatic brain injury\n"
        "- Hydrocephalus\n"
        "- Aneurysms\n",
    "CT SPINE": 
        "Make sure to add the patient's past history of/consider ruling out of:\n"
        "- Spinal fractures\n"
        "- Disc herniation\n"
        "- Spinal tumors\n"
        "- Spinal stenosis\n"
        "- Infection (e.g., osteomyelitis)\n"
        "- Spondylolisthesis\n"
        "- Degenerative disc disease\n",
    "MRI HEAD": 
        "Make sure to add the patient's past history of/consider ruling out of:\n"
        "- Stroke\n"
        "- Brain tumors\n"
        "- Multiple sclerosis\n"
        "- Brain infection (e.g., encephalitis)\n"
        "- Pituitary adenoma\n"
        "- Cerebral atrophy\n",
    "MRI SPINE": 
        "Make sure to add the patient's past history of/consider ruling out of:\n"
        "- Spinal cord compression\n"
        "- Multiple sclerosis\n"
        "- Spinal tumors\n"
        "- Disc herniation\n"
        "- Spinal cord injury\n"
        "- Syringomyelia\n",
    "US ABDOMEN": 
        "Consider the patient's past history of/consider ruling out of:\n"
        "- Gallstones\n"
        "- Liver disease\n"
        "- Pancreatitis\n"
        "- Abdominal aortic aneurysm\n"
        "- Kidney disease\n",
    "US HEAD": 
        "Make sure to add the patient's past history of/consider ruling out of:\n"
        "- Head trauma\n"
        "- Hydrocephalus\n"
        "- Intracranial hemorrhage\n"
        "- Brain tumors\n"
        "- Craniosynostosis\n"
        "- Brain cysts\n",
    "US KIDNEY": 
        "Make sure to add the patient's past history of/consider ruling out of:\n"
        "- Kidney stones\n"
        "- Hydronephrosis\n"
        "- Kidney cysts\n"
        "- Kidney tumors\n"
        "- Pyelonephritis\n",
    "US LIVER": 
        "Make sure to add the patient's past history of/consider ruling out of:\n"
        "- Liver cirrhosis\n"
        "- Liver tumors\n"
        "- Hepatitis\n"
        "- Fatty liver disease\n"
        "- Liver abscess\n",
    "US LOWER EXTREMITY": 
        "Make sure to add the patient's past history of/consider ruling out of:\n"
        "- Deep vein thrombosis (DVT)\n"
        "- Varicose veins\n"
        "- Peripheral artery disease\n"
        "- Lymphedema\n"
        "- Venous insufficiency\n",
    "DEFAULT": 
        ""
}

def notes_to_prompt(notes: List[str]) -> str:
    return '\n\n'.join([f"{note[:2000]}" for note in notes[:10]])

def generate_prompt(
    clinical_notes: List[str], 
    exam_type: str,
    clinical_information: bool = True,
    generate_confidence: bool = True,
    generate_reasoning: bool = True,
    generate_evidence: bool = True) -> str:
    prompt = DEFAULT_PROMPT
    if clinical_information:
        prompt += "\n" + CLINICAL_INFORMATION[exam_type]
    
    notes_str = "\nNotes:\n" + notes_to_prompt(clinical_notes)
    prompt += notes_str
    prompt += "\n\nFollow the following format.\n\n"
    prompt += "Indication:\n"
    if generate_confidence:
        prompt += "Confidence level (1-10):\n"
    if generate_reasoning:
        prompt += "Reasoning for the indication:\n"
    if generate_evidence:
        prompt += "Specific textual evidence from the clinical notes supporting the indication:\n"
    return prompt.strip()
