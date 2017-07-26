#! /usr/bin/env python
# coding=utf-8
#
# Copyright © 2017 Gael Lederrey <gael.lederrey@epfl.ch>
#
# Distributed under terms of the MIT license.

import multiprocessing as mp
import pandas as pd
import html
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
                html_txt = open(folder + country + '/brew.html', 'rb').read().decode('ISO-8859-1')

                # Unescape the HTML characters
                html_txt = html.unescape(html_txt)

                # ... and parse it
                str_ = '<A HREF="/brewers/(\S+)/(\d+)/"> (.+?)</A>'

                grp = re.finditer(str_, str(html_txt))
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
                    html_txt = open(folder + country + '/' + region + '/brew.html', 'rb').read().decode('ISO-8859-1')

                    # ... and parse it
                    str_ = '<A HREF="/brewers/(\S+)/(\d+)/"> (.+?)</A>'

                    grp = re.finditer(str_, str(html_txt))
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

    ########################################################################################
    ##                                                                                    ##
    ##                    Parse the breweries files to get the beers                      ##
    ##                                                                                    ##
    ########################################################################################

    def parse_brewery_files(self):
        """
        STEP 4

        Parse the brewery HTML files to get new info about the breweries and create the CSV for the beers

        !!! Make sure step 3 was done with the crawler !!!
        """

        # Load the DF
        df = pd.read_csv(self.data_folder + 'parsed/breweries.csv')

        folder = self.data_folder + 'breweries/'

        # Prepare the json for the DF
        json_beers = {'beer_name': [], 'brewery_name': [], 'beer_id': [], 'brewery_id': [], 'style': [], 'link': []}

        nbr_beers = []
        # Go through all the breweries
        for i in df.index:
            id_ = df.ix[i]['id']

            # Open the file
            html_txt = open(folder + str(id_) + '.html', 'rb').read().decode('ISO-8859-1')

            # Unescape the HTML characters
            html_txt = html.unescape(html_txt)

            # String to search for
            str_ = '<strong><A HREF="/beer/(\S+)/(\d+)/">([^<]*)</A></strong> (?!<em class="small">\(alias\)</em>)' \
                   '(.+?)<a href="/beerstyles/(\S+)/(\d+)/">([^<]*)</a>'

            grp = re.finditer(str_, str(html_txt))

            nbr = 0
            for g in grp:
                # Add the beer
                json_beers['beer_name'].append(g.group(3))
                json_beers['brewery_name'].append(df.ix[i]['name'])
                json_beers['beer_id'].append(g.group(2))
                json_beers['brewery_id'].append(id_)
                json_beers['style'].append(g.group(7))
                json_beers['link'].append('https://www.ratebeer.com/beer/{}/{}/'.format(g.group(1), g.group(2)))

                nbr += 1

            nbr_beers.append(nbr)

        # Add to the DF
        df.loc[:, 'nbr_beers'] = nbr_beers

        # Delete the links to the breweries
        df = df.drop(['link'], 1)

        # Save it again
        df.to_csv(self.data_folder + 'parsed/breweries.csv', index=False)

        # Transform JSON in pandas DF
        df_beers = pd.DataFrame(json_beers)

        # Save to a CSV file
        df_beers.to_csv(self.data_folder + 'parsed/beers.csv', index=False)



