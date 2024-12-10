import requests
import json
import sys
from pathlib import Path
from semantic_search.query_embedding import text_to_embedding, solr_knn_query

# Load the entities from the JSON file
curr_dir = Path(__file__).parent.parent
entities_file = curr_dir / "docker" / "data" / "entities.json"
entities = json.load(open(entities_file, "rb"))

def query_solr(uri, query_json):
    print(f"Querying Solr at {uri} with query: {query_json}")
    try:
        response = requests.post(uri, json=query_json)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error querying Solr: {e}")
        sys.exit(1)

    results = response.json()

    if "response" in results:
        return results["response"]
    else:
        print("Error: 'response' key not found in Solr response.")
        sys.exit(1)

def query_simple(query_json, solr_uri="http://localhost:8983/solr", collection="episodes"):
    uri = f"{solr_uri}/{collection}/select"
    response = query_solr(uri, query_json)
    episodes = set()
    for doc in response["docs"]:
        episodes.add(doc["episode"])
    # print(f"Episodes found: {episodes}")
    return response


def build_transcript_query(query_json, entities=None):

    query_params = query_json["params"]
    entities_list: list = []
    words = query_params["q"].split()
    for word in words:
        if word in entities:
            entities_list.append(word)
    aux_string = "(" + " OR ".join(entities_list) + ")^4"
    query = ""
    for word in words:
        if word in entities:
            query += aux_string
        else:
            query += word
        query += " "
    query_params["q"] = query.strip()
    fields = query_json["fields"]
    params = {
        "indent": query_params["indent"],
        "fl": query_params["fl"],
        "start": query_params["start"],
        "q.op": query_params["q.op"],
        "sort": query_params["sort"],
        "rows": query_params["rows"],
        "lowercaseOperators": query_params["lowercaseOperators"],
        "q": query_params["q"],
        "defType": query_params["defType"],
        "qf": "speaker^5 actions^3 dialogue setting",
        "pf": "speaker^3 actions^5 dialogue setting",
        "ps": query_params["ps"],
        "wt": query_params["wt"],
        "df": "dialogue"
    }

    return {
        "fields": fields,
        "params": params,
    }

def query_transcript(query_json, solr_uri="http://localhost:8983/solr", entities=None):
    uri = f"{solr_uri}/transcript_processed/select"
    query_params = build_transcript_query(query_json, entities)
    response = query_solr(uri, query_params)
    episodes = set()
    for doc in response["docs"]:
        episodes.add(doc["episode"])
    # sorted_episodes = sorted(episodes)
    # print(f"Episodes founda: {sorted_episodes}")
    return response

def merge_results(normal_results, transcript_results):
    # normalize score
    normal_docs = normal_results["docs"]
    transcript_docs = transcript_results["docs"]
    normal_max_score = normal_results["maxScore"]
    transcript_max_score = transcript_results["maxScore"]
    normal_max_score = 1 if normal_max_score == 0 else normal_max_score
    transcript_max_score = 1 if transcript_max_score == 0 else transcript_max_score
    for doc in normal_docs:
        doc["score"] = doc["score"] / normal_max_score
    for doc in transcript_docs:
        doc["score"] = doc["score"] / transcript_max_score
    
    # merge results
    merged_docs = normal_docs + transcript_docs
    # stay with only the "episode" and score
    merged_docs = [{"episode": doc["episode"], "score": doc["score"]} for doc in merged_docs]
    # sum the scores of the same episode
    merged_dict = {}
    for doc in merged_docs:
        if doc["episode"] in merged_dict:
            merged_dict[doc["episode"]] += doc["score"]
        else:
            merged_dict[doc["episode"]] = doc["score"]
    # sort by score
    sorted_merged = sorted(merged_dict.items(), key=lambda x: x[1], reverse=True)

    # print (f"Episodes found: {[episode[0] for episode in sorted_merged]}")
    # print (f"Sorted size: {len(sorted_merged)}")

    return sorted_merged[:30]

