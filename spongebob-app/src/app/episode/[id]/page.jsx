'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import Link from 'next/link'
import { useEffect, useState } from "react";
import { useParams } from "next/navigation"
import { getEpisode } from '@/app/api/search'


export default function EpisodePage() {
  const { id } = useParams();
  const [episode, setEpisode] = useState({});

  useEffect(() => {
    console.log('Episode ID:', id);
    getEpisode(id).then((data) => {
      console.log('Episode data:', data);
      setEpisode(data);
    });
  }, [id]); 

  return (
    <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6 text-center">SpongeBob Episode Search</h1>
        <Link href="/" className="text-blue-500 hover:underline mb-4 inline-block">&larr; Back to search</Link>
        <Card>
            <CardHeader>
            <CardTitle>{episode.title}</CardTitle>
            </CardHeader>
            <CardContent>
            <p>Season: {episode.season}</p>
            <p>Episode: {episode.episode}</p>
            <p className="mt-4">{episode.description}</p>
            </CardContent>
        </Card>
    </div>
  )
}

