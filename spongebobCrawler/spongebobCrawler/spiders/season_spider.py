import scrapy


class SeasonSpiderSpider(scrapy.Spider):
    name = 'season_spider'
    allowed_domains = ['spongebob.fandom.com']
    start_urls = ['https://spongebob.fandom.com/wiki/List_of_episodes']

    def parse(self, response):
        season_count = 0
        # Extract episode title and follow the link to the episode page
        for i in range(5, 80, 5):  # i is odd
            season_count += 1
            
            print(f'------------------------------------')
            print(f'Season {season_count}:')

            for j in range(2, 120, 2):  # j is even
                episode_selector = f'#mw-content-text > div > div:nth-child(4) > table:nth-child({i}) > tbody > tr:nth-child({j}) > td:nth-child(3) > a'
                episode_title = response.css(f'{episode_selector}::text').get()
                episode_link = response.css(f'{episode_selector}::attr(href)').get()

                ### TESTING CODE - REMOVE LATER
                if episode_title is not None and episode_link is not None:
                    episode_link = response.urljoin(episode_link) # Convert relative URL to absolute URL
                    print(f'{episode_title}: {episode_link}')
                else: # No more episodes in the season
                    break
                ### TESTING CODE - REMOVE LATER

                # TODO: Extract episode information
                #if episode_title is not None and episode_link is not None:
                    #yield response.follow(episode_link, self.parse_episode)
                #else: # No more episodes in the season
                    #break
            
            print(f'------------------------------------')

    def parse_episode(self, response):
        # TODO: Extract episode information
        pass
