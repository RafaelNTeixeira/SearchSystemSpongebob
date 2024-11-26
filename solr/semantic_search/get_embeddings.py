import sys
import json
import pysolr
from sentence_transformers import SentenceTransformer

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    # The model.encode() method already returns a list of floats
    return model.encode(text, convert_to_tensor=False).tolist()

if __name__ == "__main__":
    solr_url = "http://localhost:8983/solr/episodes"

    solr = pysolr.Solr(solr_url, always_commit=False)

    query = "*:*"
    documents = solr.search(query, rows=1000)

    updated_documents = []

    for document in documents:
        title = document.get("title", "")
        synopsis = document.get("synopsis", "")
        transcript = document.get("transcript", "")

        combined_text = title + " " + synopsis + " " + transcript
        document["vector"] = get_embedding(combined_text)

        updated_documents.append(document)

    solr.add(updated_documents)
    solr.commit()

    json.dump(updated_documents, sys.stdout, indent=4, ensure_ascii=False)
