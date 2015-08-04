#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download and process OxfordMan data.

Main site:
http://realized.oxford-man.ox.ac.uk/home

Download page:
http://realized.oxford-man.ox.ac.uk/data/download

Volatility 1:
http://realized.oxford-man.ox.ac.uk/media/950/realized.library.0.1.csv.zip

Volatility 2:
http://realized.oxford-man.ox.ac.uk/media/1366/
oxfordmanrealizedvolatilityindices.zip

"""
from __future__ import print_function, division

import os
import urllib
import zipfile

import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pylab as plt
import seaborn as sns

__location__ = os.path.realpath(os.path.join(os.getcwd(),
                                os.path.dirname(__file__)))
path = os.path.join(__location__, '../OxfordMan/data/')


def convert_dates(string):
    return dt.datetime.strptime(str(int(string)), '%Y%m%d')


def download_rv_data():
    """Download OxfordMan RV data.

    """
    main_url = 'http://realized.oxford-man.ox.ac.uk/media/'

    fname = 'realized.library.0.1.csv.zip'
    url = main_url + '950/' + fname
    urllib.request.urlretrieve(url, path + fname)

    fname = 'oxfordmanrealizedvolatilityindices.zip'
    url = main_url + '1366/' + fname
    urllib.request.urlretrieve(url, path + fname)


def import_rv(fname, skiprows, cols):
    """Import RV from the file.

    """
    zf = zipfile.ZipFile(fname)
    name = zf.namelist()[0]
    raw = pd.read_csv(zf.open(name), skiprows=skiprows)
    # Rename date column
    raw = raw.rename(columns={raw.columns[0]: 'date'})
    # Drop empty date rows
    raw.dropna(subset=['date'], inplace=True)
    # Convert date number to date format
    raw['date'] = raw['date'].apply(convert_dates)
    # Reindex data
    raw.set_index('date', inplace=True)
    # Subset data
    return raw[cols].dropna()


def process_rv_data():
    """Process and save OxfordMan RV data.

    """
    fname = path + 'realized.library.0.1.csv.zip'
    skiprows = [0, ]
    cols = ['SPX_rv']
    rv1 = import_rv(fname, skiprows, cols)

    fname = path + 'oxfordmanrealizedvolatilityindices.zip'
    skiprows = [0, 1]
    cols = ['SPX2.rv']
    rv2 = import_rv(fname, skiprows, cols)

    rv1 = rv1.rename(columns={'SPX_rv': 'RV'})
    rv2 = rv2.rename(columns={'SPX2.rv': 'RV'})
    # Cut off the first data set
    rv1 = rv1[rv1.index < np.array(rv2.index).min()]
    # Concatenate
    data = pd.concat([rv1, rv2], axis=0)
    # Convert to annualized standard deviations in percent
    data['RV'] = (data['RV'] * 252) ** .5 * 100
    data.sort_index(inplace=True)

    data.to_hdf(path + 'realized_vol.h5', 'realized_vol')

    print(data.head())

    sns.set_context('paper')
    data.plot()
    plt.show()


def load_realized_vol():
    """Read OxfordMan RV data from disk and check for sanity.

    """
    return pd.read_hdf(path + 'realized_vol.h5', 'realized_vol')


if __name__ == '__main__':
    download_rv_data()
    process_rv_data()
    load_realized_vol()
