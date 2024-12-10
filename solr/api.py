from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import requests

app = FastAPI()

SOLR_URL = "http://localhost:8983/solr/episodes/select"

class Query(BaseModel):
    query: str
    filters: Optional[Dict[str, list]] = None  

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change this to specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.post("/search")
def search(query: Query, sort: Optional[str] = None):
    params = {
        'q': query.query,
        'defType': 'edismax',
        'rows': 100,
        'wt': 'json'
    }
    if sort: 
        params['sort'] = sort
    
    if query.filters:
        filter_queries = []
        for key, values in query.filters.items():
            if values: 
                string_values = [str(value) for value in values]
                filter_queries.append(f"{key}:({' OR '.join(string_values)})")

        if filter_queries:
            params['fq'] = " AND ".join(filter_queries)  

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