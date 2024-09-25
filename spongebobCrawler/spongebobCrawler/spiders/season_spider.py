import scrapy


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
            
            print(f'------------------------------------')
            print(f'Season {season_count}:')

            for j in range(2, 120, 2):  # j is even
                episode_selector = f'#mw-content-text > div > div:nth-child(4) > table:nth-child({i}) > tbody > tr:nth-child({j}) > td:nth-child(3) > a'
                episode_title = response.css(f'{episode_selector}::text').get()
                episode_link = response.css(f'{episode_selector}::attr(href)').get()

                ### TESTING CODE - REMOVE LATER
                if episode_title is not None and episode_link is not None:
                    episode_link = response.urljoin(episode_link) # Convert relative URL to absolute URL
                    #print(f'{episode_title}: {episode_link}')
                else: # No more episodes in the season
                    break

                if episode_title is not None and episode_link is not None:
                    yield scrapy.Request(episode_link, self.parse_episode)
            
            print(f'------------------------------------')

    def parse_episode(self, response):
        title = response.xpath(f"{self.info_selector["Title"]}").get()
        general = response.xpath(f"{self.info_selector["General"]}").getall()
        if len(general) != 5: # Unexpected information, would need to be fixed. In case of error, warn me
            return None
        season = general[0]
        episode = general[1]
        us_viewers = general[3]
        running_time = general[4]
        airdateMonthDay = response.xpath(f"{self.info_selector["AirdateMonthDay"]}")
        airdateYear = response.xpath(f"{self.info_selector["AirdateYear"]}").get() 
        if airdateMonthDay is not None and airdateYear is not None:
            airdateMonthDay = airdateMonthDay.get().split()
            airdate = airdateMonthDay[1] + ' ' + self.month_dic[airdateMonthDay[0]] + ' ' + airdateYear
        else:
            airdate = "TBD"
        writers = response.xpath(f"{self.info_selector["Writers"]}").getall()
        animation = response.xpath(f"{self.info_selector["Animation"]}").getall()
        characters = response.xpath(f"{self.info_selector["Characters"]}")
        characters = [character.xpath('./a[1]/text()').get() for character in characters if not character.xpath('.//ul')]
        synopsis = response.xpath(f"{self.info_selector["Synopsis"]}")
        synopsis = [''.join(p.xpath('.//text()').getall()).strip() for p in synopsis]
        synopsis = ''.join(synopsis) # Remove this line if we need a list, or add '\n' if we need some sort of paragraph separation later

        musics =list(set(response.xpath(f"{self.info_selector["Musics"]}").getall()))
        print(title, season, episode, us_viewers, running_time,airdate, writers, animation,characters, synopsis, musics)