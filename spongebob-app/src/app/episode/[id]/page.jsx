import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { mockEpisodes } from "@/app/data/episodes"
import Link from 'next/link'

export default function EpisodePage({ params }) {
  const episode = mockEpisodes.find(ep => ep.id === parseInt(params.id))

  if (!episode) {
    return <div>Episode not found</div>
  }

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

