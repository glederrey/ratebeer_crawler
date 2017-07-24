#! /usr/bin/env python
# coding=utf-8
#
# Copyright © 2017 Gael Lederrey <gael.lederrey@epfl.ch>
#
# Distributed under terms of the MIT license.

import pandas as pd
import numpy as np
import requests
import time
import re
import os


class Crawler:
    """
    Crawler for RateBeer website
    """

    def __init__(self, delta_t, data_folder=None):
        """
        Initialize the class.

        :param delta_t: Average time in seconds between two requests
        :param data_folder: Folder to save the data
        """

        if data_folder is None:
            self.data_folder = '../data/'
        else:
            self.data_folder = data_folder

        self.delta_t = delta_t

        self.special_places = ['United States', 'Canada', 'England', 'Germany']
        self.codes = {213: 'United States', 39: 'Canada', 240: 'England', 79: 'Germany'}

    ########################################################################################
    ##                                                                                    ##
    ##                               Crawl the places                                     ##
    ##                                                                                    ##
    ########################################################################################

    def crawl_all_places(self):
        """
        STEP 1

        Crawl all the places
        """

        url_places = 'https://www.ratebeer.com/breweries/'

        # Create folder for all the HTML pages
        folder = self.data_folder + 'misc/'
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Crawl the countries
        r = self.request_and_wait(url_places)
        with open(folder + 'places.html', 'wb') as output:
            output.write(r.content)

        # Create folder for all the places
        folder = self.data_folder + 'places/'
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Open the HTML file and parse it to get all the links
        html = open(self.data_folder + 'misc/places.html', 'rb').read().decode('ISO-8859-1')

        str_ = 'href="/breweries/(\S+)/(\d+)/(\d+)/">(.+?)</a>'

        grp = re.finditer(str_, str(html))

        # Go through all the links and download them
        for g in grp:
            place_small = g.group(1)
            region_code = int(g.group(2))
            country_code = int(g.group(3))
            place = g.group(4)

            if 'Palestine' in place:
                place = 'Palestine'

            folder = self.data_folder + 'places/'

            if country_code in self.codes.keys():
                folder += self.codes[country_code] + '/'

            folder += place + '/'

            if not os.path.exists(folder):
                os.makedirs(folder)

            url = 'https://www.ratebeer.com/breweries/{}/{:d}/{:d}/'.format(place_small, region_code, country_code)
            r = self.request_and_wait(url)
            with open(folder + 'brew.html', 'wb') as output:
                output.write(r.content)

    ########################################################################################
    ##                                                                                    ##
    ##                                Other functions                                     ##
    ##                                                                                    ##
    ########################################################################################

    def request_and_wait(self, url):
        """
        Run the function get from the package requests, then wait a certain amount of time.

        :param url: url for the requests
        :return r: the request
        """

        # Get the time we want to wait before running the function again
        delta = np.abs(np.random.normal(self.delta_t, self.delta_t/2))

        start = time.time()

        # Run the function
        r = requests.get(url)

        elapsed = time.time()-start

        # If not enough time has been spend, sleep
        if elapsed < delta:
            time.sleep(delta-elapsed)

        # Return the result
        return r
