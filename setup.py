#! /usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='driving_forecast',
    packages=find_packages(),
    version='0.1.0',
    description='Provides forecast along a driving route to help determine best departure time.',
    author='Michael T. Neylon',
    author_email='michael.t.neylon@gmail.com',
    url='https://github.com/michaelneylon/driving_weather_forecast',
    download_url='https://github.com/michaelneylon/driving_weather_forecast/archive/0.1.0.tar.gz',
    license='MIT',
    install_requires=[
          'geopy',
      ],
)
