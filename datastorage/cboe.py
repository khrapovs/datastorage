#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download and process CBOE data.

Volatility:
http://www.cboe.com/micro/vix/historical.aspx

Correlation:
http://www.cboe.com/micro/impliedcorrelation/

"""
from __future__ import print_function, division

import os
import urllib

import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns

__location__ = os.path.realpath(os.path.join(os.getcwd(),
                                os.path.dirname(__file__)))
path = os.path.join(__location__, '../CBOE/data/')


def download_vix_data():
    """Download CBOE VIX data.

    """
    fname = 'dailypricehistory.xls'
    url = 'http://www.cboe.com/micro/buywrite/' + fname
    urllib.request.urlretrieve(url, path + fname)


def process_vix_data():
    """Process and save CBOE VIX data.

    """
    xl = pd.ExcelFile(path + 'dailypricehistory.xls')
    # Parse first sheet
    raw = xl.parse('Daily', skiprows=range(4))
    # Rename date column
    raw.rename(columns={raw.columns[0]: 'date'}, inplace=True)
    for name in raw.columns[1:]:
        raw.rename(columns={name: name[:3]}, inplace=True)
    # Reindex data
    raw.set_index('date', inplace=True)
    # Clean up string data
    raw = raw.applymap(lambda x: x if isinstance(x, float) else np.nan)
    # Subset data
    data = raw[['SPX', 'VIX']].dropna()

    data.to_hdf(path + 'vix_spx.h5', 'vix_spx')
    print(data.head())

    sns.set_context('paper')
    data.plot(subplots=True)
    plt.show()


def load_vix_spx():
    """Load CBOE VIX data from disk and check for sanity.

    """
    return pd.read_hdf(path + 'vix_spx.h5', 'vix_spx')


if __name__ == '__main__':
    download_vix_data()
    process_vix_data()
    load_vix_spx()
