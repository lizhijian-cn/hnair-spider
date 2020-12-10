from time import time
import scrapy
import logging
import time

from scrapy.http import headers


class TestSpider(scrapy.Spider):
    name = 'test'

    payload = 'Search%2FDateInformation%2FdepartDate=%202020-12-08&Search%2FDateInformation%2FreturnDate=%202020-12-12&Search%2FcalendarSearch=%20false&Search%2FcalendarSearched=%20false&Search%2FflightType=%20oneway&Search%2FPassengers%2Fadults=%201&Search%2FPassengers%2Fchildren=%200&Search%2FPassengers%2Finfants=%200&Search%2FPassengers%2FPoliceDisabled=%20&Search%2FPassengers%2FMilitaryDisabled=%20&Search%2FsearchType=%20F&searchTypeValidator=%20F&Search%2FOriginDestinationInformation%2FOrigin%2Flocation=%20CITY_BJS_CN&Search%2FOriginDestinationInformation%2FDestination%2Flocation=%20CITY_HAK_CN&Search%2FcalendarCacheSearchDays=%2060&Search%2FseatClass=%20A&Search%2FsearchNearByAllFlights=%20true'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        # 'Cookie': 'Webtrends=70e30d11.5b605d0345b7e'
    }

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
        url = "https://new.hnair.com/hainanair/ibe/air/processNearByFlightSearch.do"

        for _ in range(10):
            time.sleep(0.2)
            req = scrapy.Request(url,
                                 self.parse,
                                 headers=self.headers,
                                 meta={'proxy': proxyMeta},
                                 body=self.payload,
                                 dont_filter=True)
            yield req

    def parse(self, response):
        logging.debug({
            'body': response.text,
        })