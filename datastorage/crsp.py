#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Import industry returns.

Notes
-----
Never use 'grouped.mean()' in pandas! It leaks memory big time!

"""
from __future__ import print_function, division

import os
import zipfile

import pandas as pd
import datetime as dt
import numpy as np


__location__ = os.path.realpath(os.path.join(os.getcwd(),
                                os.path.dirname(__file__)))
path = os.path.join(__location__, '../CRSP/data/')


def convert_dates(string):
    """Convert dates from string to Python date format.

    """
    return dt.datetime.strptime(string, '%d-%m-%Y')


def cum_returns(ret):
    """Accumulate returns over time.

    """
    return np.exp(np.log(1 + ret).sum()) - 1


def import_returns():
    """Import raw data.

    The file is called industry_returns.zip

    Columns:
    DATE : str
        Date in the format 'dd-mm-yyy'
    HSICCD : int
        SIC industry codes
    CUSIP : str
        Firm ID
    PRC : float
        Price
    SHROUT : int
        Shares outstanding
    RETX : float
        Dividend adjusted monthly returns

    Typical output:
    Before resampling:
            Date  SIC     CUSIP   Price  Shares    Return
    0 1983-01-31  133  06022110  20.250    7074  0.094595
    1 1983-01-31  174  68417710   2.250   20546 -0.142857
    2 1983-01-31  179  25660510   9.125   27996  0.028169
    3 1983-01-31  251  86666510   5.750     614  0.022222
    4 1983-01-31  752  87831510   9.250    8400  0.088235

    After resampling:
                          return      value
    SIC CUSIP    year
    100 45292410 1995 -23.529461  15334.250
                 1996 -56.982108  15703.750
                 1997 -79.020959   8129.000
                 1998  38.372241   1755.125
    115 24487820 1988  21.428654  87612.375

    """
    # Import raw data
    zfile = zipfile.ZipFile(path + 'firm_returns.zip', 'r')
    data = zfile.open(zfile.namelist()[0])
    converters = {'DATE': convert_dates}
    returns = pd.read_csv(data, converters=converters, engine='c')
    # Rename columns
    columns = {'DATE': 'date', 'HSICCD': 'SIC',
               'PRC': 'price', 'SHROUT': 'shares',
               'RETX': 'return'}
    returns.rename(columns=columns, inplace=True)
    # Remove incorrect observations
    cond1 = returns['return'] != 'C'
    cond2 = returns['price'] > 0
    cond3 = returns['shares'] > 0
    returns = returns[cond1 & cond2 & cond3]
    # Convert to floats
    returns.loc[:, 'return'] = returns['return'].astype(float)

    print(returns.head())

    # Resample monthly returns to annual frequency
    returns = resample_returns(returns)

    returns.to_hdf(path + 'firm_returns.h5', 'returns')

    print(returns.head())


def resample_returns(returns):
    """Resample monthly returns to annual frequency.

    Typical output:
                          return      value
    SIC CUSIP    year
    100 45292410 1995 -23.529461  15334.250
                 1996 -56.982108  15703.750
                 1997 -79.020959   8129.000
                 1998  38.372241   1755.125
    115 24487820 1988  21.428654  87612.375

    """
    returns.eval('value = shares * price')
    returns.loc[:, 'year'] = returns['date'].apply(lambda x: x.year)
    index = ['SIC', 'CUSIP', 'year']
    returns.set_index(index, inplace=True)
    returns = returns.loc[:, ['return', 'value']]
    returns.sort_index(inplace=True)

    grouped = returns.groupby(level=index)
    returns = grouped[['return']].apply(cum_returns)
    returns.loc[:, 'value'] = grouped['value'].first()
    returns.loc[:, 'return'] *= 100

    return returns


def load_returns():
    """Load data from the disk.

    """
    return pd.read_hdf(path + 'firm_returns.h5', 'returns')


if __name__ == '__main__':

    import_returns()

    returns = load_returns()
