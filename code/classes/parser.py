#! /usr/bin/env python
# coding=utf-8
#
# Copyright © 2017 Gael Lederrey <gael.lederrey@epfl.ch>
#
# Distributed under terms of the MIT license.

import pandas as pd
import numpy as np
import datetime
import time
import html
import gzip
import re
import os


class Parser:
    """
    Parser for BeerAdvocate website
    """

    def __init__(self, data_folder=None):
        """
        Initialize the class

        :param nbr_threads: Number of threads you want to give. If not given, then it will use all the possible ones.
        :param data_folder: Folder to save the data
        """

        if data_folder is None:
            self.data_folder = '../data/'
        else:
            self.data_folder = data_folder

        self.special_places = ['United States', 'Canada', 'England', 'Germany']
        self.codes = {213: 'United_States', 39: 'Canada', 240: 'England', 79: 'Germany'}

        self.country_to_change = {'British Virgin Islands': 'Virgin Islands (British)',
                                  'United States Virgin Islands': 'Virgin Islands (U.S.)',
                                  'Kyrgyz Republic': 'Kyrgyzstan',
                                  'Réunion': 'Reunion',
                                  'St Lucia': 'Saint Lucia',
                                  'St Vincent & The Grenadines': 'Saint Vincent and The Grenadines',
                                  'São Tomé & Principe': 'Sao Tome and Principe',
                                  'Senegal Republic': 'Senegal'}

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

        json_brewery = {'name': [], 'id': [], 'location': [], 'link': []}
        # Go through all the countries
        for country in list_:
            # Check if the country is in the list of special countries
            if country not in self.special_places:
                # Open the file...
                html_txt = open(folder + country + '/brew.html', 'rb').read().decode('ISO-8859-1')

                # Change name of the country to a more convenient one
                if country in self.country_to_change:
                    country = self.country_to_change[country]

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
                    json_brewery['location'].append(country)

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
                        if country == 'United States':
                            place = country + ', ' + region
                        else:
                            place = country
                        json_brewery['location'].append(place)

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

    ########################################################################################
    ##                                                                                    ##
    ##                   Parse the beer files to get some information                     ##
    ##                                                                                    ##
    ########################################################################################

    def parse_beer_files_for_information(self):
        """
        STEP 6

        Parse the beer files to get some information on the beers

        !!! Make sure step 5 was done with the crawler !!!
        """

        # Load the DF
        df = pd.read_csv(self.data_folder + 'parsed/beers.csv')

        nbr_ratings = []
        overall_score = []
        style_score = []
        avg = []
        abv = []

        for i in df.index:
            row = df.ix[i]

            file = self.data_folder + 'beers/{}/{}/1.html'.format(row['brewery_id'], row['beer_id'])

            # Open the file
            html_txt = open(file, 'rb').read().decode('ISO-8859-1')

            # Unescape the HTML characters
            html_txt = html.unescape(html_txt)

            # Find number of ratings
            str_ = 'RATINGS: </abbr><big style="color: #777;"><b><span id="_ratingCount8" itemprop="ratingCount" ' \
                   'itemprop="reviewCount">(\d+)</span>'
            grp = re.search(str_, html_txt)

            nbr = int(grp.group(1))

            nbr_ratings.append(nbr)

            # Find the ABV
            str_ = '<abbr title="Alcohol By Volume">ABV</abbr>: <big style="color: #777;"><strong>(.+?)</strong></big>'

            grp = re.search(str_, html_txt)

            try:
                abv_val = float(grp.group(1).replace('%', ''))
            except ValueError:
                abv_val = np.nan

            abv.append(abv_val)

            if nbr == 0:
                overall_score.append(np.nan)
                style_score.append(np.nan)
                avg.append(np.nan)
            else:
                # Find the weighted average
                str_ = 'WEIGHTED AVG: <big style="color: #777;"><strong><span itemprop="ratingValue">(.+?)</span>'
                grp = re.search(str_, html_txt)

                try:
                    avg_val = float(grp.group(1))

                    avg.append(avg_val)

                    if nbr < 10:
                        overall_score.append(np.nan)
                        style_score.append(np.nan)
                    else:
                        # Find the overall score
                        str_ = 'overall</div><div class="ratingValue" itemprop="ratingValue">(\d+)</div>'
                        grp = re.search(str_, html_txt)

                        overall = int(grp.group(1))

                        overall_score.append(overall)

                        # Find the style score
                        str_ = '<div style="font-size: 25px; font-weight: bold; color: #fff; padding: 20px 0px; ">' \
                               '(\d+)<br><div class="style-text">style</div>'
                        grp = re.search(str_, html_txt)

                        style = int(grp.group(1))

                        style_score.append(style)

                except ValueError:
                    overall_score.append(np.nan)
                    style_score.append(np.nan)
                    avg.append(np.nan)

        # Add the new columns
        df.loc[:, 'nbr_ratings'] = nbr_ratings
        df.loc[:, 'overall_score'] = overall_score
        df.loc[:, 'style_score'] = style_score
        df.loc[:, 'avg'] = avg
        df.loc[:, 'abv'] = abv

        # Delete the column with the links
        df = df.drop(['link'], 1)

        # Save it again
        df.to_csv(self.data_folder + 'parsed/beers.csv', index=False)

    ########################################################################################
    ##                                                                                    ##
    ##                      Parse the beer files to get the reviews                       ##
    ##                                                                                    ##
    ########################################################################################

    def parse_beer_files_for_reviews(self):
        """
        STEP 7

        Parse the beer files to get some information on the beers
        """

        # Load the DF
        df = pd.read_csv(self.data_folder + 'parsed/beers2.csv')

        # Open the GZIP file
        f = gzip.open(self.data_folder + 'parsed/ratings.txt.gz', 'wb')
        # Go through all beers
        for i in df.index:
            row = df.ix[i]

            # Check that this beer has at least 1 rating
            if row['nbr_ratings'] > 0:

                folder = self.data_folder + 'beers/{}/{}/'.format(row['brewery_id'], row['beer_id'])

                list_ = os.listdir(folder)
                list_.sort()

                for file in list_:
                    # Open the file
                    html_txt = open(folder + file, 'rb').read().decode('ISO-8859-1')

                    # Unescape the HTML characters
                    html_txt = html.unescape(html_txt)

                    # Remove the \n, \r and \t characters
                    html_txt = html_txt.replace('\r', '').replace('\n', '').replace('\t', '')

                    # Search for all the elements
                    str_ = '<div style="display:inline; padding: 0px 0px; font-size: 24px; font-weight: bold; color: ' \
                           '#036;" title="(.+?) out of 5.0<br /><small>Aroma (\d+)/10<br />Appearance (\d+)/5<br />' \
                           'Taste (\d+)/10<br />Palate (\d+)/5<br />Overall (\d+)/20<br /></small>">(.+?)</div></div>' \
                           '<small style="color: #666666; font-size: 12px; font-weight: bold;"><A HREF="/user/(\d+)/">' \
                           '(.+?)\xa0\((\d+)\)</A></I> -(.+?)- (.+?)</small><BR><div style="padding: 20px 10px 20px ' \
                           '0px; border-bottom: 1px solid #e0e0e0; line-height: 1.5;">(.+?)</div><br>'

                    grp = re.finditer(str_, html_txt)

                    for g in grp:
                        rating = float(g.group(1))

                        appearance = int(g.group(3))
                        aroma = int(g.group(2))
                        palate = int(g.group(5))
                        taste = int(g.group(4))
                        overall = int(g.group(6))

                        user_name = g.group(9)
                        user_id = int(g.group(8))

                        text = g.group(13)

                        if 'UPDATED' in text:
                            # Update the date
                            str_ = '<small style="color: #666666">UPDATED: (.+?)</i></small> (.+)'
                            grp_txt = re.search(str_, text)

                            str_date = grp_txt.group(1)
                            text = grp_txt.group(2)

                        else:
                            str_date = g.group(12)

                            # Sometimes, the user will add a second position (or a job, not sure)
                            # Therefore, we simply split the str_date
                            str_date = str_date.split(' - ')[-1]

                        try:
                            year = int(str_date.split(",")[1])
                        except ValueError:
                            # It's possible that there's an error due to the addition of the explanation
                            # why this rating doesn't count
                            year = int(str_date.split(",")[1].split('<')[0])

                        month = time.strptime(str_date[0:3], '%b').tm_mon
                        day = int(str_date.split(",")[0][4:])

                        date = int(datetime.datetime(year, month, day, 12, 0).timestamp())

                        # Write to file
                        f.write('beer_name: {}\n'.format(row['beer_name']).encode('utf-8'))
                        f.write('beer_id: {:d}\n'.format(row['beer_id']).encode('utf-8'))
                        f.write('brewery_name: {}\n'.format(row['brewery_name']).encode('utf-8'))
                        f.write('brewery_id: {:d}\n'.format(row['brewery_id']).encode('utf-8'))
                        f.write('style: {}\n'.format(row['style']).encode('utf-8'))
                        f.write('abv: {}\n'.format(row['abv']).encode('utf-8'))
                        f.write('date: {:d}\n'.format(date).encode('utf-8'))
                        f.write('user_name: {}\n'.format(user_name).encode('utf-8'))
                        f.write('user_id: {:d}\n'.format(user_id).encode('utf-8'))
                        f.write('appearance: {:d}\n'.format(appearance).encode('utf-8'))
                        f.write('aroma: {:d}\n'.format(aroma).encode('utf-8'))
                        f.write('palate: {:d}\n'.format(palate).encode('utf-8'))
                        f.write('taste: {:d}\n'.format(taste).encode('utf-8'))
                        f.write('overall: {:d}\n'.format(overall).encode('utf-8'))
                        f.write('rating: {:.2f}\n'.format(rating).encode('utf-8'))
                        f.write('text: {}\n'.format(text).encode('utf-8'))
                        f.write('\n'.encode('utf-8'))

        f.close()
