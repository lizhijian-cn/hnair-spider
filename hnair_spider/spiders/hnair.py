import scrapy
from scrapy import Request, FormRequest
import logging
import json

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

from hnair_spider.items import HnairSpiderItem


class HnairSpider(scrapy.Spider):
    name = 'hnair'
    start_url = 'https://www.hnair.com/'
    hot_cities = []

    form_data = {
        'Search/DateInformation/departDate': '2020-12-12',
        'Search/DateInformation/returnDate': '2020-12-14',
        'Search/calendarSearch': 'false',
        'Search/calendarSearched': 'false',
        'Search/flightType': 'oneway',
        'Search/Passengers/adults': '1',
        'Search/Passengers/children': '0',
        'Search/Passengers/infants': '0',
        'Search/Passengers/PoliceDisabled': '0',
        'Search/Passengers/MilitaryDisabled': '0',
        'Search/searchType': 'F',
        'searchTypeValidator': 'F',
        'Search/OriginDestinationInformation/Origin/location': 'CITY_BJS_CN',
        'Search/OriginDestinationInformation/Destination/location':
        'CITY_SZX_CN',
        'Search/calendarCacheSearchDays': '60',
        'Search/seatClass': 'A',
        'Search/searchNearByAllFlights': 'true'
    }

    def start_requests(self):
        proxyUser = "JYQS1685688983256767"
        proxyPass = "MiG93z6Vs5bO"
        proxyHost = "dyn.horocn.com"
        proxyPort = "50000"

        self.proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }

        yield Request('https://www.hnair.com/js/city2.json',
                      self.parse,
                      meta={'proxy': self.proxyMeta})

    def parse(self, response):
        cities = json.loads(response.text)
        map = {
            city['AirPortCode']: city['AirPortCode'] for city in cities['hotCityChina']
        }
        self.hot_cities = [
            city['AirPortCode'] for city in cities['hotCityChina']
        ]
        for city in self.hot_cities:
            print(city)
            
        # self.get_cookies()

        url = "https://new.hnair.com/hainanair/ibe/air/processNearByFlightSearch.do"

        for from_city in self.hot_cities[:2]:
            for to_city in self.hot_cities[:2]:
                if from_city != to_city:
                    self.form_data[
                        'Search/OriginDestinationInformation/Origin/location'] = 'CITY_%s_CN' % (
                            from_city)
                    self.form_data[
                        'Search/OriginDestinationInformation/Destination/location'] = 'CITY_%s_CN' % (
                            to_city)
                    yield FormRequest(url=url,
                                      callback=self.parse_flight,
                                      method='POST',
                                    #   cookies=self.cookies,
                                      formdata=self.form_data,
                                      meta={'proxy': self.proxyMeta})

    def parse_flight(self, response):
        try:
            data = json.loads(response.text)
        except:
            logging.debug('no json')
            return

        if 'Flights' not in data['FlightSearchResults']:
            logging.error('get flights error, re try')
            return

        flights = data['FlightSearchResults']['Flights'][0]['Flight']

        for flight in flights:
            item = HnairSpiderItem()
            details = flight['FlightDetails'][0]['Summary']
            item['departure_airport'] = details['Departure']['Airport']
            item['arrival_airport'] = details['Arrival']['Airport']
            item['departure_time'] = details['Departure']['DateTime']
            item['arrival_time'] = details['Arrival']['DateTime']
            item['price'] = [{
                'name': price['FareFamilyName'],
                'price': price['Total'][0]['Amount']
            } for price in flight['Price']['FareBreakdowns'][:2]]
            yield item

    def get_cookies(self):
        browser = webdriver.Chrome()
        browser.get(self.start_url)
        try:
            WebDriverWait(browser, 20, 2).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '/html/body/div[5]/div/div/div[1]/div/div[1]/div[6]/div[1]/button'
                )))

            box = browser.find_element_by_xpath('//*[@id="ticket-1"]')
            from_city = box.find_element_by_xpath('//*[@id="from_city1"]')
            to_city = box.find_element_by_xpath('//*[@id="to_city1"]')
            date = box.find_element_by_xpath('//*[@id="flightBeginDate1"]')
            straight = box.find_element_by_xpath('//*[@id="onlyDirectId"]/i')
            search = browser.find_element_by_xpath(
                '/html/body/div[5]/div/div/div[1]/div/div[1]/div[6]/div[1]/button'
            )

            from_city.clear()
            from_city.send_keys('北京首都')
            to_city.clear()
            to_city.send_keys('广州')
            date.clear()
            date.send_keys('2020-12-14')
            straight.click()
            search.click()
            browser.switch_to_window(browser.window_handles[1])
            WebDriverWait(browser, 20, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[3]/div[1]/div[10]')))

            self.cookies = browser.get_cookies()
            # return Request(browser.current_url,
            #                self.parse2,
            #                meta={'proxy': self.proxyMeta})
        except Exception as e:
            logging.error('load failed')
        finally:
            browser.quit()