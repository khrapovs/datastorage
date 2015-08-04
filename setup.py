#!/usr/bin/env python
from setuptools import setup, find_packages


with open('README.rst') as file:
    long_description = file.read()

setup(name='datastorage',
      version='0.1',
      description='Data storage.',
      long_description=long_description,
      author='Stanislav Khrapov',
      author_email='khrapovs@gmail.com',
      url='https://github.com/khrapovs/datastorage',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      keywords=['data', 'econometrics', 'volatility', 'returns',
                'options', 'interest', 'rates', 'optionmetrics', 'crsp',
                'cboe', 'compustat', 'quandl'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
      ],
      )