def query_transcript_method(query_json, entities=None):
    normal_result= query_simple(query_json)
    transcript_result = query_transcript(query_json, entities=entities)
    sorted_result = merge_results(normal_result, transcript_result)
    query_json = {
    "fields": "episode, score",
    "params": {
        "indent": "true",
        "fl": "*",
        "start": "0",
        "q.op": "AND",
        "sort": "score desc",
        "rows": "30",
        "lowercaseOperators": "false",
        "defType": "edismax",
        "wt": "json",
        }
    }
    query_json["params"]["q"] = "episode:" + " OR episode:".join([str(episode[0]) for episode in sorted_result])
    uri = f"http://localhost:8983/solr/episodes/select"
    final_result = query_solr(uri, query_json)
    sorted_result_list = [episode[0] for episode in sorted_result]
    final_result["docs"] = sorted(final_result["docs"], key=lambda x: sorted_result_list.index((x["episode"])))
    return final_result

def query_simple_api(query:str ="", rows:int=0, sort:str="", fq:str=""):
    query_json = {
        "fields": "episode, score",
        "params": {
            "indent": "true",
            "fl": "*",
            "start": "0",
            "q.op": "AND",
            "sort": sort,
            "rows": rows,
            "lowercaseOperators": "false",
            "defType": "edismax",
            "wt": "json",
            "fq": fq,
            "q": query
        }
    }
    uri = f"http://localhost:8983/solr/schemaless_subset/select"
    return query_solr(uri, query_json)

def query_boosted_api(query:str ="", rows:int=0, sort:str="", fq:str=""):
    phrase_slop = len(query.split())//2
    query_json = {
    "fields": "episode, score",
    "params": {
        "indent": "true",
        "fl": "*",
        "start": "0",
        "q.op": "AND",
        "sort": sort,
        "rows": rows,
        "lowercaseOperators": "false",
        "q": query,
        "defType": "edismax",
        "qf": "transcript^3 title^5 synopsis",
        "pf": "transcript^3 title^5 synopsis",
        "ps": phrase_slop,
        "wt": "json",
        "df": "transcript",
        "fq": fq
        }
    }
    uri = f"http://localhost:8983/solr/episodes/select"
    return query_solr(uri, query_json)

def query_semantic_api(query:str= "", rows:int=10, sort:str="score desc", fq:str=""):
    phrase_slop = len(query.split())//2
    query_json = {
    "fields": "episode, score",
    "params": {
        "indent": "true",
        "fl": "*",
        "start": "0",
        "q.op": "AND",
        "sort": sort,
        "rows": rows,
        "lowercaseOperators": "false",
        "q": query,
        "defType": "edismax",
        "qf": "transcript^3 title^5 synopsis",
        "pf": "transcript^3 title^5 synopsis",
        "ps": phrase_slop,
        "wt": "json",
        "df": "transcript",
        "fq": fq
        }
    }
    return query_transcript_method(query_json, entities)

def query_semantic_api(query:str= "", rows:int=10, sort:str="score desc", fq:str=""):
    embedding = text_to_embedding(query)
    kwargs = {
        "fq": fq,
        "sort": sort,
    }
    return solr_knn_query("http://localhost:8983/solr", "episodes", embedding, k=rows, rows=rows, **kwargs)["response"]

def query_transcript_api(query:str= "", rows:int=10, sort:str="score desc", fq:str=""):
    phrase_slop = len(query.split())//2
    query_json = {
    "fields": "episode, score",
    "params": {
        "indent": "true",
        "fl": "*",
        "start": "0",
        "q.op": "AND",
        "sort": sort,
        "rows": rows,
        "lowercaseOperators": "false",
        "q": query,
        "defType": "edismax",
        "qf": "transcript^3 title^5 synopsis",
        "pf": "transcript^3 title^5 synopsis",
        "ps": phrase_slop,
        "wt": "json",
        "df": "transcript",
        "fq": fq
        }
    }
    return query_transcript_method(query_json, entities)
    

if __name__ == "__main__":
    # load query
    query_file = Path(__file__).parent.parent / "queries" / "q3.json"
    with open(query_file) as f:
        query_json = json.load(f)
    # query
    result = query_semantic_api("spongebob drive", 10, "score desc")
    print(len(result["docs"]))
    # result = query_new_method(query_json, entities)
    # print(json.dumps(result, indent=2))