import subprocess
python_path = "/home/bdrad/miniconda3/envs/radcliq/bin/python"
basepath = '/mnt/sohn2022/Adrian/GitHub/xai-vlm-indication-cxr/dataset_curation/radcliq'
datasets = [
	"mimic_cxr_indication", 
    "mimic_cxr_no_indication", 
	"chexpert_plus_indication", 
	"chexpert_plus_no_indication"
]
for dataset in datasets:
    subprocess.run([
        python_path, '/mnt/sohn2022/Adrian/GitHub/CXR-Report-Metric/evaluate.py',
        f'--gt_reports={basepath}/{dataset}_test_refs.csv',
        f'--predicted_reports={basepath}/{dataset}_test_result.csv',
        f'--out_file={basepath}/{dataset}_radcliq.csv',
        '--use_idf', 'False'
    ])