#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import data from Quandl

"""
from __future__ import print_function, division

import os

import Quandl as ql
import pandas as pd
import pandas.io.data as web
import matplotlib.pylab as plt
import seaborn as sns


__all__ = ['import_spx', 'load_spx']

__location__ = os.path.realpath(os.path.join(os.getcwd(),
                                os.path.dirname(__file__)))
path = os.path.join(__location__, '../Quandl/data/')


def import_spx(plot=False):
    """Import SPX prices.

    """
    token = open(os.path.join(__location__, 'Quandl.token')).read()
    spx = ql.get("YAHOO/INDEX_GSPC", authtoken=token)[['Close']]
    spx.rename(columns={'Close': 'spx'}, inplace=True)
    spx.index.names = ['date']

    print(spx.head())
    spx.to_hdf(path + 'spx.h5', 'spx')

    if plot:
        sns.set_context('paper')
        spx.plot()
        plt.show()


def import_vix(plot=False):
    """Import VIX prices.

    """
    token = open(os.path.join(__location__, 'Quandl.token')).read()
    vix = ql.get("YAHOO/INDEX_VIX", authtoken=token)[['Close']]
    vix.rename(columns={'Close': 'vix'}, inplace=True)
    vix.index.names = ['date']

    print(vix.head())
    vix.to_hdf(path + 'vix.h5', 'vix')

    if plot:
        sns.set_context('paper')
        vix.plot()
        plt.show()


def import_ff_factors_a():
    """Import annual Fama-French factors.

    """
    factors = web.get_data_famafrench('F-F_Research_Data_Factors')[1]
    factors.columns = ['MKT', 'SMB', 'HML', 'RF']
    factors.index.names = ['year']

    factors.to_hdf(path + 'ff_factors.h5', 'ff_factors')
    print(factors.head())


def load_spx():
    """Load SPX index from the disk.

    Typical output:

                  spx
    date
    1950-01-03 16.660
    1950-01-04 16.850
    1950-01-05 16.930
    1950-01-06 16.980
    1950-01-09 17.080

    """
    return pd.read_hdf(path + 'spx.h5', 'spx')


def load_vix():
    """Load VIX index from the disk.

    Typical output:

                  vix
    date
    1990-01-02 17.240
    1990-01-03 18.190
    1990-01-04 19.220
    1990-01-05 20.110
    1990-01-08 20.260

    """
    return pd.read_hdf(path + 'vix.h5', 'vix')


def load_ff_factors_a():
    """Load annual Fama-French factors.

    Typical output:

             MKT     SMB     HML     RF
    year
    1927  29.470  -2.500  -3.670  3.120
    1928  35.390   4.200  -6.150  3.560
    1929 -19.540 -30.790  11.830  4.750
    1930 -31.230  -5.130 -12.280  2.410
    1931 -45.110   3.530 -14.290  1.070

    """
    return pd.read_hdf(path + 'ff_factors.h5', 'ff_factors')


if __name__ == '__main__':
    import_ff_factors_a()
    load_ff_factors_a()
    import_spx()
    load_spx()
    import_vix()
    load_vix()
