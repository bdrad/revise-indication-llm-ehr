import os
import pandas as pd
import tqdm

# parquet_files = []
# for i in range(1, 7):
# 	print('='*20)
# 	print(f"Shard {i}")
# 	notes_shard_basepath = f"/mnt/sohn2022/UCSF_secure_data_info_commons_clinical_notes/additional_history/notes/shard{i}"
# 	for file in tqdm.tqdm(os.listdir(notes_shard_basepath)):
# 		if ".parquet" in file:
# 			parquet_files.append(pd.read_parquet(os.path.join(notes_shard_basepath, file)))
# data = pd.concat(parquet_files)

data = pd.read_parquet("/mnt/sohn2022/UCSF_secure_data_info_commons_clinical_notes/additional_history/notes/shard1/additional_history_0.parquet")
data.columns