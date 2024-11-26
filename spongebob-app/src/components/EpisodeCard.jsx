import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import Link from 'next/link'

export function EpisodeCard({ episode }) {
    return (
      <Link href={`/episode/${episode.id}`}>
        <Card className="h-full transition-shadow hover:shadow-md">
          <CardHeader>
            <CardTitle>{episode.title}</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Season: {episode.season}</p>
            <p>Episode: {episode.episode}</p>
          </CardContent>
        </Card>
      </Link>
    )
  }