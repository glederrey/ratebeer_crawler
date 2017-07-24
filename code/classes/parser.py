#! /usr/bin/env python
# coding=utf-8
#
# Copyright © 2017 Gael Lederrey <gael.lederrey@epfl.ch>
#
# Distributed under terms of the MIT license.

import multiprocessing as mp
import pandas as pd
import re
import os


class Parser:
    """
    Parser for BeerAdvocate website
    """

    def __init__(self, nbr_threads=None, data_folder=None):
        """
        Initialize the class

        :param nbr_threads: Number of threads you want to give. If not given, then it will use all the possible ones.
        :param data_folder: Folder to save the data
        """

        if data_folder is None:
            self.data_folder = '../data/'
        else:
            self.data_folder = data_folder

        if nbr_threads is None:
            self.threads = mp.cpu_count()
        else:
            self.threads = nbr_threads

        self.special_places = ['United States', 'Canada', 'England', 'Germany']
        self.codes = {213: 'United_States', 39: 'Canada', 240: 'England', 79: 'Germany'}

    ########################################################################################
    ##                                                                                    ##
    ##                       Parse the breweries from the places                          ##
    ##                                                                                    ##
    ########################################################################################

    def parse_breweries_from_places(self):
        """
        STEP 2

        Parse all the breweries name and ID from the places
        """

        folder = self.data_folder + 'parsed/'
        # Create folder for the parsed CSV tables
        if not os.path.exists(folder):
            os.makedirs(folder)

        folder = self.data_folder + 'places/'

        list_ = os.listdir(folder)

        json_brewery = {'name': [], 'id': [], 'place': [], 'link': []}
        # Go through all the countries
        for country in list_:
            # Check if the country is in the list of special countries
            if country not in self.special_places:
                # Open the file...
                html = open(folder + country + '/brew.html', 'rb').read().decode('ISO-8859-1')

                # ... and parse it
                str_ = '<A HREF="/brewers/(\S+)/(\d+)/"> (.+?)</A>'

                grp = re.finditer(str_, str(html))
                for g in grp:
                    link = 'https://www.ratebeer.com/brewers/{}/{}/'.format(g.group(1), g.group(2))

                    json_brewery['name'].append(g.group(3))
                    json_brewery['id'].append(g.group(2))
                    json_brewery['link'].append(link)
                    json_brewery['place'].append(country)

            else:
                # Get the list of regions
                list_2 = os.listdir(folder + country)
                # Go through all regions
                for region in list_2:
                    # Open the file...
                    html = open(folder + country + '/' + region + '/brew.html', 'rb').read().decode('ISO-8859-1')

                    # ... and parse it
                    str_ = '<A HREF="/brewers/(\S+)/(\d+)/"> (.+?)</A>'

                    grp = re.finditer(str_, str(html))
                    for g in grp:
                        link = 'https://www.ratebeer.com/brewers/{}/{}/'.format(g.group(1), g.group(2))

                        json_brewery['name'].append(g.group(3))
                        json_brewery['id'].append(g.group(2))
                        json_brewery['link'].append(link)
                        json_brewery['place'].append(country)

        # Transform into pandas DF
        df = pd.DataFrame(json_brewery)

        # Save it
        df.to_csv(self.data_folder + 'parsed/breweries.csv', index=False)



