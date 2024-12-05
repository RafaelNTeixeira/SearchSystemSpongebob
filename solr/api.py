from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

SOLR_URL = "http://localhost:8983/solr/episodes/select"

class Query(BaseModel):
    query: str

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change this to specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.post("/search")
def search(query: Query):
    params = {
        'q': query.query,
        'defType': 'edismax',
        'rows': 30,
        'wt': 'json'
    }
    response = requests.get(SOLR_URL, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error querying SOLR")
    
    return response.json()

@app.get("/episode/{id}")
def get_episode(id: str):
    params = {
        'q': f'id:{id}',
        'wt': 'json'
    }
    response = requests.get(SOLR_URL, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error querying SOLR")
    
    results = response.json()
    if results['response']['numFound'] == 0:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    return results['response']['docs'][0]