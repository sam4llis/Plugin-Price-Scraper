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

    def __init__(self, url: str) -> None:
        self.url = url
        self._data = requests.get(self.url)

    def __repr__(self) -> str:
        fmt_hdr = lambda d: '\n'.join( f'{k}: {v}' for k, v in d.items() )

        return f'''
            \r---------- request ----------
            \r{self._data.request.method} {self._data.request.url}

            \r{fmt_hdr(self._data.request.headers)}

            \r---------- response ----------
            \r{self._data.status_code} {self._data.reason} {self._data.url}

            \r{fmt_hdr(self._data.headers)}
            '''

    def __str__(self) -> str:
        return repr(self)

    @property
    def soup(self):
        return BeautifulSoup(self._data.text, 'html.parser')


class PluginParser:
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

    def __init__(self, data: str) -> None:
        self.data = data

    def query_data_one(self, d: dict):
        q = self.data
        for tag, class_ in d.items():
            q = q.find(tag, class_) # type: ignore
        return q.text.strip() if q != None else None

    def query_data_all(self, d: dict):
        tag, class_ = d.keys(), d.items()
        return self.data.find_all(tag, class_=class_)

    def get_date(self, format: str='%d-%m-%y %H:%M') -> str:
        return datetime.now().strftime(format)


class UADPlugin(PluginParser):
    """
    A sub-class from 'PluginParser' which is used to specifically scrape data
    for Universal Audio plugins.

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
    def __init__(self, data: str) -> None:
        super().__init__(data)

    def __repr__(self) -> str:
        return str(self.to_dict())

    def __str__(self) -> str:
        return repr(self)

    def to_dict(self) -> dict:
        return {
                'name': self.name,
                'price': self.price,
                'on_sale': self.on_sale,
                'datetime': self.get_date()
                }

    @property
    def name(self):
        d = {'h2': 'product-name', 'a': None}
        return self.query_data_one(d)

    @property
    def price(self) -> int:
        d = {'p': 'special-price', 'span': 'price'} if self.on_sale \
                else {'span': 'price'}
        return self.price_to_int(self.query_data_one(d))

    def price_to_int(self, p: str) -> int:
        return int( float(p[1:].replace(',', '')) )

    @property
    def on_sale(self):
        d = {'p': 'special-price'}
        return bool(self.query_data_one(d))

    def catogory(self):
        # Only needs to be scraped once!
        pass

    def url(self):
        # Only needs to be scraped once
        pass

class UADCoupon:
    pass

class CouponParser:
    pass

class FireStore:
    pass

class FileUtil:

    def __init__(self, plugin, directory) -> None:
        self.plugin = plugin # UADPlugin class object
        self.directory = directory
        self.filepath = os.path.join(self.directory, self.filename)
        self.directory_exists = os.path.exists(self.directory)
        self.file_exists = os.path.exists(self.filepath)

        if not self.directory_exists:
            os.makedirs(self.directory)

    def write_to_csv(self):
        """if file exists, append to it, else create it"""
        self.df = pd.DataFrame.from_dict([self.plugin.to_dict()])
        self.df.to_csv(self.filepath, mode='a',
                header= not self.file_exists, index=False)

    @property
    def filename(self):
        s = self.plugin.name.encode('ascii', errors='ignore').decode() + '.csv'
        return s.replace("'", '').replace(' & ', '_').replace('/', '_').replace(' ', '_').lower()


def main():
    url = 'https://www.uaudio.com/uad-plugins/all-plugins.html'
    data = Fetcher(url)
    plugins = PluginParser(data.soup).query_data_all( {'li': 'item'} )

    for plug in plugins:
        p = UADPlugin(plug)
        f = FileUtil(p, directory='data/UAD')
        f.write_to_csv()

if __name__ == "__main__":
    main()
