import json
from nltk.corpus import wordnet as wn
import nltk
from pathlib import Path

# This custom dictionary revels itself as necessary because of the unique synonyms needed in the Spongebob Squartpants universe, where people drive boats instead of cars
def load_custom_dictionary(filename="custom_dictionary.json"):
    with open(filename, 'r') as file:
        custom_dict = json.load(file)
    return custom_dict

def load_episodes(file_path):
    with open(file_path, 'r') as file:
        episodes = json.load(file)
    return episodes

def extract_terms(episodes, fields):
    terms = set()
    for episode in episodes:
        for field in fields:
            if field in episode and isinstance(episode[field], str):
                words = episode[field].split()
                terms.update(word.lower().strip(".,!?:;") for word in words)
    return terms

def generate_synonyms(terms, custom_dict):
    synonyms = {term: custom_dict[term] for term in custom_dict}
    
    for term in terms:
        if term not in synonyms:  
            synonym_set = set()
            for synset in wn.synsets(term):
                for lemma in synset.lemmas():
                    synonym_set.add(lemma.name().replace('_', ' '))
            if synonym_set:
                synonyms[term] = list(synonym_set)
    
    return synonyms

def save_synonyms_to_file(synonyms, filename="synonyms.txt"):
    path = Path(__file__).parent
    path = Path(f"{path}/docker/data")
    path.mkdir(parents=True, exist_ok=True)
    path = Path(f"{path}/{filename}")
    with open(path, "w") as file:
        for word, syns in synonyms.items():
            file.write(f"{word}: {', '.join(syns)}\n")

file_path = "docker/data/study_subset.json"
episodes = load_episodes(file_path)

custom_dictionary = load_custom_dictionary()

fields_to_extract = ["title", "synopsis", "transcript"]
terms = extract_terms(episodes, fields_to_extract)

synonyms = generate_synonyms(terms, custom_dictionary)

save_synonyms_to_file(synonyms)


# generate stopwords
nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

with open("docker/data/stopwords.txt", "w") as file:
    for word in stop_words:
        file.write(f"{word}\n")