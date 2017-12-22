#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get weather forecast at specific time and place.
"""

from __future__ import print_function, unicode_literals
import os
import logging
import requests
import argparse
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


class Forecast:
    """
    Get weather forecast for given location (coordinates).
    https://api.darksky.net/forecast/[key]/[latitude],[longitude]
    """

    def __init__(self, latitude, longitude, api_key,
                 base_url="https://api.darksky.net/forecast", extend=True):
        """
        Constructor.
        :param latitude: latitude
        :type latitude: float
        :param longitude: longitude
        :type longitude: float
        :param api_key: dark sky weather api key
        :type api_key: str or unicode
        :param base_url: base url for dark sky weather forecast api
        :type base_url: str or unicode
        :param extend: bool whether the forecast should be extended to 168
        hours out instead of default 48.
        :type extend: bool
        """
        self.latitude = latitude
        self.longitude = longitude
        self.api_key = api_key
        self.base_url = base_url
        if extend:
            self.extend="?extend=hourly"
        else:
            self.extend=""

    def query(self):
        """
        Construct API call url and get back results.
        :return: weather forecast in json format.
        """
        url = "{base_url}/{api_key}/{latitude},{longitude}{extend_option}"
        url = url.format(base_url=self.base_url, api_key=self.api_key,
        latitude=self.latitude, longitude=self.longitude,
                         extend_option=self.extend)
        request = requests.get(url)
        return request.json()


class Configuration:
    """
    Read in api keys from the configuration file.
    """

    def __init__(self, config_file='development/config.ini'):
        """
        Constructor.

        :param config_file: path to the configuration file.
        :type config_file: str or unicode
        """
        self.config_file = config_file
        self.weather_api_key = self.parse_config()


    def read_config(self):
        """
        Check for existence of the development directory and configuration
        file. Read it in if so.

        :return: configparser.ConfigParser() object
        """
        config = configparser.ConfigParser()
        if os.path.isfile(os.path.abspath(self.config_file)):
            config.read(self.config_file)
        else:
            raise Exception("Create a 'development' directory and copy "
                            "'config.ini' into it and fill in the values.")
        return config

    def parse_config(self):
        """
        Get the relevant values from the configuration file.

        :return: the google api key
        """
        weather_api_key = ""
        config = self.read_config()
        if config.has_section('dark_sky'):
            if config.has_option('dark_sky', 'weather_api_key'):
                weather_api_key = config.get('dark_sky',
                                             'weather_api_key').strip()
            else:
                logging.error("Malformed configuration file. No option in "
                              "'dark_sky' for 'weather_api_key'")
        else:
            logging.error("Malformed configuration file. No section "
                          "'dark_sky'.")
        if weather_api_key:
            return weather_api_key
        else:
            raise Exception("Missing value for dark_sky api key(s).")

def cli():
    """
    If this script is run directly, allow it to be used as a command-line tool.

    :return: argparser arguments
    """
    parser = argparse.ArgumentParser(description="Weather forecast for given location.")
    parser.add_argument("-lat", "--latitude", dest='latitude', type=float,
                        help="Latitude", required=True)
    parser.add_argument("-long", "--longitude", dest='longitude', type=float,
                        help="Longitude", required=True)
    args = parser.parse_args()
    return args

if __name__=="__main__":
    args = cli()
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s')
    config = Configuration()
    forecast = Forecast(
        latitude=args.latitude,
        longitude=args.longitude,
        api_key=config.weather_api_key)
    print(forecast.query())
    print("Powered by Dark Sky https://darksky.net/poweredby/")
