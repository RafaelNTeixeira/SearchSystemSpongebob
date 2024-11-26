import { mockEpisodes } from "@/app/data/episodes"

const axios = require('axios');

const SOLR_URL = 'http://localhost:8983/solr/episodes/select';

export function mockSearchSolr(query) {
    return mockEpisodes.filter(episode => episode.title.toLowerCase().includes(query.toLowerCase()));
}


// TODO: Implement searchSolr function to query Solr
export async function searchSolr(query) {
    try {
        const response = await axios.get(SOLR_URL, {
            params: {
                q: query,
                wt: 'json'
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error querying Solr:', error);
        throw error;
    }
}