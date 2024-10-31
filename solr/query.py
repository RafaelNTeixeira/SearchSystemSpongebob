import json
import requests
import urllib.parse
from pathlib import Path


current_file_path = Path(__file__)
data_dir_path = current_file_path.parent
queries_dir_path = Path(f"{data_dir_path}/queries")
output_dir_path = Path(f"{data_dir_path}/queriesResults")

output_dir_path.mkdir(parents=True,exist_ok=True)

REQUEST_BASE_URL = "http://localhost:8983/solr/episodes/select?"
DOCKER_CONTAINER_NAME = "spongebob_solr"

def getRequestParameters(query_name:str) -> json:
    path = f"{queries_dir_path}/{query_name}.json"
    with open(path, 'r') as file:
        parameters = json.load(file)
        file.close()
    return parameters

def getRequest(parameters: json) -> str:
    query_string = urllib.parse.urlencode(parameters, quote_via=urllib.parse.quote)
    return REQUEST_BASE_URL + query_string

def query(query_name: str) -> None:
    path = f"{output_dir_path}/{query_name}.json"
    parameters = getRequestParameters(query_name)
    request = getRequest(parameters)

    result = requests.get(request).json()

    docs = result.get("response", {}).get("docs", [])

    with open(path, 'w') as file:
        file.write(json.dumps(docs, indent=1))
        file.close()


for file in queries_dir_path.iterdir():
    query(file.stem)
 