import scrapy

from spongebobCrawler.items import EpisodeItem

class SeasonSpiderSpider(scrapy.Spider):
    name = 'season_spider'
    allowed_domains = ['spongebob.fandom.com']
    start_urls = ['https://spongebob.fandom.com/wiki/List_of_episodes']
    info_selector = {
        "Title" : "//span[@class=\"mw-page-title-main\"]/text()",
        "General" : "//div[@data-source=\"title\"]//div/text()",
        "AirdateMonthDay" :"//div[@data-source=\"airdate\"]//a[@title=\"United States of America\"]/following-sibling::a[1]/text()", 
        "AirdateYear" :"//div[@data-source=\"airdate\"]//a[@title=\"United States of America\"]/following-sibling::a[1]/following-sibling::a[1]/text()", 
        "Writers":"//div[@data-source=\"writer\"]//a/text()",
        "Animation":"//div[@data-source=\"director-animation\"]//a/text()",
        "Characters":"//div[@role=\"navigation\"]/following-sibling::h3[1]/following-sibling::ul[1]//li",
        "Synopsis":"//div[@class=\"mw-parser-output\"]/p[count(preceding-sibling::h2)=1]",
        "Musics":"//div[@class=\"mw-parser-output\"]/p[count(preceding-sibling::h3/span[@id=\"Music\"])=1]/a/text()"

    } 

    month_dic = {
        "January" : "1",
        "February" : "2",
        "March" : "3", 
        "April" : "4",
        "May" : "5",
        "June" : "6",
        "July" : "7",
        "August" : "8",
        "September" : "9",
        "October" : "10",
        "November" : "11",
        "December" : "12"
    }

    def parse(self, response):
        season_count = 0
        # Extract episode title and follow the link to the episode page
        for i in range(5, 80, 5):  # i is odd
            season_count += 1
            
            print(f'\n---------------------------------------------\n')
            print(f'Season {season_count}:\n')

            for j in range(2, 120, 2):  # j is even
                episode_selector = f'#mw-content-text > div > div:nth-child(4) > table:nth-child({i}) > tbody > tr:nth-child({j}) > td:nth-child(3) > a'
                episode_title = response.css(f'{episode_selector}::text').get()
                episode_link = response.css(f'{episode_selector}::attr(href)').get()


                if episode_title is not None and episode_link is not None:
                    episode_link = response.urljoin(episode_link) # Convert relative URL to absolute URL
                    print(f'{episode_title}: {episode_link}')
                    yield scrapy.Request(episode_link, self.parse_episode)
                                        
                    print(f'\n-----------{episode_title}\'s TRANSCRIPT-----------\n')
                    episode_title = episode_title.replace(' ', '_') # Replace spaces with underscores
                    transcript_link = f'{episode_link}/transcript'
                    print(f'{episode_title}: {transcript_link}')
                else: # No more episodes in the season
                    break

            
            print(f'---------------------------------------------\n')

    def parse_episode(self, response):
        item = EpisodeItem()
        item['title'] = response.xpath(self.info_selector['Title']).get()
        general = response.xpath(self.info_selector['General']).getall()
        if len(general) != 5:  # Unexpected information
            return None
        item['season'] = general[0]
        item['episode'] = general[1]
        item['us_viewers'] = general[3]
        item['running_time'] = general[4]
        airdateMonthDay = response.xpath(self.info_selector['AirdateMonthDay']).get()
        airdateYear = response.xpath(self.info_selector['AirdateYear']).get()
        if airdateMonthDay is not None and airdateYear is not None:
            airdateMonthDay = airdateMonthDay.split()
            item['airdate'] = f"{airdateMonthDay[1]} {self.month_dic[airdateMonthDay[0]]} {airdateYear}"
        else:
            item['airdate'] = "TBD"
        item['writers'] = response.xpath(self.info_selector['Writers']).getall()
        item['animation'] = response.xpath(self.info_selector['Animation']).getall()
        characters = response.xpath(self.info_selector['Characters'])
        item['characters'] = [character.xpath('./a[1]/text()').get() for character in characters if not character.xpath('.//ul')]
        synopsis = response.xpath(self.info_selector['Synopsis'])
        item['synopsis'] = ''.join([''.join(p.xpath('.//text()').getall()).strip() for p in synopsis])
        item['musics'] = list(set(response.xpath(self.info_selector['Musics']).getall()))

        transcript_link = f"{response.url}/transcript"
        yield scrapy.Request(transcript_link, self.parse_transcript, meta={'item': item})

    def parse_transcript(self, response):
        item = response.meta['item']
        ul_elements = response.css('div.mw-parser-output ul')
        transcript_lines = []

        for ul in ul_elements:
            li_elements = ul.css('li')

            for li in li_elements:
                character = li.css('b::text').get(default='').strip() # Nome do personagem a dialogar

                # Se recebe ':' como nome de personagem, significa que o nome da personagem está como hiperligação (<a>)
                if character == ':':
                    character = li.css('b a::text').get(default='').strip()
                    
                dialogue_parts = li.xpath('.//text()').getall() # Retira todos os nodes de texto, incluindo as tags <i>

                dialogue = ' '.join(part.strip() for part in dialogue_parts if part.strip()) # Retirar espaços em branco e juntar as partes do diálogo

                if dialogue:
                    transcript_lines.append(f"{dialogue}")

        item['transcript'] = '\n'.join(transcript_lines)

        yield item