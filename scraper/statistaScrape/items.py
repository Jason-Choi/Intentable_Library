# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StatistaItem(scrapy.Item):
    title = scrapy.Field()
    market = scrapy.Field()
    topic = scrapy.Field()
    spec = scrapy.Field()   
    caption = scrapy.Field()
    
    id = scrapy.Field()
    pass