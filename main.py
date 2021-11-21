import pandas as pd
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import math
import requests
import os

class PluginUAD:

    def __init__(self, plugin):
        self.plugin = plugin

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    def __str__(self):
        return repr(self)

    def scrape_data(self):
        self.name = self._get_name()
        self.url = self._get_url()
        self.bundle = self._is_bundle()
        self.sale = self._is_on_sale()
        self.r_price = self._get_regular_price()
        self.s_price = self._get_special_price()
        self.saving = self._calc_saving()

    def to_dict(self):
        self.scrape_data()
        return {
                    'URL': self.url,
                    'Bundle': self.bundle,
                    'Sale': self.sale,
                    'Regular Price (£)': self.r_price,
                    'Sale Price (£)': self.s_price,
                    'Saving (%)': self.saving,
               }

    def _get_name(self):
        return self.plugin['data-name']

    def _get_url(self):
        return self.plugin.select_one('h2.product-name a')['href']

    def _get_regular_price(self):
        if self._is_on_sale():
            price = self.plugin.select_one('p.old-price span.price').text.strip()[1:]
        else:
            price = self.plugin.select_one('span.regular-price').text.strip()[1:]
        return int(float( price.replace(',', '') ))

    def _get_special_price(self):
        if self._is_on_sale():
            price = self.plugin.select_one('p.special-price span.price').text.strip()[1:]
            return int(float( price.replace(',', '') ))

    def _is_bundle(self):
        if self._get_name() == 'UAD Custom 2 Bundle':
            # fixes categorisation error on uaudio.com.
            return True
        return 'category_ids-12' in self.plugin['class']

    def _is_on_sale(self):
        return bool(self.plugin.find('p', class_='special-price'))

    def _calc_saving(self):
        return math.floor( (1 - self.s_price / self.r_price) * 100 ) if self._is_on_sale() else 0

def fetch_data(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    data = soup.find_all('li', class_='item')
    return [PluginUAD(entry) for entry in data]

def fetch_time(zone='Europe/London', fmt='%d-%m-%Y %H:%M'):
    from datetime import datetime
    from pytz import timezone
    tz = timezone(zone)
    return datetime.now(tz).strftime(fmt)

def main():
    dir_path = os.path.dirname(os.path.abspath(__file__))
    url = 'https://www.uaudio.com/uad-plugins.html'
    d = fetch_data(url)

    data = {}
    for item in d:
        item.scrape_data()
        data[item.name] = item.to_dict()

    if not firebase_admin._apps:
        cred = credentials.Certificate(os.path.join(dir_path,'ServiceAccountKey.json'))
        default_app = firebase_admin.initialize_app(cred)
    db = firestore.client()
    db.collection('Universal Audio').document(fetch_time()).set(data)
    t = fetch_time()
    print(f'Data gathered at {t}')

    # create local backup
    df = pd.DataFrame.from_dict(data, orient='index')
    df.to_csv(os.path.join(dir_path, 'data', f'{t}.csv'), encoding='utf-8')

if __name__ == "__main__":
    main()
