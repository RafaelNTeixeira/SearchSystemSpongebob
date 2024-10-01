import spacy
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

# Load dataset (assuming it's a CSV file with a 'text' column)
current_file_path = Path(__file__)
data_dir_path = current_file_path.parent.parent
raw_output_dir_path = Path(f"{data_dir_path}/raw")
documents_output_dir_path = Path(f"{data_dir_path}/documents")
documents_output_dir_path.mkdir(parents=True, exist_ok=True) # Where to output artifacts like graphs

# Load dataset
df = pd.read_csv(f"{raw_output_dir_path}/output_raw.csv")

# Function to extract entities
def extract_entities(text):
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
def draw_entities_season(df : pd.DataFrame):
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
            plt.savefig(f"{documents_output_dir_path}/entities_season_{season}.png")

            plt.close()

draw_entities_season(df)