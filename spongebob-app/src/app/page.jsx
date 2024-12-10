'use client';

import { useEffect, useState } from 'react';
import { SearchEndpoints, getPaginatedEpisodes } from '@/app/api/search';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { EpisodeCard } from "@/components/EpisodeCard";
import { Logo } from "@/components/Logo";

export default function SpongeBobSearch() {
  const [searchQuery, setSearchQuery] = useState('*');
  const [episodes, setEpisodes] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [sortOption, setSortOption] = useState('');
  const [seasonSize, setSeasonSize] = useState(1);
  const [seasonOption, setSeasonOption] = useState([]);
  const [searchEndpoint, setSearchEndpoint] = useState(SearchEndpoints.simple);
  const [filters, setFilters] = useState({
    season: [] 
  });


  const fetchEpisodes = async () => {
    setIsLoading(true);
    try {
      const data = await getPaginatedEpisodes(currentPage, 6, searchQuery, sortOption, filters, searchEndpoint);
      setEpisodes(data.episodes);
      setTotalPages(data.totalPages);
    } catch (error) {
      console.error('Error fetching episodes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  const handleSearchChange = (e) => {
    const value = e.target.value;
    const endpoint = SearchEndpoints[value];
    setSearchEndpoint(endpoint);
    setCurrentPage(1);
  }

  const handlePrevPage = () => {
    setCurrentPage((prev) => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setCurrentPage((prev) => Math.min(prev + 1, totalPages));
  };

  const handleSortChange = (e) => {
    setSortOption(e.target.value);
    setCurrentPage(1);
  };

  const handleSeasonOver = () => {
    setSeasonSize(seasons.length);
  };

  const handleSeasonOut = () => {
    setSeasonSize(1);
  };

  const handleSeasonChange = (e) => {
    const selected = Array.from(e.target.selectedOptions, (option) => option.value);
    setSeasonOption(selected);
    setFilters((prev) => ({ ...prev, season: selected }));
    setCurrentPage(1);
  };


  useEffect(() => {
    fetchEpisodes();
  }, [currentPage, searchQuery, searchEndpoint, sortOption, filters]);

  const seasons = [1, 2, 3, 4, 5]; // List of seasons to display

  return (
    <div className="container mx-auto p-4">
      <Logo />
      <section className="mb-10">
      <select
          title='Search Type'
          value={searchEndpoint}
          onChange={handleSearchChange}
          className="absolute top-44 left-40 p-2 border rounded-md"
        >
          {Object.keys(SearchEndpoints).map((endpoint) => (
            <option key={endpoint} value={endpoint}>
              {endpoint}
            </option>
          ))}
        </select>
        <Input
          type="text"
          title='Search Episodes'
          placeholder="Search episodes..."
          value={searchQuery}
          onChange={handleSearch}
          className="mt-8 w-1/2 mx-auto"
        />
            <select
          title='Sort Episodes'
          value={sortOption}
          onChange={handleSortChange}
          className="absolute top-44 right-40 p-2 border rounded-md"
        >
          <option value="">Relevance</option>
          <option value="airdate desc">Most Recent Episodes</option>
          <option value="running_time desc">Longest Episodes</option>
        </select>
        <select
          title='Filter Seasons'
          value={seasonOption}
          multiple={true}
          size={seasonSize}
          onMouseOver={handleSeasonOver}
          onMouseOut={handleSeasonOut}
          onChange={handleSeasonChange}
          className="absolute top-44 right-14 z-10 p-1 border rounded-md"
        >
          {seasons.map((season) => (
            <option key={season} value={season} className={'p-1.5 rounded-md'}>
              Season {season}
            </option>
          ))}
        </select>
      </section>
      {isLoading ? (
        <p className="text-center">Loading...</p>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {episodes.map((episode) => (
              <EpisodeCard key={episode.id} episode={episode} />
            ))}
          </div>
          {episodes.length === 0 && (
            <p className="text-center text-gray-500 mt-4">No episodes found.</p>
          )}
          <div className="mt-6 flex justify-center items-center space-x-4">
            <Button onClick={handlePrevPage} disabled={currentPage === 1}>
              Previous
            </Button>
            <span>Page {currentPage} of {totalPages}</span>
            <Button onClick={handleNextPage} disabled={currentPage === totalPages}>
              Next
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
