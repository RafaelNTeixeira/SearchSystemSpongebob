import pandas as pd
from pathlib import Path
from typing import Any
from wordcloud import WordCloud, STOPWORDS
import wordtree as WordTree
import spacy
import matplotlib.pyplot as plt
import numpy as np
import re


current_file_path = Path(__file__)
data_dir_path = current_file_path.parent.parent
clean_dir_path = Path(f"{data_dir_path}/clean")
clean_dir_path.mkdir(parents=True, exist_ok=True) # Where to output cleaned version of data
documents_output_dir_path = Path(f"{data_dir_path}/documents")
documents_output_dir_path.mkdir(parents=True, exist_ok=True) # Where to output artifacts like graphs

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

def extract_character_dialogues(df: pd.DataFrame, season: int, threshold_percentage=0.025):
    characters = df[df['season'] == season]['characters'].explode()
    dialogues = df[df['season'] == season]['transcript']


    character_dialogues = {}
    for character, dialogue in zip(characters, dialogues):
        if character in character_dialogues:
            character_dialogues[character] += len(re.findall(r'\w+:', dialogue))
            character_dialogues[character] += len(re.findall(rf'{re.escape(character.split()[0])}:', dialogue))

        else:
            character_dialogues[character] = len(re.findall(r'\w+:', dialogue))
            character_dialogues[character] += len(re.findall(rf'{re.escape(character.split()[0])}:', dialogue))
    

    # Remove characters with no dialogues
    character_dialogues = {k: v for k, v in character_dialogues.items() if v > 0}

    # If character has less than threshold_percentage of the total dialogues, group them as 'Others'
    total_dialogues = sum(character_dialogues.values())
    threshold = threshold_percentage * total_dialogues
    others = 0

    characters_to_delete = []
    for character, dialogues in character_dialogues.items():
        if dialogues < threshold:
            others += dialogues
            characters_to_delete.append(character)
    
    for character in characters_to_delete:
        del character_dialogues[character]

    if others > 0:
        character_dialogues['Others'] = others
              
    return character_dialogues

                
def draw_character_dialogues(character_dialogues, season: int):
    characters = list(character_dialogues.keys())
    dialogues = list(character_dialogues.values())

    plt.figure(figsize=(12, 6))
    plt.pie(dialogues, labels=characters, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title(f'Character Dialogues in Season {season}')
    plt.tight_layout(pad=2)
    plt.savefig(f'{documents_output_dir_path}/character_dialogues_season_{season}.png', format='png')
    plt.close()
    print(f"Character dialogues in Season {season} plotted")

def analyze_character_dialogues(df: pd.DataFrame):
    for season in df['season'].unique():
        character_dialogues = extract_character_dialogues(df, season)
        draw_character_dialogues(character_dialogues, season)

    print("Character dialogues analysis completed")

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

    analyze_character_dialogues(df)
    
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
    character_frequency_top_n.plot(kind='bar', color='pink', width=0.6)
    plt.xlabel('Characters')
    plt.ylabel('Frequency')
    plt.title(f'Top {top_n} Character Frequency Distribution')
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.tight_layout(pad=2)
    plt.savefig(f'{documents_output_dir_path}/character_frequency.png', format='png')
    plt.close()

    print("Top_n plot for character frequency generated")

def analyze_viewers_per_writer(df: pd.DataFrame):
    exploded_df = df.explode('writers')
    viewers_per_writer = exploded_df.groupby('writers')['us_viewers'].sum().reset_index()
    viewers_per_writer = viewers_per_writer.sort_values(by='us_viewers', ascending=False)

    plt.figure(figsize=(18, 8))
    plt.bar(viewers_per_writer['writers'], viewers_per_writer['us_viewers'], color='pink', width=0.6)
    plt.xlabel('Writers')
    plt.ylabel('Total US Viewers (in millions)')
    plt.title('Total US Viewers per Writer')
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.tight_layout(pad=2)
    plt.savefig(f'{documents_output_dir_path}/viewers_per_writer.png', format='png')
    plt.close()

    print("Bar plot for viewers per writer generated")

def analyze_viewers_per_animator(df: pd.DataFrame):
    exploded_df = df.explode('animation')
    viewers_per_animator = exploded_df.groupby('animation')['us_viewers'].sum().reset_index()

    viewers_per_animator = viewers_per_animator.sort_values(by='us_viewers', ascending=False)
    plt.figure(figsize=(18, 8))
    plt.bar(viewers_per_animator['animation'], viewers_per_animator['us_viewers'], color='pink', width=0.6)
    plt.xlabel('Writers')
    plt.ylabel('Total US Viewers (in millions)')
    plt.title('Total US Viewers per animator')
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.tight_layout(pad=2)
    plt.savefig(f'{documents_output_dir_path}/viewers_per_animator.png', format='png')
    plt.close()

    print("Bar plot for viewers per animator generated")

def seasons_viewing_analysis(df: pd.DataFrame): 

    season_views = df.groupby('season')['us_viewers'].sum().reset_index()

    plt.figure(figsize=(12, 6))
    plt.plot(season_views['season'], season_views['us_viewers'], marker='o', color='pink', linestyle='-')
    plt.xlabel('Season')
    plt.ylabel('Total US Viewers (in millions)')
    plt.title('Total US Viewers per Season')
    plt.xticks(season_views['season'], rotation=45)
    plt.grid()
    plt.tight_layout()
    plt.savefig(f'{documents_output_dir_path}/views_per_season.png', format='png')
    plt.close()

    print("Line graph for views per season generated")

def episode_ranking(df: pd.DataFrame, top_n=20): 
    ranked_episodes = df[['episode', 'us_viewers']].sort_values(by='us_viewers', ascending=False).head(top_n)

    plt.figure(figsize=(12, top_n * 0.4))  
    plt.barh(ranked_episodes['episode'].astype(str), ranked_episodes['us_viewers'], color='pink')
    plt.xlabel('Total US Viewers (in millions)')
    plt.title(f'Top {top_n} Episodes by Total US Viewers')
    plt.gca().invert_yaxis()  
    plt.tight_layout()
    plt.savefig(f"{documents_output_dir_path}/top_{top_n}_episode_ranking.png", format='png')
    plt.close()

    print("Episode ranking plot generated")
    
for f in Path(clean_dir_path).iterdir(): # Loops through raw directory
    output_character_freq_path = f"{documents_output_dir_path}/{f.stem[:-4]}_character_frequency_{f.suffix[1:]}.txt"
    if f.suffix[1:] == "json":
        file_type = "json"
        clean_df = pd.read_json(f)
    elif f.suffix[1:] == "csv":
        file_type = "csv"
        clean_df = pd.read_csv(f, sep=",")
    else:
        continue

    clean_df['airdate'] = pd.to_datetime(clean_df['airdate'], format="%Y-%m-%d")

    episode_ranking(clean_df, 20) # Change last number to adjust the number of episodes that appear in the plot
    seasons_viewing_analysis(clean_df)
    analyze_viewers_per_animator(clean_df)
    analyze_viewers_per_writer(clean_df)
    character_frequency(clean_df, output_character_freq_path, 50) # Change last number to adjust the number of characters that appear in the plot
    wordcloud(clean_df)
    data_analysis(clean_df)
    wordtree(clean_df, 'spongebob') # Insert keyword to make a wordtree
    analyze_character_dialogues(clean_df)
    draw_entities_season(clean_df, documents_output_dir_path)
    break

    