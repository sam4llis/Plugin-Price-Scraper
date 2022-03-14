#!/usr/bin/env python3

import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_data(fpath):
    df = pd.read_csv(fpath, parse_dates=['date'], dayfirst=True)
    print(df.info())
    plt.plot(df.date, df.price)
    plt.title(os.path.split(fpath)[1].split('.')[0].replace('_', ' '))
    plt.xlabel('Date')
    plt.ylabel('Price, £')
    plt.xticks(rotation=45)
    plt.show()


def main():
    F_DIR = os.path.join('~', 'Desktop', 'Plugin-Price-Scraper', 'data', 'UAD')
    fpath = os.path.join(F_DIR, 'api_500_series_eq_collection.csv')
    plot_data(fpath)
    return 0


if __name__ == "__main__":
    exit(main())
