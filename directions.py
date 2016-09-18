#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get driving directions and times from Google.
"""

from __future__ import print_function, unicode_literals
import requests
import logging
import argparse
import os
from datetime import datetime
import pytz
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import geopy


class GoogleDirections:
    """
    Get driving directions using google maps api.
    """

    def __init__(self, origin, destination, maps_api_key,
                 time_zone_api_key, alternatives="true",
                 departure_time="now",
                 base_url="https://maps.googleapis.com/maps/api/directions"
                          "/json?"):
        """
        Constructor method.

        :param origin: street address start point
        :type origin: str or unicode
        :param destination: street address end point
        :type destination: str or unicode
        :param maps_api_key: google maps api key
        :type maps_api_key: str or unicode
        :param time_zone_api_key: google maps time zone api key
        :type time_zone_api_key: str or unicode
        :param alternatives: str reprsenting bool if multiple routes should be
        provided, 'true' or 'false'.
        :type alternatives: str or unicode
        :param departure_time: datetime.datetime instance of departure time
        from origin
        :type departure_time: datetime.datetime()
        :param base_url: google maps api base url
        :type base_url: str or unicode
        """
        self.origin = origin
        self.destination = destination
        self.maps_api_key = maps_api_key
        self.base_url = base_url
        self.alternatives = alternatives
        self.departure_time = departure_time
        self.time_zone_api_key = time_zone_api_key

    def epoch_time(self, origin):
        """
        Convert the date and time in the starting location time zone into
        epoch/posix time.

        :param origin: lat/long coordinate for start location
        :type origin: str or unicode
        :return: epoch time as a str of an int
        """
        # TODO: compare specified time to current time in start city. warn if
        # in past. Google api returns appropriate error, but better to save a
        #  query and check it locally if possible.
        if self.departure_time != "now":
            current_timestamp = LocalTime(
                api_key=self.time_zone_api_key,
                date=self.departure_time, coordinates=origin)

            tz = current_timestamp.tz
            dt_with_tz = tz.localize(self.departure_time, is_dst=None)
            ts = (dt_with_tz - datetime(1970, 1, 1,
                                         tzinfo=pytz.utc)).total_seconds()
            return str(int(ts))
        else:
            return self.departure_time


    def query(self, start, stop, epoch_start_time):
        """
        Build the query and retrieve the response from google maps api.

        :param start: start location as lat,long string.
        :type start: str or unicode
        :param stop: stop location as lat,long string.
        :type stop: str or unicode
        :param epoch_start_time: start time in epoch/posix seconds for the
        departure time zone.
        :type epoch_start_time: str or unicode
        :return: json response
        """
        params = {'origin': start, 'destination': stop, 'alternatives':
            self.alternatives, 'departure_time': epoch_start_time,
                  'key': self.maps_api_key}
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
        epoch = self.epoch_time(start)  # check specified datetime first
        response = self.query(start, end, epoch)
        return response


class LocalTime:
    """
    Get current date and time in the start location's local time.
    """
    def __init__(self, date, coordinates, api_key,
        base_url="https://maps.googleapis.com/maps/api"
                                 "/timezone/json?"):
        """
        :param date: date-time instance
        :type date: datetime.datetime()
        :param coordinates: latitude,longitude string
        :type coordinates: str or unicode
        :param api_key: google time zone api key
        :type api_key: str or unicode
        :param base_url: google time zone base url
        :type base_url: str or unicode
        """
        self.base_url = base_url
        self.date = (date - datetime(1970,1,1)).total_seconds()
        self.coordinates = coordinates
        self.api_key = api_key
        self.local_date_time, self.tz = self.current_date_time()

    def time_zone(self):
        """
        Use google time zone api to get the time zone from the start location.

        :return: time zone ID
        """
        params = {'location': self.coordinates, 'timestamp': self.date,
                  'key': self.api_key}
        request = requests.get(self.base_url, params=params)
        response = request.json()
        time_zone = response['timeZoneId']
        return time_zone

    def current_date_time(self):
        """
        Get the current date and time in the time zone of the start location.

        :return: local date time stamp from now and the time zone instance.
        """
        tz = pytz.timezone(self.time_zone())
        local_date_time = datetime.now(tz)
        return local_date_time, tz

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
        self.google_maps_api_key, self.google_time_zone_api_key = \
            self.parse_config()


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
        maps_api_key = ""
        time_zone_api_key = ""
        config = self.read_config()
        if config.has_section('google'):
            if config.has_option('google', 'maps_api_key'):
                maps_api_key = config.get('google', 'maps_api_key').strip()
            else:
                logging.error("Malformed configuration file. No option in "
                              "'google' for 'maps_api_key'")
            if config.has_option('google', 'time_zone_api_key'):
                time_zone_api_key = config.get('google',
                                            'time_zone_api_key').strip()
            else:
                logging.error("Malformed configuration file. No option in "
                              "'google' for 'time_zone_api_key'")
        else:
            logging.error("Malformed configuration file. No section 'google'.")
        if maps_api_key and time_zone_api_key:
            return maps_api_key, time_zone_api_key
        else:
            logging.error("Missing value for google api key(s).")



def CLI():
    """
    If this script is run directly, allow it to be used as a command-line tool.

    :return: argparser arguments
    """
    def valid_date_time(s):
        try:
            return datetime.strptime(s, "%Y-%m-%dT%H:%M")
        except ValueError:
            msg = "Not a valid date-time: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)
    parser = argparse.ArgumentParser(description="Driving directions for "
                                                 "given addresses")
    parser.add_argument("-o", "--origin", dest='origin', type=str,
                        help="Start Address", required=True)
    parser.add_argument("-d", "--destination", dest='destination', type=str,
                        help="Destination Address", required=True)
    parser.add_argument("-dt", "--date_time", dest='departure_date_time',
                        help="Enter departure date and time in the future in "
                             "the format YYYY-MM-DDThh:mm in 24 hour format.",
                        type=valid_date_time,  default="now")
    args = parser.parse_args()
    return args

if __name__=="__main__":
    arguments = CLI()
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s')

    api_key = Configuration()

    y = GoogleDirections(origin=arguments.origin,
                         destination=arguments.destination,
                         departure_time=arguments.departure_date_time,
                         maps_api_key=api_key.google_maps_api_key,
                         time_zone_api_key=api_key.google_time_zone_api_key)
    print(y.run())