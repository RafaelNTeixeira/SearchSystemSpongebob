
import pandas as pd
from pathlib import Path
from typing import Any

current_file_path = Path(__file__)
data_dir_path = current_file_path.parent.parent
clean_output_dir_path = Path(f"{data_dir_path}/clean")
clean_output_dir_path.mkdir(parents=True, exist_ok=True) # Where to output cleaned version of data
documents_output_dir_path = Path(f"{data_dir_path}/documents")
documents_output_dir_path.mkdir(parents=True, exist_ok=True) # Where to output artifacts like graphs
file_type = ""

def file_stats(src_df : pd.DataFrame, output_path : Path, extra : dict[str, Any] = dict()): 
    Path(output_path).touch(exist_ok=True)
    with open(output_path, "w") as f:
        for key, val in extra.items():
            f.write(f"{key}:{val}\n")
        f.write(f"Number of instances: {src_df.shape[0]}\n")
        f.write(f"Number of features: {src_df.shape[1]}\n")

        for col in src_df.columns:
            f.write(f"Attribute: '{col}' ({type(src_df[col][0])})\n")
            f.write(f"\tNumber of NaN values in '{col}': {src_df[col].isna().sum()}\n")
            f.write(f"\n")
        
        f.close()

def create_url_transcript(df : pd.DataFrame):
    df['url_transcript'] = df['url'] + "/transcript"

def remove_nan(df : pd.DataFrame):
    df.dropna(subset=['transcript', 'airdate'], inplace=True)

def fill_nan_values(df : pd.DataFrame, value : any):
    if type(value) == type([]):
        for col in ['animation', 'writers', 'characters', 'musics']:
            df[col] = df.apply(lambda x : value if type(pd.NA) == type(x[col]) else x[col], axis=1)
    else:
        df.fillna({'animation':value, 'writers':value, 'characters':value, 'musics':value}, inplace=True)

def clean_airdate(df : pd.DataFrame):
    df['airdate'] = pd.to_datetime(df['airdate'], format="%d %m %Y")

def clean_viewers(df : pd.DataFrame):
    def choose_viewers(row : pd.Series):
        string = row['us_viewers']
        if (len(string) <= 4):
            if string[0].isnumeric():
                return string
            return "0.0"
        tokens = string.split('|')
        for i in range(len(tokens)-1):
            if tokens[i][0].isnumeric() and tokens[i+1][0].isnumeric():
                return tokens[i]
        return "0.0"
    df['us_viewers'] = df['us_viewers'].fillna("0.0")
    df['us_viewers'] = df.apply(choose_viewers, axis=1)
    df['us_viewers'] = pd.to_numeric(df['us_viewers'])

def clean_running_time(df : pd.DataFrame):
    def create_timedelta(string: str):
        minutes = 0
        seconds = 0
        parts = string.split(',')
    
        for part in parts:
            part = part.strip() 
            if 'minute' in part:
                minutes = int(part.split(' ')[0])
            elif 'second' in part:
                seconds = int(part.split(' ')[0])
    
        return pd.Timedelta(minutes=minutes, seconds=seconds)
    
    def choose_running_time(row : pd.Series):
        string = row['running_time']
        tokens = string.split('|')
        if len(tokens) != 1:
            for x in tokens:
                if "uncut" in x or "original" in x:
                    return create_timedelta(x)
        return create_timedelta(tokens[0]) 
    
    df['running_time'] = df.apply(choose_running_time, axis=1)
    df['running_time'] = df['running_time'].astype(str)
    df['running_time'] = df.apply(lambda x: x['running_time'].split()[2], axis=1)

def clean_animation(df : pd.DataFrame):
    if (type(df['animation'][0]) == type("")):
        df['animation'] = df.apply(lambda x: [a for a in x['animation'].split(',') if a.strip()[0] != '['], axis=1)
    elif (type(df['animation'][0]) == type([])):
        df['animation'] = df.apply(lambda x: [a for a in x['animation'] if a.strip()[0] != '['], axis=1)
    else :
        print("CHECK CLEAN_ANIMATION", type(df['animation'][0]))  
    
