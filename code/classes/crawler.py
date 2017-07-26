#! /usr/bin/env python
# coding=utf-8
#
# Copyright © 2017 Gael Lederrey <gael.lederrey@epfl.ch>
#
# Distributed under terms of the MIT license.

from classes.helpers import round_
import pandas as pd
import numpy as np
import requests
import html
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

            if place == 'Chicago':
                # This is the first city, therefore, we need to stop the loop here
                break

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
    ##                       Crawl the pages for all the breweries                        ##
    ##                                                                                    ##
    ########################################################################################

    def crawl_all_breweries(self):
        """
        STEP 3

        Crawl all the breweries pages

        !!! Make sure step 2 was done with the parser !!!
        """

        df = pd.read_csv(self.data_folder + 'parsed/breweries.csv')

        folder = self.data_folder + 'breweries/'
        # Create folder for all the HTML pages
        if not os.path.exists(folder):
            os.makedirs(folder)

        for i in df.index:
            row = df.ix[i]
            link = row['link']
            id_ = row['id']

            folder = self.data_folder + 'breweries/'

            # Check if file already exists
            if not os.path.exists(folder + str(id_) + '.html'):
                # Get the HTML page
                r = self.request_and_wait(link)

                # Save it
                with open(folder + str(id_) + '.html', 'wb') as output:
                    output.write(r.content)

    ########################################################################################
    ##                                                                                    ##
    ##                              Crawl all the beers                                   ##
    ##                                                                                    ##
    ########################################################################################

    def crawl_all_beers_and_reviews(self):
        """
        STEP 5

        Crawl all the reviews from all the beers.

        !!! Make sure step 4 was done with the parser !!!
        """

        # Read the CSV file
        df = pd.read_csv(self.data_folder + 'parsed/beers.csv')

        df = df[:1000]

        folder = self.data_folder + 'beers/'
        # Create folder for all the HTML pages
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Number of step for crawling the review pages
        step = 10

        for i in df.index:
            row = df.ix[i]
            brewery_id = row['brewery_id']
            beer_id = row['beer_id']

            try:
                # Create the folder
                folder = self.data_folder + 'beers/{:d}/{:d}/'.format(brewery_id, beer_id)
                if not os.path.exists(folder):
                    os.makedirs(folder)

                if not os.path.exists(folder + '1.html'):
                    # Get it and write it
                    r = self.request_and_wait(row['link'])
                    with open(folder + '1.html', 'wb') as output:
                        output.write(r.content)

                html_txt = open(folder + '1.html', 'rb').read().decode('ISO-8859-1')

                # Unescape the HTML characters
                html_txt = html.unescape(html_txt)

                # Get the number of ratings
                str_ = 'RATINGS: </abbr><big style="color: #777;"><b><span id="_ratingCount8" itemprop="ratingCount" ' \
                       'itemprop="reviewCount">(\d+)</span>'
                grp = re.search(str_, str(html_txt))

                if grp is not None:
                    nbr = round_(int(grp.group(1).replace(',', '')) - 1, step)

                    # Get all the pages with the reviews and ratings
                    for i in range(1, int(nbr / step) + 1):
                        idx = i + 1
                        if not os.path.exists(folder + str(idx) + '.html'):
                            url = row['link'] + '/1/{}/'.format(idx)

                            r = self.request_and_wait(url)

                            with open(folder + str(idx) + '.html', 'wb') as output:
                                output.write(r.content)
            except Exception as e:
                print('---------------------------------------------------------------------')
                print('')
                print('ERROR WITH BREWERY_ID {} AND BEER_ID {}'.format(brewery_id, beer_id))
                print(e)
                print('---------------------------------------------------------------------')
                print('')
                pass

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
