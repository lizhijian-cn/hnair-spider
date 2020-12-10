import scrapy
from scrapy import Request
from selenium import webdriver
import logging
import time
import json
import traceback
from bs4 import BeautifulSoup
import random
import string
import zipfile

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from hnair_spider.items import HnairSpiderItem


class HnairSpider(scrapy.Spider):
    name = 'hnair-v2'
    start_url = 'https://www.hnair.com/'

    hot_cities = []

    def start_requests(self):

        # self.proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        #     "host": proxyHost,
        #     "port": proxyPort,
        #     "user": proxyUser,
        #     "pass": proxyPass,
        # }
        # self.count = 0
        yield Request(
            'https://www.hnair.com/js/city2.json',
            self.parse,
        )

    def parse(self, response):
        cities = json.loads(response.text)
        self.hot_cities = cities['hotCityChina']
        # self.hot_cities = [
        #     city['AirPortName'] for city in cities['hotCityChina']
        # ]
        for city in cities['hotCityChina']:
            print(city['AirPortName'], city['AirPortCode'])

        cp = webdriver.ChromeOptions()
        # cp.add_argument('--headless')
        # cp.add_argument('--disable-gpu')
        proxyUser = "JYQS1685688983256767"
        proxyPass = "MiG93z6Vs5bO"
        proxyHost = "dyn.horocn.com"
        proxyPort = "50000"
        proxy_auth_plugin_path = self.create_proxy_auth_extension(
            proxy_host=proxyHost,
            proxy_port=proxyPort,
            proxy_username=proxyUser,
            proxy_password=proxyPass)
        cp.add_argument("--start-maximized")
        # cp.add_extension(proxy_auth_plugin_path)
        cp.add_experimental_option(
            'prefs', {
                "profile.managed_default_content_settings.images": 2,
            })
        browser = webdriver.Chrome(chrome_options=cp)
        try:
            browser.get(self.start_url)
            for from_name_code in self.hot_cities:
            # for _ in range(1):
                for to_name_code in self.hot_cities:
                    from_name = from_name_code['AirPortName']
                    # from_name = '重庆江北'
                    to_name = to_name_code['AirPortName']
                    if from_name != to_name:
                        logging.info(from_name)
                        logging.info(to_name)
                        browser.switch_to_window(browser.window_handles[0])
                        WebDriverWait(browser, 20, 2).until(
                            EC.presence_of_element_located((
                                By.XPATH,
                                '/html/body/div[5]/div/div/div[1]/div/div[1]/div[6]/div[1]/button'
                            )))

                        box = browser.find_element_by_xpath(
                            '//*[@id="ticket-1"]')
                        from_city = box.find_element_by_xpath(
                            '//*[@id="from_city1"]')
                        to_city = box.find_element_by_xpath(
                            '//*[@id="to_city1"]')
                        date = box.find_element_by_xpath(
                            '//*[@id="flightBeginDate1"]')
                        straight = box.find_element_by_xpath(
                            '//*[@id="onlyDirectId"]/i')
                        search = browser.find_element_by_xpath(
                            '/html/body/div[5]/div/div/div[1]/div/div[1]/div[6]/div[1]/button'
                        )

                        from_city.clear()
                        from_city.send_keys(from_name)
                        to_city.clear()
                        to_city.send_keys(to_name)
                        date.clear()
                        date.send_keys('2020-12-14')
                        straight.click()
                        logging.debug(browser.current_url)
                        search.click()
                        try:
                            WebDriverWait(browser, 10, 0.5).until(
                                EC.visibility_of_element_located(
                                    (By.ID, 'popup_arrive_%s' %
                                     (to_name_code['AirPortCode']))))
                            browser.find_element_by_id(
                                # '//*[@id="popup_arrive_SYX"]/div[2]/div[2]/button'
                                'popup_arrive_%s' %
                                (to_name_code['AirPortCode'])
                            ).find_element_by_class_name(
                                'btn-disabled').click()
                        except Exception as e:
                            print('repr(e):\t', repr(e))
                            print('traceback.format_exc():\n%s' %
                                  traceback.format_exc())
                        browser.switch_to_window(browser.window_handles[1])
                        try:
                            WebDriverWait(browser, 20, 1).until(
                                EC.presence_of_all_elements_located(
                                    (By.XPATH,
                                     '/html/body/div[3]/div[1]/div[10]/div[2]'
                                     )))
                        except Exception as e:
                            print('traceback.format_exc():\n%s' %
                                  traceback.format_exc())
                            browser.close()
                            continue

                        text = browser.page_source.encode('utf-8')
                        browser.close()
                        soup = BeautifulSoup(text, 'lxml')
                        flights = soup.find_all('div',
                                                class_='flight-list-item')
                        for flight in flights:
                            item = HnairSpiderItem()
                            departure = flight.find('div',
                                                    class_='flight-departure')
                            arrival = flight.find('div',
                                                  class_='flight-arrive')
                            item['departure_airport'] = departure.find(
                                'p', class_='airport').text
                            item['arrival_airport'] = arrival.find(
                                'p', class_='airport').text
                            item['departure_time'] = departure.find(
                                'p', class_='time').text
                            item['arrival_time'] = arrival.find(
                                'p', class_='time').text

                            item['price'] = []

                            its = flight.find_all('div', class_='flight-cabin')
                            for it in its:
                                type = it.find('p', class_='cabin-type')
                                amount = it.find('strong', class_='pricetag')
                                i = {'type': type.text, 'amount': 'sold out'}
                                if (amount):
                                    i['amount'] = amount.text
                                item['price'].append(i)
                            yield item

        except Exception as e:
            print('repr(e):\t', repr(e))
            print('traceback.format_exc():\n%s' % traceback.format_exc())


    def create_proxy_auth_extension(self,
                                    proxy_host,
                                    proxy_port,
                                    proxy_username,
                                    proxy_password,
                                    scheme='http',
                                    plugin_path=None):
        if plugin_path is None:
            # 请保证下面的路径可用
            plugin_path = r'qtproxy-tunnel-ext.zip'

        manifest_json = """
        {
            "version": "1.0.1",
            "manifest_version": 2,
            "name": "Qtproxy(proxy.horocn.com)",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = string.Template("""
            var config = {
                mode: "fixed_servers",
                rules: {
                    singleProxy: {
                        scheme: "${scheme}",
                        host: "${host}",
                        port: parseInt(${port})
                    },
                    bypassList: ["localhost"]
                }
            };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "${username}",
                        password: "${password}"
                    }
                };
            }

            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """).substitute(
            host=proxy_host,
            port=proxy_port,
            username=proxy_username,
            password=proxy_password,
            scheme=scheme,
        )

        with zipfile.ZipFile(plugin_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        return plugin_path

