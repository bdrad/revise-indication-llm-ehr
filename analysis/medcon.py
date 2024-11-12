import subprocess
# python_path = "/home/bdrad/miniconda3/envs/radcliq/bin/python"
basepath = '/mnt/sohn2022/Adrian/llm-revise-indication-notes/analysis/llm_evaluation_scores'
datasets = [
	"mimic_cxr_indication", 
    "mimic_cxr_no_indication", 
	"chexpert_plus_indication", 
	"chexpert_plus_no_indication"
]
for dataset in datasets:
    subprocess.run([
        "python", '/mnt/sohn2022/Adrian/Utils/Evaluation/MEDCON/main.py',
        f'--csv_path={basepath}/{dataset}_medcon_temp.csv',
        f'--output_path={basepath}/{dataset}_medcon.csv',
    ])