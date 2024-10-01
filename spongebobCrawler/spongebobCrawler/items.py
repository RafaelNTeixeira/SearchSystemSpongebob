# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SpongebobcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

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
