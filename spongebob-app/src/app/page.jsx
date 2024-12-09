'use client'

import { useEffect, useState } from 'react'
import { getPaginatedEpisodes } from '@/app/api/search'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { EpisodeCard } from "@/components/EpisodeCard"
import { Logo } from "@/components/Logo"

export default function SpongeBobSearch() {
  const [searchQuery, setSearchQuery] = useState('*')
  const [episodes, setEpisodes] = useState([]);
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [sortOption, setSortOption] = useState('') 

  const fetchEpisodes = async () => {
    setIsLoading(true)
    try {
      const data = await getPaginatedEpisodes(currentPage, 6, searchQuery, sortOption)
      setEpisodes(data.episodes)
      setTotalPages(data.totalPages)
    } catch (error) {
      console.error('Error fetching episodes:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (e) => {
    setSearchQuery(e.target.value)
    setCurrentPage(1)
  }

  const handlePrevPage = () => {
    setCurrentPage(prev => Math.max(prev - 1, 1))
  }

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages))
  }

  const handleSortChange = (e) => {
    setSortOption(e.target.value)
    setCurrentPage(1) 
  }

  useEffect(() => {
    fetchEpisodes()
  }, [currentPage, searchQuery, sortOption])

  return (
    <div className="container mx-auto p-4">
      <Logo />
      <div className="flex flex-wrap justify-between items-center mb-6">
        <Input
          type="text"
          placeholder="Search episodes..."
          value={searchQuery}
          onChange={handleSearch}
          className="w-full md:w-auto mb-4 md:mb-0"
        />
        <select
          value={sortOption}
          onChange={handleSortChange}
          className="p-2 border rounded-md"
        >
          <option value="">Relevance</option>
          <option value="airdate desc">Most Recent Episodes</option>
          <option value="running_time desc">Longest Episodes</option>
        </select>
      </div>
      {isLoading ? (
        <p className="text-center">Loading...</p>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {episodes.map(episode => (
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
  )
}
