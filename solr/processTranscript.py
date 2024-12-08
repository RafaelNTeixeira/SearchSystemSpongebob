import json
import re
import requests
import subprocess
from pathlib import Path

current_file_path = Path(__file__)
data_dir_path = Path(f"{current_file_path.parent}/docker/data")


SOLR_URL = "http://localhost:8983/solr/"
DOCKER_CONTAINER_NAME = "spongebob_solr"
CORE_NAME = "episodes"

JSON_FILE_PATH = f"{data_dir_path}/spongebob.json"
JSON_OUTPUT_PATH = f"{data_dir_path}/processedTranscript.json"
ENTITIES_OUTPUT_PATH = f"{data_dir_path}/entities.json"


def parse_transcript(transcript, episode_id):
    formatted_transcript = []
    scene_index = 0
    quote_index = 1
    transcript_elements = transcript.split("//")
    while quote_index < len(transcript_elements):
        if (transcript_elements[quote_index][0] == "["):
            scene_index = quote_index
            quote_index += 1
            if quote_index >= len(transcript_elements):
                formatted_transcript.append(
                    {
                        'episode' : episode_id,
                        'setting' : transcript_elements[scene_index],
                        'dialogue' : "",
                        'actions' : "",
                        'speaker' : ""
                    })
                break
        

        quote = transcript_elements[quote_index]
        quote_parts = quote.split(":")
        if len(quote_parts) < 2:
            formatted_transcript.append(
                {
                    'episode' : episode_id,
                    'setting' : transcript_elements[scene_index],
                    'dialogue' : "",
                    'actions' : quote,
                    'speaker' : ""
                })
        else:
            speaker = quote.split(":")[0]
            dialogue, actions = extract_dialogue_and_actions(quote.split(":")[1])
            formatted_transcript.append(
                {
                    'episode' : episode_id,
                    'setting' : transcript_elements[scene_index],
                    'dialogue' : dialogue,
                    'actions' : actions,
                    'speaker' : speaker
                })
        quote_index = quote_index + 1
    
    return formatted_transcript

def extract_dialogue_and_actions(dialogue):
    action_pattern = r'\[([^\]]*)\]'
    actions = re.findall(action_pattern, dialogue)
    cleaned_dialogue = re.sub(action_pattern, '', dialogue)
    cleaned_dialogue = cleaned_dialogue.strip()
    cleaned_dialogue = cleaned_dialogue.replace("//", "")
    actions = [action.replace("//", "") for action in actions]
    # actions to string
    actions = " ".join(actions)

    return cleaned_dialogue, actions

def parse_and_index_transcripts(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    documents = []
    
    for episode in data:
        transcript = episode.get("transcript", "")
        episode_id = episode.get("episode", "")
        
        if transcript:
            parsed_transcript = parse_transcript(transcript, episode_id)
            
            documents.extend(parsed_transcript)
    
    # Entities extraction
    entities = set()
    for document in documents:
        entities.add((str(document['speaker'])).lower())

    entities = sorted(list(entities))

    with open(ENTITIES_OUTPUT_PATH, 'w') as file:
        json.dump(entities, file, indent=2)
    
    # print(json.dumps(documents, indent=2)) # Print documents for verification
    with open(JSON_OUTPUT_PATH, 'w') as file:
        json.dump(documents, file, indent=2)
    
    # Mean of documents per episode
    mean = len(documents) / len(data)
    print(f"Mean of documents per episode: {mean}")

parse_and_index_transcripts(JSON_FILE_PATH)