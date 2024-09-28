import pandas as pd
from pathlib import Path
from typing import Any

current_file_path = Path(__file__)
data_dir_path = current_file_path.parent.parent
clean_output_dir_path = Path(f"{data_dir_path}/clean")
clean_output_dir_path.mkdir(parents=True, exist_ok=True) # Where to output cleaned version of data
documents_output_dir_path = Path(f"{data_dir_path}/documents")
documents_output_dir_path.mkdir(parents=True, exist_ok=True) # Where to output artifacts like graphs

def file_stats(src_df : pd.DataFrame, output_path : Path, extra : dict[str, Any] = dict()): 
    Path(output_path).touch(exist_ok=True)
    with open(output_path, "w") as f:
        for key, val in extra.items():
            f.write(f"{key}:{val}\n")
        f.write(f"Number of instances: {src_df.shape[0]}\n")
        f.write(f"Number of features: {src_df.shape[1]}\n")
        
        f.close()

for f in Path(f"{data_dir_path}/raw").iterdir(): # Loops through raw directory
    output_path = f"{documents_output_dir_path}/{f.stem}_{f.suffix[1:]}_stats.txt"
    if f.suffix[1:] == "json":
        raw_df = pd.read_json(f)
    elif f.suffix[1:] == "csv":
        raw_df = pd.read_csv(f, sep=",")
    else:
        continue

    print(raw_df.head())
    file_stats(raw_df, output_path)
    