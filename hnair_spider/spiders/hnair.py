import scrapy
from bs4 import BeautifulSoup
from scrapy import Request, FormRequest
from scrapy.http import headers, request
from selenium import webdriver
import logging
import json
from urllib import parse
import requests
from selenium import webdriver

class HnairSpider(scrapy.Spider):
    name = 'hnair'
    start_url = 'hnair.com'

    def start_requests(self):
        browser = webdriver.Chrome()
        browser.get(self.start_url)
        self.browser.implicitly_wait(4)
        box = browser.find_element_by_xpath('//*[@id="ticket-1"]')
        from_city = box.find_element_by_xpath('//*[@id="from_city1"]')
        to_city = box.find_element_by_xpath('//*[@id="to_city1"]')
        time = box.find_element_by_xpath('//*[@id="flightBeginDate1"]')
        search = box.find_element_by_xpath('//*[@id="ticket-1"]/div[6]/div[1]/button')
        print(from_city.text, to_city.text, time.text)
        yield('www.baidu.com', self.parse)
# class HnairSpider(scrapy.Spider):
#     name = 'hnair'

#     china_cities = []
#     form_data = {
#         'Search/DateInformation/departDate': '2020-12-10',
#         'Search/DateInformation/returnDate': '2020-12-12',
#         'Search/calendarSearch': 'false',
#         'Search/calendarSearched': 'false',
#         'Search/flightType': 'oneway',
#         'Search/Passengers/adults': '1',
#         'Search/Passengers/children': '0',
#         'Search/Passengers/infants': '0',
#         'Search/searchType': 'F',
#         'searchTypeValidator': 'F',
#         'Search/OriginDestinationInformation/Origin/location': 'CITY_BJS_CN',
#         'Search/OriginDestinationInformation/Destination/location':
#         'CITY_CAN_CN',
#         'Search/calendarCacheSearchDays': '60',
#         'Search/seatClass': 'A',
#         'Search/searchNearByAllFlights': 'true'
#     }

#     def start_requests(self):
#         yield Request('https://www.hnair.com/js/city.json', self.parse)

#     def parse(self, response):
#         cities = json.loads(response.text)
#         self.china_cities = [
#             city['AirPortCode'] for city in cities['China']['A'][:5]
#         ]
#         print(self.china_cities)

#         url = "https://new.hnair.com/hainanair/ibe/air/processNearByFlightSearch.do"

#         payload='Search%2FDateInformation%2FdepartDate=%202020-12-07&Search%2FDateInformation%2FreturnDate=%202020-12-12&Search%2FcalendarSearch=%20false&Search%2FcalendarSearched=%20false&Search%2FflightType=%20oneway&Search%2FPassengers%2Fadults=%201&Search%2FPassengers%2Fchildren=%200&Search%2FPassengers%2Finfants=%200&Search%2FPassengers%2FPoliceDisabled=%20&Search%2FPassengers%2FMilitaryDisabled=%20&Search%2FsearchType=%20F&searchTypeValidator=%20F&Search%2FOriginDestinationInformation%2FOrigin%2Flocation=%20CITY_BJS_CN&Search%2FOriginDestinationInformation%2FDestination%2Flocation=%20CITY_HAK_CN&Search%2FcalendarCacheSearchDays=%2060&Search%2FseatClass=%20A&Search%2FsearchNearByAllFlights=%20true'
#         headers = {
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Cookie': 'JSESSIONID=402B84E71E41D1496FB14819951A2229.HUIBEServer20; Webtrends=70e30d11.5b605d0345b7e'
#         }

#         yield Request(url=url, callback=self.parse2, method='POST', headers=headers, body=payload)

#     def parse2(self, response):
#         print(response.text)
