import json
import requests
import urllib.parse
from pathlib import Path
import sys

current_file_path = Path(__file__)
data_dir_path = current_file_path.parent
queries_dir_path = Path(f"{data_dir_path}/queries")
output_dir_path = Path(f"{data_dir_path}/queriesResults")

output_dir_path.mkdir(parents=True,exist_ok=True)

REQUEST_BASE_URL = "http://localhost:8983/solr/episodes/select?"
DOCKER_CONTAINER_NAME = "spongebob_solr"
URI = "http://localhost:8983/solr"
COLLECTION = "episodes"

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

def fetch_solr_results(query_file, solr_uri, collection):
    """
    Fetch search results from a Solr instance based on the query parameters.

    Arguments:
    - query_file: Path to the JSON file containing Solr query parameters.
    - solr_uri: URI of the Solr instance (e.g., http://localhost:8983/solr).
    - collection: Solr collection name from which results will be fetched.

    Output:
    - Prints the JSON search results to STDOUT.
    """
    # Load the query parameters from the JSON file
    try:
        with open(query_file) as f:
            query_params = json.load(f)
    except FileNotFoundError:   
        print(f"Error: Query file {query_file} not found.")
        sys.exit(1)

    # Construct the Solr request URL
    uri = f"{solr_uri}/{collection}/select"

    try:
        # Send the POST request to Solr
        response = requests.post(uri, json=query_params)
        response.raise_for_status()  # Raise error if the request failed
    except requests.RequestException as e:
        print(f"Error querying Solr: {e}")
        sys.exit(1)

    result = response.json()

    docs = result.get("response", {}).get("docs", [])
    path = f"{output_dir_path}/{query_file.stem}.json"

    with open(path, 'w') as file:
        file.write(json.dumps(docs, indent=1))
        file.close()
    # # Fetch and print the results as JSON
    # results = response.json()
    # print(json.dumps(results, indent=2))

    # if "response" in results:
    #     print(json.dumps(results["response"], indent=2))
    # else:
    #     print("Error: 'response' key not found in Solr response.")
    #     sys.exit(1)

for file in queries_dir_path.iterdir():
    # query(file.stem)
    fetch_solr_results(file, URI, COLLECTION)
 