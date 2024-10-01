import scrapy

class EpisodeItem(scrapy.Item):
    title = scrapy.Field()
    season = scrapy.Field()
    episode = scrapy.Field()
    us_viewers = scrapy.Field()
    running_time = scrapy.Field()
    airdate = scrapy.Field()
    writers = scrapy.Field()
    animation = scrapy.Field()
    characters = scrapy.Field()
    synopsis = scrapy.Field()
    musics = scrapy.Field()
    transcript = scrapy.Field()
    url = scrapy.Field()