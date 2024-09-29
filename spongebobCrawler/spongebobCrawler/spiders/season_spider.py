import scrapy

from spongebobCrawler.items import EpisodeItem
from scrapy.spidermiddlewares.httperror import HttpError

class SeasonSpiderSpider(scrapy.Spider):
    name = 'season_spider'
    allowed_domains = ['spongebob.fandom.com']
    start_urls = ['https://spongebob.fandom.com/wiki/List_of_episodes']
    handle_httpstatus_list = [404]
    info_selector = {
        "Season": "#mw-content-text > div > div:nth-child(4) > table:nth-child({i})", # Built for css!
        "Episode": "tbody > tr:nth-child({j}) > td:nth-child(3) > a", # Built for css!
        "Title" : "//span[@class=\"mw-page-title-main\"]/text()",
        "General" : "//div[@data-source=\"title\"]//div/text()",
        "TableSeason" : "//div[@data-source=\"title\"][1]/div/text()",
        "TableEpisode" : "//div[@data-source=\"title\"][2]/div/text()",
        "TableUSViewers" : "//div[@data-source=\"title\"]/h3[contains(text(), \"U.S. viewers (millions):\")]/../div//text()",
        "TableRunningTime" : "//div[@data-source=\"title\"]/h3[contains(text(), \"Running time:\")]/../div//text()",
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
        season_aux = 5 # i is odd
        enable_print = getattr(self, "enable_print", False)
        while (True) :
            season_count += 1
            season_table = response.css(self.info_selector["Season"].format(i=season_aux)) # i is season_aux
            if season_table.get() is None: # No more seasons to search for
                break
            
            if enable_print:
                print(f'\n---------------------------------------------\n')
                print(f'Season {season_count}:\n')

            episode_aux = 2 # j is even
            while (True):
                episode_selector = self.info_selector["Episode"].format(j=episode_aux)
                episode_title = season_table.css(f"{episode_selector}::text").get()
                episode_link = season_table.css(f"{episode_selector}::attr(href)").get()


                if episode_title is not None and episode_link is not None:
                    episode_link = response.urljoin(episode_link) # Convert relative URL to absolute URL
                    if enable_print:
                        print(f'{episode_title}: {episode_link}')
                    
                    yield scrapy.Request(episode_link, self.parse_episode)
                else: # No more episodes in the season
                    break

                episode_aux += 2

            if enable_print:
                print(f'---------------------------------------------\n')
            season_aux += 5

    def parse_episode(self, response):
        item = EpisodeItem()
        item['title'] = response.xpath(self.info_selector['Title']).get()
        item['season'] = response.xpath(self.info_selector['TableSeason']).get()
        item['episode'] = response.xpath(self.info_selector['TableEpisode']).get()
        item['us_viewers'] = ' '.join([x.strip() for x in response.xpath(self.info_selector['TableUSViewers']).getall()])
        item['running_time'] = ' '.join([x.strip() for x in response.xpath(self.info_selector['TableRunningTime']).getall()])
        if item['us_viewers'] == "":
            item['us_viewers'] = "TBD"
        if item['running_time'] == "":
            item['running_time'] = "TBD"
            
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

        enable_print = getattr(self, "enable_print", False)
        if enable_print:
            print(f"Title: {item['title']}")
            print(f"Season: {item['season']}")
            print(f"Episode: {item['episode']}")
            print(f"Us viewers (millions): {item['us_viewers']}")
            print(f"Running time: {item['running_time']}")
            print(f"Airdate: {item['airdate']}")
            print("Writers:")
            for w in item['writers']:
                print(f"\t{w}")
            print("Animation:")
            for a in item['animation']:
                print(f"\t{a}")
            print("Characters:")
            for c in item['characters']:
                print(f"\t{c}")
            print(f"Synopsis: {item['synopsis']}")
            print("Musics:")
            for m in item['musics']:
                print(f"\t{m}")

        transcript_link = f"{response.url}/transcript"
        yield scrapy.Request(transcript_link, self.parse_transcript, meta={'item': item}, errback=self.transcript_error)

    def parse_transcript(self, response):
        item = response.meta['item']

        enable_print = getattr(self, "enable_print", False)
        
        if enable_print:
            print(f'\n-----------TRANSCRIPT-----------\n')

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
                    if enable_print:
                        print(f"\t{dialogue}")


        item['transcript'] = ' '.join(transcript_lines)

        yield item

    def transcript_error(self, failure):
        item = failure.meta['item']
        enable_print = getattr(self, "enable_print", False)
        # Handle errors section
        if failure.check(HttpError):
            item['transcript'] = ''
            if enable_print:
                print("Transcript: No transcript was found!")
            yield item
        