def clean_writers(df : pd.DataFrame):
    if (type(df['writers'][0]) == type("")):
        df['writers'] = df.apply(lambda x: [w for w in x['writers'].split(',') if w.strip()[0] != '['], axis=1)
    elif (type(df['writers'][0]) == type([])):
        df['writers'] = df.apply(lambda x: [w for w in x['writers'] if w.strip()[0] != '['], axis=1)
    else :
        print("CHECK CLEAN_WRITERS", type(df['writers'][0]))  

def clean_characters(df: pd.DataFrame):
    if (type(df['characters'][0]) == type("")):
        df['characters'] = df.apply(lambda x: [c for c in x['characters'].split(',') if c.strip()[0] != '['], axis=1)
    elif (type(df['characters'][0]) == type([])):
        df['characters'] = df.apply(lambda x: [c for c in x['characters'] if c.strip()[0] != '['], axis=1)
    else :
        print("CHECK CLEAN_CHARACTERS", type(df['characters'][0]))  

def clean_musics(df: pd.DataFrame):
    if (type(df['musics'][0]) == type("")):
        df['musics'] = df.apply(lambda x: [m for m in x['musics'].split(',') if m.strip()[0] != '[' and m.strip()[0:5] != "https"], axis=1)
    elif (type(df['musics'][0]) == type([])):
        df['musics'] = df.apply(lambda x: [m for m in x['musics'] if m.strip()[0] != '[' and m.strip()[0:5] != "https"], axis=1)
    else :
        print("CHECK CLEAN_MUSICS", type(df['musics'][0])) 

def clean_season(df: pd.DataFrame):
    df['season'] = pd.to_numeric(df['season'])

def clean_data(src_df : pd.DataFrame) -> pd.DataFrame:
    df = src_df.copy(True)
    remove_nan(df)
    if file_type == "json":
        fill_nan_values(df, ["Not disclosed"])
    else:
        fill_nan_values(df, "Not disclosed")

    clean_airdate(df)
    clean_viewers(df)
    clean_running_time(df)
    clean_animation(df)
    clean_writers(df)
    clean_characters(df)
    clean_musics(df)
    clean_season(df)

    df.drop_duplicates(subset=['episode'])
    create_url_transcript(df)

    return df
for f in Path(f"{data_dir_path}/raw").iterdir(): # Loops through raw directory
    output_raw_stats_path = f"{documents_output_dir_path}/{f.stem}_{f.suffix[1:]}_stats.txt"
    output_clean_stats_path = f"{documents_output_dir_path}/{f.stem[:-4]}_clean_{f.suffix[1:]}_stats.txt"
    output_clean_data_path = f"{clean_output_dir_path}/{f.stem[:-4]}_clean{f.suffix}"
    output_character_freq_path = f"{documents_output_dir_path}/{f.stem[:-4]}_character_frequency_{f.suffix[1:]}.txt"
    if f.suffix[1:] == "json":
        file_type = "json"
        raw_df = pd.read_json(f)
        raw_df.replace("", pd.NA, inplace=True)
        raw_df.replace([], pd.NA, inplace=True)
        raw_df['animation'] = raw_df['animation'].apply(lambda x: pd.NA if x == [] else x)
        raw_df['characters'] = raw_df['characters'].apply(lambda x: pd.NA if x == [] else x)
        raw_df['musics'] = raw_df['musics'].apply(lambda x: pd.NA if x == [] else x)
        raw_df['writers'] = raw_df['writers'].apply(lambda x: pd.NA if x == [] else x)
    elif f.suffix[1:] == "csv":
        file_type = "csv"
        raw_df = pd.read_csv(f, sep=",")
    else:
        continue



    file_stats(raw_df, output_raw_stats_path)
    clean_df = clean_data(raw_df)
    file_stats(clean_df, output_clean_stats_path)

    clean_df['airdate'] = clean_df['airdate'].astype(str)
    clean_df = clean_df.sort_values(['season', 'episode'])
    if f.suffix[1:] == "json":
        clean_df.to_json(output_clean_data_path, orient='records', force_ascii=False)
    elif f.suffix[1:] == "csv":
        clean_df.to_csv(output_clean_data_path, index=False)
    else:
        continue