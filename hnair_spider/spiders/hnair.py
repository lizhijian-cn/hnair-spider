import scrapy


class HnairSpider(scrapy.Spider):
    name = 'hnair'
    allowed_domains = ['www.hnair.com']
    start_urls = ['http://www.hnair.com/']

    def parse(self, response):
        pass
