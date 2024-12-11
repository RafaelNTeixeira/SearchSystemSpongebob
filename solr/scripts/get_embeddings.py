import sys
import json
import pysolr
from sentence_transformers import SentenceTransformer, losses, InputExample
from torch.utils.data import DataLoader
from pathlib import Path

# Load the SentenceTransformer model
def load_training_examples(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
        return [InputExample(texts=example["texts"]) for example in data]
    
# training_file = "./semantic_search/spongebob_train_examples.json"
training_file = Path(__file__).parent / "semantic_search" / "spongebob_train_examples.json"

train_examples = load_training_examples(training_file)

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
model = SentenceTransformer('all-MiniLM-L6-v2')
train_loss = losses.MultipleNegativesRankingLoss(model)

model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=3)
model.save("spongebob_model")


def get_embedding(text):
    # The model.encode() method already returns a list of floats
    return model.encode(text, convert_to_tensor=False).tolist()

if __name__ == "__main__":
    model = SentenceTransformer("spongebob_model")
    
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
        context = "Analyze this considering it's in the SpongeBob universe: "
        combined_text_with_context = context + combined_text
        document["vector"] = get_embedding(combined_text_with_context)

        updated_documents.append(document)

    solr.add(updated_documents)
    solr.commit()

    # json.dump(updated_documents, sys.stdout, indent=4, ensure_ascii=False)
