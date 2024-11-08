import json
from pathlib import Path
import requests
import urllib.parse
import pandas as pd

current_file_path = Path(__file__)
solr_dir_path = current_file_path.parent
input_dir_path = Path(f"{solr_dir_path}/test")
output_dir_path = Path(f"{solr_dir_path}/docker/data")

output_dir_path.mkdir(parents=True,exist_ok=True)

def getTitles(p:str) -> set: 
    res = set()
    with open(p, 'r') as file:
        for line in file:
            line = line.strip()
            res.add(line)
    return res

def query(file: str) -> None:
    path = f"{input_dir_path}/{file.name}"
    output_path = f"{output_dir_path}/{file.stem}.json"
    set_of_titles = getTitles(path)
    clean_df = pd.read_json(f"{output_dir_path}/spongebob.json")
    clean_df['running_time'] = clean_df['running_time'].astype(str)
    clean_df['running_time'] = clean_df.apply(lambda x: x['running_time'].split(" ")[1], axis=1)
    clean_df = clean_df[clean_df['title'].isin(set_of_titles)]
    clean_df.to_json(output_path, orient='records', force_ascii=False)
    
for file in input_dir_path.iterdir():
    data = query(file)
    
 