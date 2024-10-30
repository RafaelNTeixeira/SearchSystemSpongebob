import json
import re
from pathlib import Path

current_file_path = Path(__file__)
data_dir_path = current_file_path.parent

SOLR_URL = "http://localhost:8983/solr/spongebob_solr/" # Dont know which place exactly to insert this in

JSON_FILE_PATH = f"{data_dir_path}/spongebob.json"

def parse_transcript(transcript):
    scene_pattern = r"\[(.*?)\]"
    dialogue_pattern = r"(\w+): (.*?)(?=\w+:|$)"
    
    scenes = re.findall(scene_pattern, transcript)
    dialogues = re.findall(dialogue_pattern, transcript)

    formatted_transcript = {}

    if scenes:
        first_scene = scenes[0].strip()
        
        formatted_transcript['setting'] = first_scene
        formatted_transcript['dialogues'] = []
        
        for speaker, dialogue in dialogues:
            cleaned_dialogue, actions = extract_dialogue_and_actions(dialogue)
            formatted_transcript['dialogues'].append({
                'speaker': speaker.strip(),
                'dialogue': cleaned_dialogue.strip(),
                'actions': actions
            })

    return formatted_transcript

def extract_dialogue_and_actions(dialogue):
    action_pattern = r'\[([^\]]*)\]'

    actions = re.findall(action_pattern, dialogue)
    
    cleaned_dialogue = re.sub(action_pattern, '', dialogue)
    
    cleaned_dialogue = cleaned_dialogue.strip()

    return cleaned_dialogue, actions

def parse_and_index_transcripts(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    documents = []
    
    for episode in data:
        transcript = episode.get("transcript", "")
        
        if transcript:
            parsed_transcript = parse_transcript(transcript)
            doc = {
                "id": episode.get("url", ""),  # Using URL
                "transcript": parsed_transcript
            }
            documents.append(doc)

    # Uncomment this section to enable indexing
    # headers = {"Content-Type": "application/json"}
    # solr_data = json.dumps(documents)
    
    # response = requests.post(SOLR_URL, headers=headers, data=solr_data)
    
    # if response.status_code == 200:
    #     print("Data indexed successfully")
    # else:
    #     print("Error indexing data:", response.text)

    print(json.dumps(documents[1], indent=2))  # Print documents for verification

parse_and_index_transcripts(JSON_FILE_PATH)
