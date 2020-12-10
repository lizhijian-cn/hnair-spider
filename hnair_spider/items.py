# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HnairSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    departure_airport = scrapy.Field()
    arrival_airport = scrapy.Field()
    departure_time = scrapy.Field()
    arrival_time = scrapy.Field()
    price = scrapy.Field()

