import axios from 'axios'

const BASE_URL = 'http://localhost:8000';

export const SearchEndpoints = {
    simple: 'simple',
    boosted: 'boosted',
    semantic: 'semantic',
    transcript: 'transcript'
};

export async function getPaginatedEpisodes(page, pageSize, query = '', sortOption = '', filters = {}, endpoint) {
    const response = await searchSolr(query, sortOption, filters, endpoint);
    const filteredEpisodes = response.docs;
  
    const startIndex = (page - 1) * pageSize
    const endIndex = startIndex + pageSize
  
    return {
      episodes: filteredEpisodes.slice(startIndex, endIndex),
      totalPages: Math.ceil(filteredEpisodes.length / pageSize),
      currentPage: page
    }
}

export async function searchSolr(query, sortOption = '', filters = {}, endpoint="simple") {
    try {
        const response = await axios.post(BASE_URL + '/' + endpoint, { query: query, filters: filters}, { params: { sort: sortOption } });
        return response.data;
    } catch (error) {
        console.error('Error querying Solr:', error);
        throw error;
    }
}

export async function getEpisode(id) {
    try {
        const response = await axios.get(BASE_URL + '/episode/' + id);
        return response.data;
    } catch (error) {
        console.error('Error querying Solr:', error);
        throw error;
    }
}