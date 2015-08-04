#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Short interest dynamics

"""
from __future__ import print_function, division

import os
import zipfile

import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

__location__ = os.path.realpath(os.path.join(os.getcwd(),
                                os.path.dirname(__file__)))
path = os.path.join(__location__, '../Compustat/data/')


def date_convert(string):
    return dt.datetime.strptime(string, '%d-%m-%Y')


def import_data():
    """Import data and save it to the disk.

    """
    zf = zipfile.ZipFile(path + 'short_int.zip', 'r')
    name = zf.namelist()[0]

    short_int = pd.read_csv(zf.open(name),
                            converters={'datadate': date_convert})
    columns = {'datadate': 'date',
               'SHORTINTADJ': 'short_int',
               'GVKEY': 'gvkey'}
    short_int.rename(columns=columns, inplace=True)
    short_int.set_index(['gvkey', 'date'], inplace=True)
    short_int.sort_index(inplace=True)

    short_int.to_hdf(path + 'short_int.h5', key='short_int')

    print(short_int.head())
    print(short_int.dtypes)
    print('Number of unique companies: ',
          short_int.index.get_level_values('gvkey').nunique())
    print('Number of unique dates: ',
          short_int.index.get_level_values('date').nunique())
    print('Min and Max date: ',
          short_int.index.get_level_values('date').min().date(), ',',
          short_int.index.get_level_values('date').max().date())


def load_data():
    """Load data from disk and check for sanity.

    """
    return pd.read_hdf(path + 'short_int.h5', 'short_int')


def count_companies(short_int):
    """Plot number of companies over time.

    """
    df = short_int.reset_index().groupby('date')['gvkey'].nunique()

    sns.set_context('paper')

    df.plot(figsize=(10, 3))
    plt.show()

    data = df.ix[dt.date(2006, 1, 1):dt.date(2007, 6, 30)]
    data.plot(figsize=(10, 3))
    plt.show()


def mean_short_int(short_int):
    """Mean short interest on each date.

    """
    df = short_int.groupby(level='date')['short_int'].mean()

    sns.set_context('paper')

    df.plot(figsize=(10, 3))
    plt.show()

    df.ix[:dt.date(2004, 12, 31)].plot(figsize=(10, 3))
    plt.show()

    df.ix[dt.date(2006, 1, 1):dt.date(2007, 6, 30)].plot(figsize=(10, 3))
    plt.show()


if __name__ == '__main__':

    import_data()
    short_int = load_data()
    count_companies(short_int)
    mean_short_int(short_int)
