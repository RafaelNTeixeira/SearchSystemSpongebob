import pandas as pd
from pathlib import Path
from typing import Any
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

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

        for col in src_df.columns:
            f.write(f"Number of NaN values in '{col}': {src_df[col].isna().sum()}\n")
        
        f.close()

def create_url_transcript(df : pd.DataFrame):
    df['url_transcript'] = f"{df['url']}/transcript"

def remove_nan(df : pd.DataFrame):
    df.dropna(subset=['transcript', 'airdate'], inplace=True)

def fill_nan_values(df : pd.DataFrame, value : any):
    df.fillna({'animation':value, 'writers':value, 'characters':value, 'musics':value}, inplace=True)

def clean_data(src_df : pd.DataFrame) -> pd.DataFrame:
    df = src_df.copy(True)
    remove_nan(df)
    fill_nan_values(df, "Not disclosed")
    
    print(df[df.isna().any(axis=1)][['title','animation']])
    # Now there is a need to fix the us_viewers missing.
    # createUrlTranscript(df)
    return df

def wordcloud(df : pd.DataFrame):
    words = ''
    stopwords = set(STOPWORDS)
    
    for transcript in df['transcript']:
        transcript = str(transcript) 
        tokens = transcript.split()

        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()
     
        words += " ".join(tokens) + " "

    wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(words)
    
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)
    
    plt.savefig(f'{documents_output_dir_path}/wordcloud.png', format='png')
    plt.close()

for f in Path(f"{data_dir_path}/raw").iterdir(): # Loops through raw directory
    output_raw_stats_path = f"{documents_output_dir_path}/{f.stem}_{f.suffix[1:]}_stats.txt"
    output_clean_stats_path = f"{documents_output_dir_path}/{f.stem[:-4]}_clean_{f.suffix[1:]}_stats.txt"
    if f.suffix[1:] == "json":
        raw_df = pd.read_json(f)
    elif f.suffix[1:] == "csv":
        raw_df = pd.read_csv(f, sep=",")
    else:
        continue

    file_stats(raw_df, output_raw_stats_path)
    clean_df = clean_data(raw_df)
    file_stats(clean_df, output_clean_stats_path)
    wordcloud(clean_df)
    break

    