import axios from 'axios'

const API_URL = 'http://localhost:8000/search';

export async function searchSolr(query) {
    try {
        const response = await axios.post(API_URL, { query: query });
        return response.data;
    } catch (error) {
        console.error('Error querying Solr:', error);
        throw error;
    }
}