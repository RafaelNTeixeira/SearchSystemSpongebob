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
            f.write(f"Attribute: '{col}' ({type(src_df[col][0])})")
            f.write(f"Number of NaN values in '{col}': {src_df[col].isna().sum()}\n")
        
        f.close()

def create_url_transcript(df : pd.DataFrame):
    df['url_transcript'] = f"{df['url']}/transcript"

def remove_nan(df : pd.DataFrame):
    df.dropna(subset=['transcript', 'airdate'], inplace=True)

def fill_nan_values(df : pd.DataFrame, value : any):
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

    df['us_viewers'] = df['us_viewers'].astype(str)
    df['us_viewers'] = df.apply(choose_viewers, axis=1)
    df['us_viewers'] = pd.to_numeric(df['us_viewers'])
    print(df['us_viewers'].unique())

def clean_data(src_df : pd.DataFrame) -> pd.DataFrame:
    df = src_df.copy(True)
    remove_nan(df)
    fill_nan_values(df, "Not disclosed")
    clean_airdate(df)
    clean_viewers(df)
    
    create_url_transcript(df)

    # print(df[['title', 'us_viewers']])
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

    # Retrieve years where episodes were aired
    split_dates = [airdate.split(' ') for airdate in airdates]
    filtered_dates = [date for date in split_dates if len(date) == 3] # Get only the dates that are in the correct format (ignores 'TBD')
    year_dates = [date[2] for date in filtered_dates]

    # Create dictionaries to:
    episodes_year_dict = {year: 0 for year in year_dates} # Count the number of episodes aired per year
    views_year_dict = {year: 0 for year in year_dates} # Count the amount of views per year

    for airdate in df['airdate']:
        split_date = airdate.split(' ')
        if len(split_date) == 3:
            year = split_date[2]
            episodes_year_dict[year] += 1 # Increment an episode since one episode as been aired on that year
            viewers = df[df['airdate'] == airdate]['us_viewers']

            if not viewers.empty:
                numeric_viewers = pd.to_numeric(viewers, errors='coerce') # Ignores fields filled with 'TBD'
                views_year_dict[year] += round(float(numeric_viewers.sum()), 2)

    sorted_episodes_year_dict = dict(sorted(episodes_year_dict.items(), key=lambda x: int(x[0]))) # Sort by year (represented as the key of dict)
    sorted_views_year_dict = dict(sorted(views_year_dict.items(), key=lambda x: int(x[0])))

    years = list(sorted_episodes_year_dict.keys())
    episode_count = list(sorted_episodes_year_dict.values())
    view_count = list(sorted_views_year_dict.values())

    # Generate histogram for the frequency of eps per year
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

    # Generate histogram for the ammount of views per year
    plt.figure(figsize=(10, 6))
    plt.bar(years, view_count, color='skyblue')
    plt.xlabel('Year')
    plt.ylabel('Ammount of Views (Millions)')
    plt.title('Ammount of Views per Year')
    plt.xticks(rotation=45) 
    plt.grid(axis='y')  
    plt.tight_layout()  
    plt.savefig(f'{documents_output_dir_path}/views_per_year.png', format='png')
    plt.close()
    

for f in Path(f"{data_dir_path}/raw").iterdir(): # Loops through raw directory
    output_raw_stats_path = f"{documents_output_dir_path}/{f.stem}_{f.suffix[1:]}_stats.txt"
    output_clean_stats_path = f"{documents_output_dir_path}/{f.stem[:-4]}_clean_{f.suffix[1:]}_stats.txt"
    output_clean_data_path = f"{clean_output_dir_path}/{f.stem[:-4]}_clean{f.suffix}"
    if f.suffix[1:] == "json":
        raw_df = pd.read_json(f)
    elif f.suffix[1:] == "csv":
        raw_df = pd.read_csv(f, sep=",")
    else:
        continue

    file_stats(raw_df, output_raw_stats_path)
    clean_df = clean_data(raw_df)
    file_stats(clean_df, output_clean_stats_path)
    
    if f.suffix[1:] == "json":
        clean_df.to_json(output_clean_data_path)
    elif f.suffix[1:] == "csv":
        clean_df.to_csv(output_clean_data_path, index=False)
    else:
        continue
    
    wordcloud(clean_df)
    data_analysis(clean_df)
    break

    