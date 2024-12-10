import axios from 'axios'

const SEARCH_URL = 'http://localhost:8000/search';
const GET_EPISODE_URL = 'http://localhost:8000/episode';

export async function getPaginatedEpisodes(page, pageSize, query = '', sortOption = '', filters = {}) {
    const response = await searchSolr(query, sortOption, filters);
    const filteredEpisodes = response.response.docs;
  
    const startIndex = (page - 1) * pageSize
    const endIndex = startIndex + pageSize
  
    return {
      episodes: filteredEpisodes.slice(startIndex, endIndex),
      totalPages: Math.ceil(filteredEpisodes.length / pageSize),
      currentPage: page
    }
  }

export async function searchSolr(query, sortOption = '', filters = {}) {
    try {
        console.log(filters); 
        const response = await axios.post(SEARCH_URL, { query: query, filters: filters}, { params: { sort: sortOption } });
        return response.data;
    } catch (error) {
        console.error('Error querying Solr:', error);
        throw error;
    }
}

export async function getEpisode(id) {
    try {
        const response = await axios.get(`${GET_EPISODE_URL}/${id}`);
        return response.data;
    } catch (error) {
        console.error('Error querying Solr:', error);
        throw error;
    }
}