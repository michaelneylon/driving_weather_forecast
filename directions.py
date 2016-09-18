#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get driving directions and times from Open Source Routing Machine (OSRM).
https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md

Resolve coordinates using Google Maps through geopy.
"""

from __future__ import print_function, unicode_literals
import requests
import logging
import argparse
import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import geopy

__author__ = "Michael T. Neylon"

# TODO: allow multiple destinations

class GoogleDirections:
    """
    Get driving directions using google maps api.
    """

    def __init__(self, origin, destination, api_key,
                 base_url="https://maps.googleapis.com/maps/api/directions"
                          "/json?"):
        """

        :param origin:
        :param destination:
        :param api_key:
        :param base_url:
        """
        self.origin = origin
        self.destination = destination
        self.api_key = api_key
        self.base_url = base_url

    def query(self, start, stop):
        params = {'origin': start, 'destination': stop,
                  'key': self.api_key}
        request = requests.get(self.base_url, params=params)
        return request.json()

    def get_coordinates(self, address):
        """
        Call to Coordinates class to resolve coordinates for a given street
        address.

        :param address: Street address
        :type address: str
        :return: Coordinates.location() tuple
        """
        loc = Coordinates(address)
        return loc.location()

    def run(self):
        """
        Public method to call to resolve addresses into coordinates and call
        the Route class to retrieve directions.

        :return: route data in json format
        """
        start = self.get_coordinates(self.origin)
        end = self.get_coordinates(self.destination)
        logging.info("Start location: {}".format(start[0]))
        logging.info("End location: {}".format(end[0]))
        start = "{},{}".format(start[1], start[2])
        end = "{},{}".format(end[1], end[2])
        response = self.query(start, end)
        return response

class Coordinates:
    """
    Get the coordinates of a given address using Google Maps through geopy.
    """

    def __init__(self, address):
        """
        :param address: street address
        :type address: str
        """
        self.address = address

    def location(self):
        """
        Get the resolved address and coordinates for a given street address
        using Google maps through geopy.

        :return: tuple of location name, latitude, longitude
        """
        geolocator = geopy.geocoders.GoogleV3()
        location = geolocator.geocode(self.address)
        return [location, location.latitude, location.longitude]


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
        self.google_api_key = self.parse_config()

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
        config = self.read_config()
        if config.has_section('google'):
            if config.has_option('google', 'apikey'):
                google_api_key = config.get('google', 'apikey').strip()
                if google_api_key:
                    return google_api_key
            else:
                logging.error("Malformed configuration file. No option in "
                              "'google' for 'apikey'")
        else:
            logging.error("Malformed configuration file. No section 'google'.")


def CLI():
    """
    If this script is run directly, allow it to be used as a command-line tool.

    :return: argparser arguments
    """
    parser = argparse.ArgumentParser(description="Driving directions for "
                                                 "given addresses")
    parser.add_argument("-o", "-origin", dest='origin', type=str,
                        help="Start Address", required=True)
    parser.add_argument("-d", "-destination", dest='destination', type=str,
                        help="Destination Address", required=True)
    args = parser.parse_args()
    return args

if __name__=="__main__":
    arguments = CLI()
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s')

    api_key = Configuration().google_api_key

    y = GoogleDirections(origin=arguments.origin,
                         destination=arguments.destination, api_key=api_key)

    print(y.run())