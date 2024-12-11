#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from query_api import query_semantic_api, query_simple, query_transcript_method

def fetch_solr_results(query_file, solr_uri, collection, query_type):
    try:
        with open(query_file) as f:
            query_params = json.load(f)
    except FileNotFoundError:   
        print(f"Error: Query file {query_file} not found.")
        sys.exit(1)
    
    if query_type == "simple":
        response = query_simple(query_params, solr_uri, collection)
    elif query_type == "semantic":
        query = query_params["params"]["q"]
        rows = query_params["params"]["rows"]
        if ("fq" in query_params["params"]):
            fq = query_params["params"]["fq"]
        else:
            fq = ""
        sort = query_params["params"]["sort"]
        response = query_semantic_api(query, rows, sort, fq)
    elif query_type == "transcript":
        response = query_transcript_method(query_params)
    else:
        print(f"Error: Invalid query type '{query_type}'.")
        sys.exit(1)
    
    if not response:
        print("Error: No response from Solr.")
        sys.exit(1)

    print(json.dumps(response, indent=2))


    # # Construct the Solr request URL
    # uri = f"{solr_uri}/{collection}/select"

    # try:
    #     # Send the POST request to Solr
    #     response = requests.post(uri, json=query_params)
    #     response.raise_for_status()  # Raise error if the request failed
    # except requests.RequestException as e:
    #     print(f"Error querying Solr: {e}")
    #     sys.exit(1)

    # Fetch and print the results as JSON
    # results = response.json()

    # if "response" in response:
    #     print(json.dumps(results["response"], indent=2))
    # else:
    #     print("Error: 'response' key not found in Solr response.")
    #     sys.exit(1)


if __name__ == "__main__":
    # Set up argument parsing for the command-line interface
    parser = argparse.ArgumentParser(
        description="Fetch search results from Solr and output them in JSON format."
    )

    # Add arguments for query file, Solr URI, and collection name
    parser.add_argument(
        "--query",
        type=Path,
        required=True,
        help="Path to the JSON file containing the Solr query parameters.",
    )
    parser.add_argument(
        "--uri",
        type=str,
        default="http://localhost:8983/solr",
        help="The URI of the Solr instance (default: http://localhost:8983/solr).",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="episodes",
        help="Name of the Solr collection to query (default: 'episodes').",
    )
    parser.add_argument(
        "--type",
        type=str,
        default="simple",
        help="Type of query to perform ['simple', 'semantic', 'transcript'] (default: 'simple').",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Call the function with parsed arguments
    fetch_solr_results(args.query, args.uri, args.collection, args.type)
