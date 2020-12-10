from time import time
import scrapy
import logging
import time

class MyIPSpider(scrapy.Spider):
    name = 'my_ip'

    # start_urls = [
    #     'http://myip.ipip.ne'
    # ]

    def start_requests(self):
        proxyUser = "JYQS1685688983256767"
        proxyPass = "MiG93z6Vs5bO"
        proxyHost = "dyn.horocn.com"
        proxyPort = "50000"

        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }

        for _ in range(10):
            time.sleep(3)
            req = scrapy.Request('http://myip.ipip.net', self.parse, meta={'proxy': proxyMeta}, dont_filter=True)
            yield req

    def parse(self, response):
        logging.debug({
            'body': response.text,
        })