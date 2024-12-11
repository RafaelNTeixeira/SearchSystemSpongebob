import requests
from sentence_transformers import SentenceTransformer
from pathlib import Path

model = SentenceTransformer("spongebob_model") 

def text_to_embedding(text):
    # Load the SentenceTransformer model from the joblib file
    embedding = model.encode(text, convert_to_tensor=False).tolist()
    
    # Convert the embedding to the expected format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"
    return embedding_str

def solr_knn_query(endpoint, collection, embedding, k=10, rows=10, **kwargs):
    url = f"{endpoint}/{collection}/select"

    data = {
        "q": f"{{!knn f=vector topK={k}}}{embedding}",
        "fl": "*",
        "rows": rows,
        "wt": "json"
    }
    data.update(kwargs)
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()

def display_results(results):
    docs = results.get("response", {}).get("docs", [])
    if not docs:
        print("No results found.")
        return

    for doc in docs:
        print(f"* {doc.get('episode')} {doc} [score: {doc.get('score'):.2f}]")

def main():
    solr_endpoint = "http://localhost:8983/solr"
    collection = "episodes"
    
    query_text = input("Enter your query: ")
    embedding = text_to_embedding(query_text)

    try:
        results = solr_knn_query(solr_endpoint, collection, embedding)
        display_results(results)
    except requests.HTTPError as e:
        print(f"Error {e.response.status_code}: {e.response.text}")

if __name__ == "__main__":
    main()