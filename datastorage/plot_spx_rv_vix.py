#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plot SPX, logR, RV, VIX

"""
from __future__ import print_function, division

import matplotlib.pylab as plt
import seaborn as sns
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf

from datastorage.oxfordman import load_realized_vol
from datastorage.cboe import load_vix_spx


def load_data():

    realized_vol = load_realized_vol()
    vix_spx = load_vix_spx()
    data = pd.merge(realized_vol, vix_spx, left_index=True, right_index=True)
    data['logR'] = data['SPX'].apply(np.log).diff(1)
    data.dropna(inplace=True)
    print(data.head())
    return data


def plot_SPX_logR(data):
    fig, axes = plt.subplots(nrows=2, ncols=1,
                             sharex=True, figsize=(8, 6))
    data['SPX'].plot(ax=axes[0])
    data['logR'].plot(ax=axes[1])
    axes[0].set_title('SPX')
    axes[0].set_xlabel('')
    axes[1].set_title('log(R)')
    plt.savefig('../plots/SPX_logR.eps',
                bbox_inches='tight', pad_inches=.05)
    plt.show()


def plot_RV_VIX(data):
    fig, axes = plt.subplots(nrows=2, ncols=1,
                             sharex=True, figsize=(8, 6))
    data[['RV', 'VIX']].plot(ax=axes[0])
    data['RV-VIX'] = data['RV'] - data['VIX']
    data['RV-VIX'].plot(ax=axes[1])
    axes[0].set_title('Volatility measures')
    axes[0].set_xlabel('')
    axes[1].set_title('Difference')
    plt.savefig('../plots/RV_VIX.eps',
                bbox_inches='tight', pad_inches=.05)
    plt.show()


def plot_acf(data):
    nlags = 90
    lw = 2
    x = range(nlags+1)

    plt.figure(figsize=(6, 4))
    plt.plot(x, acf(data['VIX']**2, nlags=nlags), lw=lw, label='VIX')
    plt.plot(x, acf(data['RV']**2, nlags=nlags), lw=lw, label='RV')
    plt.plot(x, acf(data['logR'], nlags=nlags), lw=lw, label='logR')
    plt.legend()
    plt.xlabel('Lags, days')
    plt.grid()
    plt.savefig('../plots/autocorr_logr_vix_rv.eps',
                bbox_inches='tight', pad_inches=.05)
    plt.show()


if __name__ == '__main__':
    sns.set_context('paper')
    data = load_data()
    plot_SPX_logR(data)
    plot_RV_VIX(data)
    plot_acf(data)
