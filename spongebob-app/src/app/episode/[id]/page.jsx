'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import Link from 'next/link'
import { use, useEffect, useState } from "react";
import { useParams } from "next/navigation"
import { getEpisode } from '@/app/api/search'
import { Button } from "@/components/ui/button"
import { Logo } from "@/components/Logo"


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
      <Logo />
      <Link href="/" className="p-3 bg-slate-800 text-white rounded-lg">&larr; Back to search</Link>
        <Card className="mt-8">
            <CardHeader className="flex flex-row justify-between">
              <CardTitle className="text-2xl">{episode.title}</CardTitle>
              <div className="flex gap-2">
              <Link href={episode.url ? episode.url :  "#"}>
                <Button>View Episode</Button>
              </Link>
              <Link href={episode.url ? episode.url + '/transcript' :  "#"}>
                <Button>View Transcript</Button>
              </Link>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between">
                <p><span className="font-semibold">Season:</span> {episode.season}</p>
                <p><span className="font-semibold">Episode:</span> {episode.episode}</p>
              </div>
              <div className="flex justify-between">
                <p><span className="font-semibold">Air date:</span> {new Date(episode.airdate).toLocaleDateString()}</p>
                <p><span className="font-semibold">Total Viewers:</span> {episode.us_viewers} M</p>
              </div>
              <h2 className="text-xl font-bold mt-4">Synopsis</h2>
              <p className="mt-2 p-3 rounded-md outline bg-slate-100 text-black">{episode.synopsis}</p>
              <Transcript transcript={episode.transcript} />
            </CardContent>
        </Card>
    </div>
  )
}


const Transcript = ({ transcript }) => {

  return (
    <div className="mt-8">
      <h2 className="text-xl font-bold">Transcript</h2>
      <div className="mt-2 p-3 rounded-md outline bg-slate-100 text-black">
        <p className="whitespace-pre-wrap">{transcript && 
          transcript.replace(/\/\//g, '\n')}
        </p>
      </div>
    </div>
  )
}
