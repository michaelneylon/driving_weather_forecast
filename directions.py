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

import geopy

__author__ = "Michael T. Neylon"

# TODO: allow multiple destinations

class Route:
    """
    Use OSRM demo server to find the route between two coordinates,
    including distance and time.
    """

    def __init__(self, longitude1, latitude1, longitude2, latitude2,
                 base_url='https://router.project-osrm.org', service='route',
                 version='v1', profile='driving'):
        """
        :param longitude1: Longitude of start address
        :type longitude1: float
        :param latitude1: Latitude of start address
        :type latitude1 float
        :param longitude2: Longitude of end address
        :type longitude2: float
        :param latitude2: Latitude of end address
        :type latitude2: float
        :param base_url: OSRM base url
        :param service: Service selection for OSRM API. Available options:
        route, nearest, table, match, trip, tile
        :type service: str
        :param version: Version of the api protocol
        :type version: str
        :param profile: Mode of transportation
        :type: str
        """
        self.base_url = base_url
        self.service = service
        self.version = version
        self.profile = profile
        self.longitude1 = str(longitude1)
        self.latitude1 = str(latitude1)
        self.longitude2 = str(longitude2)
        self.latitude2 = str(latitude2)


    def build_url(self):
        """
        Build a query url for the OSRM api.

        :return: the url as a string
        """
        url = "{base_url}/{service}/{version}/{profile}/{long1},{lat1};{" \
              "long2},{lat2}?overview=false&steps=true"
        url = url.format(base_url=self.base_url, service=self.service,
                         version=self.version, profile=self.profile,
                         long1=self.longitude1, lat1=self.latitude1,
                         long2=self.longitude2, lat2=self.latitude2)
        return url

    def query(self):
        """
        Request the data from OSRM.

        :return: OSRM response in JSON.
        """
        url = self.build_url()
        result = requests.get(url)
        return result.json()


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

        :return: tuple of location name, longitude, latitude
        """
        geolocator = geopy.geocoders.GoogleV3()
        location = geolocator.geocode(self.address)
        return [location, location.longitude, location.latitude]


class Directions:
    """
    Get directions for two street address. Find coordinates through Google and
    then map a route from OSRM.
    """

    def __init__(self, source, destination):
        """
        :param source: Path source = start address
        :type source: str
        :param destination: Path destination = end address
        :type destination: str
        """
        self.source = source
        self.destination = destination

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
        start = self.get_coordinates(self.source)
        end = self.get_coordinates(self.destination)
        logging.info("Start location: {}".format(start[0]))
        logging.info("End location: {}".format(end[0]))
        route = Route(longitude1=start[1], latitude1=start[2],
                      longitude2=start[1], latitude2=end[2])
        return route.query()


def CLI():
    """
    If this script is run directly, allow it to be used as a command-line tool.
    :return: argparser arguments
    """
    parser = argparse.ArgumentParser(description="Driving directions for "
                                                 "given addresses")
    parser.add_argument("-s", "-start", dest='start', type=str,
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

    x = Directions(source=arguments.start,
                   destination=arguments.destination)
    print(x.run())
