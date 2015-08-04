#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Import OptionMetrics data.

"""
from __future__ import print_function, division

import os
import zipfile

import numpy as np
import pandas as pd
import datetime as dt

from scipy.interpolate import interp1d

from impvol import lfmoneyness, delta, vega
from datastorage.quandl import load_spx

path = os.getenv("HOME") + '/Dropbox/Research/data/OptionMetrics/data/'
# __location__ = os.path.realpath(os.path.join(os.getcwd(),
#                                 os.path.dirname(__file__)))
# path = os.path.join(__location__, path + 'OptionMetrics/data/')


def convert_dates(string):
    return dt.datetime.strptime(string, '%d-%m-%Y')


def import_dividends():
    """Import dividends.

    """
    zf = zipfile.ZipFile(path + 'SPX_dividend.zip', 'r')
    name = zf.namelist()[0]
    dividends = pd.read_csv(zf.open(name), converters={'date': convert_dates})

    dividends.set_index('date', inplace=True)
    dividends.sort_index(inplace=True)

    print(dividends.head())

    dividends.to_hdf(path + 'dividends.h5', 'dividends')


def import_yield_curve():
    """Import zero yield curve.

    """
    zf = zipfile.ZipFile(path + 'yield_curve.zip', 'r')
    name = zf.namelist()[0]
    yields = pd.read_csv(zf.open(name), converters={'date': convert_dates})

    # Remove weird observations
    yields = yields[yields['rate'] < 10]
    # Fill in the blanks in the yield curve
    # yields = interpolate_curve(yields)

    yields.rename(columns={'rate': 'riskfree'}, inplace=True)
    yields.set_index(['date', 'days'], inplace=True)
    yields.sort_index(inplace=True)

    print(yields.head())

    yields.to_hdf(path + 'yields.h5', 'yields')


def interpolate_curve_group(group):
    """Interpolate yields for one day.

    """
    y = np.array(group.riskfree)
    x = np.array(group.days)
    a = group.days.min()
    b = group.days.max()
    new_x = np.linspace(a, b, b-a+1).astype(int)
    try:
        new_y = interp1d(x, y, kind='cubic')(new_x)
    except:
        new_y = interp1d(x, y, kind='linear')(new_x)

    group = pd.DataFrame(new_y, index=pd.Index(new_x, name='days'))
    return group


def interpolate_curve(yields):
    """Fill in the blanks in the yield curve.

    """
    yields.reset_index(inplace=True)
    yields = yields.groupby('date').apply(interpolate_curve_group)
    yields = yields.unstack('days')
    yields.fillna(method='ffill', axis=1, inplace=True)
    yields.fillna(method='bfill', axis=1, inplace=True)
    yields = yields.stack('days')
    yields.rename(columns={0: 'riskfree'}, inplace=True)
    return yields


def import_riskfree():
    """Take the last value of the yield curve as a risk-free rate.
    Saves annualized rate in percentage points.

    """
    yields = load_yields()
    riskfree = yields.groupby(level='date').last()

    print(riskfree.head())

    riskfree.to_hdf(path + 'riskfree.h5', 'riskfree')


def import_standard_options():
    """Import standardized options.

    """
    zf = zipfile.ZipFile(path + 'SPX_standard_options.zip', 'r')
    name = zf.namelist()[0]
    data = pd.read_csv(zf.open(name), converters={'date': convert_dates})
    cols = {'forward_price': 'forward', 'impl_volatility': 'imp_vol'}
    data.rename(columns=cols, inplace=True)
    data = data.set_index(['cp_flag', 'date', 'days']).sort_index()

    print(data.head())

    data.to_hdf(path + 'std_options.h5', 'std_options')


def import_vol_surface():
    """Import volatility surface.
    Infer risk-free rate directly from data.

    """
    zf = zipfile.ZipFile(path + 'SPX_surface.zip', 'r')
    name = zf.namelist()[0]
    df = pd.read_csv(zf.open(name), converters={'date': convert_dates})
    df.loc[:, 'weekday'] = df['date'].apply(lambda x: x.weekday())

    # Apply some filters
    df = df[df['weekday'] == 2]
    df = df[df['days'] <= 365]
    df = df.drop('weekday', axis=1)

    surface = df#.set_index(['cp_flag', 'date', 'days']).sort_index()

    cols = {'impl_volatility': 'imp_vol', 'impl_strike': 'strike',
            'impl_premium': 'premium'}
    surface.rename(columns=cols, inplace=True)

    # TODO : who term structure should be imported and merged!
    riskfree = load_riskfree().reset_index()
    dividends = load_dividends().reset_index()
    spx = load_spx().reset_index()

    surface = pd.merge(surface, riskfree)
    surface = pd.merge(surface, spx)
    surface = pd.merge(surface, dividends)

    # Adjust riskfree by dividend yield
    surface['riskfree'] -= surface['rate']
    # Remove percentage point
    surface['riskfree'] /= 100
    # Replace 'cp_flag' with True/False 'call' variable
    surface.loc[:, 'call'] = True
    surface.loc[surface['cp_flag'] == 'P', 'call'] = False
    # Normalize maturity to being a share of the year
    surface['maturity'] = surface['days'] / 365
    # Rename columns
    surface.rename(columns={'spx': 'price'}, inplace=True)
    # Compute lf-moneyness
    surface['moneyness'] = lfmoneyness(surface['price'], surface['strike'],
                                       surface['riskfree'],
                                       surface['maturity'])
    # Compute option Delta normalized by current price
    surface['delta'] = delta(surface['moneyness'], surface['maturity'],
                             surface['imp_vol'], surface['call'])
    # Compute option Vega normalized by current price
    surface['vega'] = vega(surface['moneyness'], surface['maturity'],
                           surface['imp_vol'])
    # Sort index
    surface.sort_index(by=['date', 'maturity', 'moneyness'], inplace=True)

    print(surface.head())

    surface.to_hdf(path + 'surface.h5', 'surface')


def import_vol_surface_simple():
    """Import volatility surface. Simple version.

    """
    zf = zipfile.ZipFile(path + 'SPX_surface.zip', 'r')
    name = zf.namelist()[0]
    df = pd.read_csv(zf.open(name), converters={'date': convert_dates})
    df.loc[:, 'weekday'] = df['date'].apply(lambda x: x.weekday())

    # Apply some filters
    df = df[df['weekday'] == 2]
    df = df[df['days'] <= 365]
    surface = df.drop('weekday', axis=1)

    cols = {'impl_volatility': 'imp_vol', 'impl_strike': 'strike',
            'impl_premium': 'premium'}
    surface.rename(columns=cols, inplace=True)

    spx = load_spx().reset_index()
    standard_options = load_standard_options()[['forward']].reset_index()

    surface = pd.merge(surface, standard_options)
    surface = pd.merge(surface, spx)

    # Normalize maturity to being a share of the year
    surface['maturity'] = surface['days'] / 365
    surface['riskfree'] = np.log(surface['forward'] / surface['spx'])
    surface['riskfree'] /= surface['maturity']
    # Remove percentage point

    # Replace 'cp_flag' with True/False 'call' variable
    surface.loc[:, 'call'] = True
    surface.loc[surface['cp_flag'] == 'P', 'call'] = False
    # Rename columns
    surface.rename(columns={'spx': 'price'}, inplace=True)
    # Compute lf-moneyness
    surface['moneyness'] = lfmoneyness(surface['price'], surface['strike'],
                                       surface['riskfree'],
                                       surface['maturity'])
    # Compute option Delta normalized by current price
    surface['delta'] = delta(surface['moneyness'], surface['maturity'],
                             surface['imp_vol'], surface['call'])
    # Compute option Vega normalized by current price
    surface['vega'] = vega(surface['moneyness'], surface['maturity'],
                           surface['imp_vol'])
    # Take out-of-the-money options
    calls = surface['call'] & (surface['moneyness'] >= 0)
    puts = np.logical_not(surface['call']) & (surface['moneyness'] < 0)
    surface = pd.concat([surface[calls], surface[puts]])
    # Sort index
    surface.sort_index(by=['date', 'maturity', 'moneyness'], inplace=True)

    print(surface.head())

    surface.to_hdf(path + 'surface.h5', 'surface')


def load_dividends():
    """Load dividends from the disk (annualized, percentage points).

    Typical output:

                 rate
    date
    1996-01-04  2.460
    1996-01-05  2.492
    1996-01-08  2.612
    1996-01-09  2.455
    1996-01-10  2.511

    """
    return pd.read_hdf(path + 'dividends.h5', 'dividends')


def load_yields():
    """Load zero yield curve from the disk (annualized, percentage points).

    Typical output:

                     riskfree
    date       days
    1996-01-02 9        5.763
               15       5.746
               50       5.673
               78       5.609
               169      5.474
    """
    return pd.read_hdf(path + 'yields.h5', 'yields')


def load_riskfree():
    """Load risk-free rate (annualized, percentage points).

    Returns
    -------
    DataFrame
        Annualized rate in percentage points

    Typical output:

                riskfree
    date
    1996-01-02     6.138
    1996-01-03     6.125
    1996-01-04     6.142
    1996-01-05     6.219
    1996-01-08     6.220

    """
    return pd.read_hdf(path + 'riskfree.h5', 'riskfree')


def load_standard_options():
    """Load standardized options from the disk.

    Typical output:
                             forward  premium  imp_vol
    cp_flag date       days
    C       1996-01-04 30    619.345    7.285    0.103
                       60    620.935   10.403    0.105
                       91    622.523   12.879    0.105
                       122   624.080   16.156    0.114
                       152   625.545   18.259    0.116

    """
    return pd.read_hdf(path + 'std_options.h5', 'std_options')


def load_vol_surface():
    """Load volatility surface from the disk.

    Typical output:

             date  days  imp_vol  strike  premium cp_flag  forward   price
    12 1996-01-10    30    0.175 576.030    3.431       P  600.043 598.480
    11 1996-01-10    30    0.165 581.866    4.336       P  600.043 598.480
    10 1996-01-10    30    0.157 586.685    5.257       P  600.043 598.480
    9  1996-01-10    30    0.150 590.755    6.230       P  600.043 598.480
    8  1996-01-10    30    0.146 594.303    7.299       P  600.043 598.480

        maturity  riskfree   call  moneyness  delta   vega
    12     0.082     0.032  False     -0.041 -0.200  0.080
    11     0.082     0.032  False     -0.031 -0.251  0.091
    10     0.082     0.032  False     -0.023 -0.301  0.100
    9      0.082     0.032  False     -0.016 -0.351  0.106
    8      0.082     0.032  False     -0.010 -0.401  0.111

    """
    return pd.read_hdf(path + 'surface.h5', 'surface')


if __name__ == '__main__':

    pd.set_option('float_format', '{:6.3f}'.format)

#    import_dividends()
#    import_yield_curve()
#    import_riskfree()
#    import_standard_options()
#    import_vol_surface()
    import_vol_surface_simple()

#    dividends = load_dividends()
#    yields = load_yields()
#    riskfree = load_riskfree()
#    standard_options = load_standard_options()
    surface = load_vol_surface()
