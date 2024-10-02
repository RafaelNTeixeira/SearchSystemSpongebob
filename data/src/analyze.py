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

# Generate wordcloud for transcripts and synopses
def wordcloud(df : pd.DataFrame):
    transcript_words = ''
    synopsis_words = ''
    stopwords = set(STOPWORDS)

    # Get transcript tokens
    for transcript in df['transcript']:
        transcript = str(transcript) # Ensure that we are processing a string 
        transcript_tokens = transcript.split() # Split transcript into tokens

        # Convert tokens to lowercase to ensure consistent word frequency counting, as 'Word' and 'word' should be treated as the same token
        for i in range(len(transcript_tokens)):
            transcript_tokens[i] = transcript_tokens[i].lower()
     
        transcript_words += " ".join(transcript_tokens) + " "

    # Get synopsis tokens
    for synopsis in df['synopsis']:
        synopsis = str(synopsis) 
        synopsis_tokens = synopsis.split() 

        for i in range(len(synopsis_tokens)):
            synopsis_tokens[i] = synopsis_tokens[i].lower()
     
        synopsis_words += " ".join(synopsis_tokens) + " "


    wordcloud_transcripts = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(transcript_words)
    
    wordcloud_synopsis = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(synopsis_words)
    
    # Create plot
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud_transcripts)
    plt.axis("off")
    plt.tight_layout(pad = 0)

    # Save plot as png
    plt.savefig(f'{documents_output_dir_path}/wordcloud_transcripts.png', format='png')
    plt.close()

    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud_synopsis)
    plt.axis("off")
    plt.tight_layout(pad = 0)

    plt.savefig(f'{documents_output_dir_path}/wordcloud_synopsis.png', format='png')
    plt.close()

# Generation of plots for data analysis
def data_analysis(df : pd.DataFrame):
    airdates = set(df['airdate'])
    split_dates = [airdate.split(' ') for airdate in airdates]
    filtered_dates = [date for date in split_dates if len(date) == 3] # Get only the dates that are in the correct format (ignores "TBD")
    year_dates = [date[2] for date in filtered_dates]
    year_dict = {year: 0 for year in year_dates} # Get a dictionary only for the years that episodes were aired 

    # Count the frequency of each episode per year
    for airdate in df['airdate']:
        split_date = airdate.split(' ')
        if len(split_date) == 3:
            year = split_date[2]
            year_dict[year] += 1

    sorted_year_dict = dict(sorted(year_dict.items(), key=lambda x: int(x[0]))) # Sort by year (represented as the key of dict)

    years = list(sorted_year_dict.keys())
    episode_count = list(sorted_year_dict.values())

    plt.figure(figsize=(10, 6))
    plt.bar(years, episode_count, color='skyblue')
    plt.xlabel('Year')
    plt.ylabel('Number of Episodes')
    plt.title('Number of Episodes per Year')
    plt.xticks(rotation=45) 
    plt.grid(axis='y')  
    plt.tight_layout()  
    
    plt.savefig(f'{documents_output_dir_path}/frequency_episodes_per_year.png', format='png')
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
    data_analysis(clean_df)
    break

    