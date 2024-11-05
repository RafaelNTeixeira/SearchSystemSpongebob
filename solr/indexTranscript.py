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

def create_core(core_name):
    create_command = [
        "docker", "exec", DOCKER_CONTAINER_NAME,
        "bin/solr", "create_core", "-c", core_name
    ]
    
    try:
        subprocess.run(create_command, check=True)
        print(f"Core '{core_name}' created successfully.")
    except subprocess.CalledProcessError as e:
        print("Error creating core:", e)

def check_core_exists(solr_url, core_name):
    # Check if the core is available in solr
    ping_url = f"{solr_url}{core_name}/admin/ping"
    try:
        response = requests.get(ping_url)
        if response.status_code == 200:
            print(f"Core '{core_name}' exists. Proceeding with indexing.")
            return True
        else:
            print(f"Core '{core_name}' does not exist. Creating it now...")
            create_core(core_name)
            return check_core_exists(solr_url, core_name)
    except requests.RequestException as e:
        print("Error checking for core:", e)
        return False

def add_fields_to_schema(solr_url, core_name):
    fields = [
        {"name": "setting", "type": "string", "indexed": True, "stored": False},
        {"name": "speaker", "type": "string", "indexed": True, "stored": False},
        {"name": "dialogue", "type": "text_general", "indexed": True, "stored": False},
        {"name": "actions", "type": "text_general", "indexed": True, "stored": False},
    ]
    
    for field in fields:
        response = requests.post( 
            f"{solr_url}{core_name}/schema/fields",
            headers={'Content-Type': 'application/json'},
            json={"add-field": field}
        )
        if response.status_code == 200:
            print(f"Field '{field['name']}' added successfully.")
        else:
            print(f"Error adding field '{field['name']}':", response.text)

def parse_and_index_transcripts(json_file_path, solr_url, core_name):
    if not check_core_exists(solr_url, core_name):
        return
    
    add_fields_to_schema(solr_url, core_name)
    
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    documents = []
    
    for episode in data:
        transcript = episode.get("transcript", "")
        
        if transcript:
            parsed_transcript = parse_transcript(transcript)
            doc = {
                "id": episode.get("url", ""), # Using transcript URL
                "transcript": parsed_transcript
            }
            documents.append(doc)
    
    response = requests.post(
        f"{solr_url}{core_name}/update?commit=true",
        headers={'Content-Type': 'application/json'},
        json=documents)
    
    if response.status_code == 200:
        print("Data indexed successfully")
    else:
        print("Error indexing data:", response.text)

    # print(json.dumps(documents, indent=2)) # Print documents for verification

parse_and_index_transcripts(JSON_FILE_PATH, SOLR_URL, CORE_NAME)
