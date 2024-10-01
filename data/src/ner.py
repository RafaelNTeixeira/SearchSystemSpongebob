import spacy
import pandas as pd
from pathlib import Path

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

def output_entities_episode(df : pd.DataFrame, output_path : Path):
    Path(output_path).touch(exist_ok=True)
    with open(output_path, "w") as f:
        for index, row in df.iterrows():
            row['transcript'] = str(row['transcript']) # Ensure 'transcript' is a string
            entities = extract_entities(row['transcript'])
            f.write(f"Episode {index + 1}:\n")
            for entity in entities:
                f.write(f"{entity[0]}: {entity[1]}\n")
            f.write("\n")
        f.close()

output_entities_episode(df, f"{documents_output_dir_path}/entities_episode.txt")
