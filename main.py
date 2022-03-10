#!/usr/bin/env python3

import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


class Fetcher:
    """
    A class used to fetch all HTML data from a specified website.

    Attributes
    ----------
    url : str
        A web page's URL address.

    Methods
    -------
    soup()
        Returns HTML data from a URL request.
    """

    def __init__(self, url):
        self.url = url
        self._data = requests.get(self.url)

    def __repr__(self):

        fmt_hdr = lambda d: '\n'.join(f'{k}: {v}' for k, v in d.items())

        return f'''
            \r---------- request ----------
            \r{self._data.request.method} {self._data.request.url}

            \r{fmt_hdr(self._data.request.headers)}

            \r---------- response ----------
            \r{self._data.status_code} {self._data.reason} {self._data.url}

            \r{fmt_hdr(self._data.headers)}
            '''

    def __str__(self):
        return repr(self)

    @property
    def soup(self):
        return BeautifulSoup(self._data.text, 'html.parser')


class Parser:
    """
    A parent class used to parse the fetched HTML data into meaningful content.

    Attributes
    ----------
    data: str
        The fetched HTML data for a specific plugin.

    Methods
    -------
    query_data_one(d)
        Returns a string of HTML data with a corresponding series of HTML-tag:
        HTML class_ (key: value) pairs.

    """

    def __init__(self, data):
        self.data = data

    def query_data_one(self, d):
        q = self.data
        for tag, class_ in d.items():
            q = q.find(tag, class_)
        return q.text.strip() if q is not None else None

    def query_data_all(self, d):
        tag, class_ = d.keys(), d.items()
        return self.data.find_all(tag, class_=class_)

    def get_date(self, format='%d-%m-%y %H:%M'):
        return datetime.now().strftime(format)


class UADPlugin(Parser):
    """
    A sub-class from 'PluginParser' which is used to specifically scrape data
    for a Universal Audio plugin.

    Attributes
    ----------
    data: The fetched HTML data for a specific plugin.

    Methods
    -------
    to_dict()
        Returns a dictionary of relevant plugin data.

    name()
        Returns the name of the plugin.

    price()
        Returns the price of the plugin.

    price_to_int(p):
        Converts the price of a plugin to integer (int) format.

    on_sale()
        Returns True if the plugin is on sale, else False.
    """

    def __init__(self, data):
        super().__init__(data)

    def __repr__(self):
        return str(self.to_dict())

    def __str__(self):
        return repr(self)

    def to_dict(self):
        return {
                'name': self.name,
                'price': self.price,
                'date': TIME,
                }

    @property
    def name(self):
        d = {'h2': 'product-name', 'a': None}
        return self.query_data_one(d)

    @property
    def price(self):
        d = {'p': 'special-price', 'span': 'price'} if self.on_sale \
                else {'span': 'price'}
        return self.price_to_int(self.query_data_one(d))

    def price_to_int(self, p):
        return int(float(p[1:].replace(',', '')))

    @property
    def on_sale(self):
        d = {'p': 'special-price'}
        return bool(self.query_data_one(d))

    @property
    def brand(self):
        brand_id = ''.join(
            v for v in self.data['class'] if v.startswith('brand'))
        print(brand_id)
        return self._translate_brand_id(brand_id)

    def _translate_brand_id(self, brand_id):
        pass

    @property
    def category(self):
        # classes = [v['class'] for v in self.data.find_all(
        #     'li', 'category_ids-28')]
        # class_=lambda v: v and value.startswith('category'))]
        # classes = [v for v in self.data['class'] if v.startswith('category')]
        pass

    def url(self):  # TODO(sam3llis): complete this function
        # Only needs to be scraped once!
        pass


class UADCoupon(Parser):

    def __init__(self, data):
        super().__init__(data)


class CouponParser:
    pass


class FireStore:
    pass


class FileUtil:

    def __init__(self, plugin, directory):
        self.directory = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), directory)
        self.plugin = plugin  # UADPlugin class object
        self.filepath = os.path.join(self.directory, self.filename)
        self.directory_exists = os.path.exists(self.directory)
        self.file_exists = os.path.exists(self.filepath)

        if not self.directory_exists:
            os.makedirs(self.directory)

    def write_to_csv(self):
        """if file exists, append to it, else create it"""
        self.df = pd.DataFrame.from_dict([self.plugin.to_dict()])
        self.df.to_csv(
            self.filepath, mode='a', header=not self.file_exists, index=False)

    @property
    def filename(self):
        s = self.plugin.name.encode('ascii', errors='ignore').decode() + '.csv'
        return s.replace("'", '').replace(
            ' & ', '_').replace('/', '_').replace(' ', '_').lower()


def get_date(format='%d-%m-%y'):
    return datetime.now().strftime(format)


def main():
    global TIME
    TIME = get_date()

    url = 'https://www.uaudio.com/uad-plugins/all-plugins.html'
    data = Fetcher(url)
    plugins = Parser(data.soup).query_data_all({'li': 'item'})
    # brand_id = Parser(data.soup).query_data_one( {
    #     'h3': 'dropdown--brand'})
    # print(brand_id)
    # x: str = data.soup.find('aside').prettify()
    # print(x)
    # input()

    for plug in plugins:
        p = UADPlugin(plug)
        f = FileUtil(p, directory='data/UAD')
        f.write_to_csv()

    print(f'Successfully Scraped Plugin Data at: {TIME}')


if __name__ == "__main__":
    main()
