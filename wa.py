from random import randint
from time import sleep
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


OUTPUT_FILENAME = 'data.csv'


class WallaCrawler():
    def __init__(self, output, urls, chrome_driver=None):
        self.urls = urls
        self.output = output
        self.chrome_driver = chrome_driver
        self.cards = []
        self.write_header = True

    # Open headless chromedriver
    def start_deriver(self):
        chrome_options = Options()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('disable-gpu')
        chrome_options.add_argument('no-sandbox')
        if self.chrome_driver:
            self.driver = webdriver.Chrome(
                executable_path=self.chrome_driver, chrome_options=chrome_options)
        else:
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
        sleep(5)

    # Close chromedriver
    def close_driver(self):
        self.driver.quit()

    # Get info from a specific url
    def grab_card_info(self, url):
        print('Scrapping ' + url)
        self.driver.get(url)
        try:
            element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "card-result-title"))
            )
        except:
            return

        card_detail = {}
        try:
            body = self.driver.find_element_by_tag_name('body')
            card_detail['card_name'] = body.find_element_by_xpath(
                './/div[@class="ccdb"]/descendant::h1').text

            try:
                card_type = body.find_element_by_xpath(
                    './/div[contains(@class, "card-result-title")]/descendant::h6').text

                card_type_image = body.find_element_by_xpath(
                    './/div[contains(@class, "card-result-title")]/div[2]/div[2]/img').get_attribute("src")

                card_detail['card_type'] = card_type + ' | ' + card_type_image
            except Exception as identifier:
                pass

            try:
                card_detail['learn_more_link'] = body.find_element_by_xpath(
                    './/a[contains(text(), "Learn More")]').get_attribute('href')
            except Exception:
                pass

            try:
                card_detail['image_link'] = body.find_element_by_xpath(
                    './/div[contains(@class, "card-result-image")]/descendant::img').get_attribute("src")
            except Exception:
                pass

            try:
                card_features = body.find_elements_by_xpath(
                    './/img[contains(@class, "img-responsive") and contains(@class,"amenity")]')
                card_features = [f.get_attribute(
                    "data-original-title") for f in card_features]
                card_detail['card_features'] = ' | '.join(card_features)
            except Exception:
                pass

            try:
                another_card_features = body.find_elements_by_xpath(
                    './/div[@class="reward-text"]/descendant::li')
                another_card_features = [f.text for f in another_card_features]
                card_detail['another_card_features'] = ' | '.join(
                    another_card_features)
            except Exception as ex:
                pass

            try:
                card_detail['apr'] = body.find_element_by_xpath(
                    './/th[contains(text(), "APR")]/following-sibling::td[1]').text
            except Exception as identifier:
                pass

            try:
                card_detail['annual_fee'] = body.find_element_by_xpath(
                    './/th[contains(text(),"Annual Fee")]/following-sibling::td[1]').text
            except Exception as identifier:
                pass

            try:
                card_detail['foreign_transaction_fee'] = body.find_element_by_xpath(
                    './/th[contains(text(), "Foreign Transaction Fee")]/following-sibling::td[1]').text
            except Exception as identifier:
                pass

            try:
                card_detail['emv'] = body.find_element_by_xpath(
                    './/th[contains(text(), "EMV")]/following-sibling::td[1]').text
            except Exception as identifier:
                pass

            try:
                card_detail['tos'] = body.find_element_by_xpath(
                    './/a[contains(text(), "Terms of Service")]').get_attribute('href')
            except Exception as identifier:
                pass
        except Exception as ex:
            print(ex)
        finally:
            return card_detail

    def run(self):
        self.start_deriver()
        data = []
        i = 0
        try:
            for url in self.urls:
                data.append(self.grab_card_info(url))
                i += 1

                # Keep update file for every 50 records
                if i > 10:
                    self.export_to_csv(data, self.output)
                    i = 0
                    data = []
        except Exception as ex:
            pass
        finally:
            self.export_to_csv(data, self.output)
            self.close_driver()

    def export_to_csv(self, data, output):
        try:
            with open(output, 'a', newline='') as csvfile:
                fields = [
                    'Card Name',
                    'Card Type',
                    'Learn More',
                    'Image Link',
                    'Card Features',
                    'Another Card Features',
                    'APR',
                    'Annual Fee',
                    'Foreign Transaction Fee',
                    'EMV',
                    'Term Of Service'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                if self.write_header:
                    writer.writeheader()
                    self.write_header = False
                for row in data:
                    if not row:
                        continue
                    writer.writerow({
                        'Card Name': row.get('card_name'),
                        'Card Type': row.get('card_type'),
                        'Learn More': row.get('learn_more_link'),
                        'Image Link': row.get('image_link'),
                        'Card Features': row.get('card_features'),
                        'Another Card Features': row.get('another_card_features'),
                        'APR': row.get('apr'),
                        'Annual Fee': row.get('annual_fee'),
                        'Foreign Transaction Fee': row.get('foreign_transaction_fee'),
                        'EMV': row.get('emv'),
                        'Term Of Service': row.get('tos')
                    })
        except Exception as identifier:
            pass


if __name__ == '__main__':

    with open('urls.txt', 'r') as f:
        urls = f.read().splitlines()

    wa = WallaCrawler('data.csv', urls)
    wa.run()
