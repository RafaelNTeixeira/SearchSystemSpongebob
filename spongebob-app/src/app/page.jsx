'use client'

import { useEffect, useState } from 'react'
import { Input } from "@/components/ui/input"
import { EpisodeCard } from "@/components/EpisodeCard"
import { Logo } from "@/components/Logo"
import { mockSearchSolr } from "@/app/api/search"
import { mockEpisodes } from "@/app/data/episodes"

export default function SpongeBobSearch() {
  const [episodes, setEpisodes] = useState(mockEpisodes)

  const handleSearch = (query) => {
    try {
      const response = mockSearchSolr(query)
      setEpisodes(response)
    }
    catch (error) {
      console.error('Error querying Solr:', error)
    }
  }


  return (
    <div className="container mx-auto p-4">
      <Logo />
      <Input
        type="text"
        placeholder="Search episodes..."
        onChange={(e) => handleSearch(e.target.value)}
        className="mb-6"
      />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {episodes.map(episode => (
          <EpisodeCard key={episode.id} episode={episode} />
        ))}
      </div>
      {episodes.length === 0 && (
        <p className="text-center text-gray-500 mt-4">No episodes found.</p>
      )}
    </div>
  )
}

