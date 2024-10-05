import pandas as pd
from pathlib import Path
from typing import Any
from wordcloud import WordCloud, STOPWORDS
import wordtree as WordTree
import spacy
import matplotlib.pyplot as plt

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
        df['musics'] = df.apply(lambda x: [m for m in x['musics'].split(',') if m.strip()[0] != '['], axis=1)
    elif (type(df['musics'][0]) == type([])):
        df['musics'] = df.apply(lambda x: [m for m in x['musics'] if m.strip()[0] != '['], axis=1)
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

    print("Wordcloud for transcripts generated")

    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud_synopsis)
    plt.axis("off")
    plt.tight_layout(pad = 0)

    plt.savefig(f'{documents_output_dir_path}/wordcloud_synopsis.png', format='png')
    plt.close()

    print("Wordcloud for synopses generated")

def wordtree(df : pd.DataFrame, keyword):
    documents_transcript = df['transcript'].tolist()
    documents_synopses = df['synopsis'].tolist()

    transcripts_g = WordTree.search_and_draw(corpus = documents_transcript, keyword = keyword, max_n = 5)
    synopses_g = WordTree.search_and_draw(corpus = documents_synopses, keyword = keyword, max_n = 5)

    output_path_transcripts = f'{documents_output_dir_path}/wordtree_transcripts_{keyword}'
    output_path_synopses = f'{documents_output_dir_path}/wordtree_synopses_{keyword}'

    transcripts_g.render(output_path_transcripts) 
    print(f"Transcripts WordTree for keyword '{keyword}' generated")
    synopses_g.render(output_path_synopses) 
    print(f"Synopses WordTree for keyword '{keyword}' generated")

# Load spaCy's English model
def load_spacy_model():
    nlp = spacy.load("en_core_web_sm")
    return nlp

# Function to extract entities
def extract_entities(text):
    nlp = load_spacy_model()
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

# Get entities from each episode
def get_entities_episode(df : pd.DataFrame):
    entities_list = []
    for _, row in df.iterrows():
        entities = extract_entities(str(row['transcript']))
        entities_list.append(entities)
    return entities_list

# Draw entities plot, grouping episodes by 'season'
def draw_entities_season(df : pd.DataFrame, output_path : Path):
    for season in df['season'].unique():
        entities_list = get_entities_episode(df[df['season'] == season])
        entities_df = pd.DataFrame([entity for entities in entities_list for entity in entities], columns=['Entity', 'Label'])
        if not entities_df.empty:
            entities_df['Frequency'] = entities_df.groupby('Entity')['Entity'].transform('count')
            entities_df.drop_duplicates(subset=['Label'], inplace=True)
            entities_df.plot(kind='bar', x='Entity', y='Frequency')
            plt.xlabel('Entities')
            plt.ylabel('Frequency')
            plt.title(f"Entities in Season {season}")
            plt.tight_layout(pad = 2)
            plt.savefig(f"{output_path}/entities_season_{season}.png")
            plt.close()
            print(f"Entities in Season {season} plotted")

# Generation of plots for data analysis
def data_analysis(df : pd.DataFrame):
    airdates = set(df['airdate'])

    # Retrieve years where episodes were aired
    year_dates = [airdate.year for airdate in airdates]

    # Create dictionaries to:
    episodes_year_dict = {year: 0 for year in set(year_dates)} # Count the number of episodes aired per year
    views_year_dict = {year: 0 for year in set(year_dates)} # Count the amount of views per year

    for airdate in df['airdate']:
        year = airdate.year
        episodes_year_dict[year] += 1 # Increment an episode since one episode as been aired on that year
        viewers = df[df['airdate'] == airdate]['us_viewers']

        if not viewers.empty:
            views_year_dict[year] += round(float(viewers.sum()), 2)    

    years = list(episodes_year_dict.keys())
    episode_count = list(episodes_year_dict.values())
    view_count = list(views_year_dict.values())

    # Generate histogram for the frequency of eps per year
    plt.figure(figsize=(10, 6))
    plt.bar(years, episode_count, color='skyblue')
    plt.xlabel('Year')
    plt.ylabel('Number of Episodes')
    plt.title('Number of Episodes per Year')
    plt.xticks(years, rotation=45) 
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
    plt.xticks(years, rotation=45) 
    plt.grid(axis='y')  
    plt.tight_layout()  
    plt.savefig(f'{documents_output_dir_path}/views_per_year.png', format='png')
    plt.close()
    
    # Generate Named Entity Recognition (NER) plots
    draw_entities_season(df, documents_output_dir_path)

def character_frequency(df: pd.DataFrame, output_path: Path, top_n=50):
    character_list = df['characters'].explode().str.strip().tolist()
    character_frequency = pd.Series(character_list).value_counts()

    with open(output_path, 'w') as f:
        for character, count in character_frequency.items():
            f.write(f"{character}: {count}\n")

    character_frequency_top_n = character_frequency.head(top_n)
    plt.figure(figsize=(14, 8))
    character_frequency_top_n.plot(kind='bar', color='skyblue', width=0.6)
    plt.xlabel('Characters')
    plt.ylabel('Frequency')
    plt.title(f'Top {top_n} Character Frequency Distribution')
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.tight_layout(pad=2)
    plt.savefig(f'{documents_output_dir_path}/character_frequency.png', format='png')
    plt.close()

    
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
    
    if f.suffix[1:] == "json":
        clean_df.to_json(output_clean_data_path, orient='records', date_format='iso', force_ascii=False)
    elif f.suffix[1:] == "csv":
        clean_df.to_csv(output_clean_data_path, index=False)
    else:
        continue

    character_frequency(clean_df, output_character_freq_path)
    wordcloud(clean_df)
    data_analysis(clean_df)
    wordtree(clean_df, 'spongebob') # Insert keyword to make a wordtree
    break

    