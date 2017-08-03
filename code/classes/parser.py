#! /usr/bin/env python
# coding=utf-8
#
# Copyright © 2017 Gael Lederrey <gael.lederrey@epfl.ch>
#
# Distributed under terms of the MIT license.

from classes.helpers import parse
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

        self.us_states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
                          'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas',
                          'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
                          'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
                          'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
                          'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas',
                          'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']

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
        df = df.drop(['link'], 1, errors='ignore')

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
            
            try:
                nbr = int(grp.group(1))
            except AttributeError:
                nbr = -1

            nbr_ratings.append(nbr)

            # Find the ABV
            str_ = '<abbr title="Alcohol By Volume">ABV</abbr>: <big style="color: #777;"><strong>(.+?)</strong></big>'

            grp = re.search(str_, html_txt)

            try:
                abv_val = float(grp.group(1).replace('%', ''))
            except (ValueError, AttributeError):
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
                except (ValueError, AttributeError):
                    avg_val = np.nan

                avg.append(avg_val)

                if nbr < 10:
                    overall_score.append(np.nan)
                    style_score.append(np.nan)
                else:
                    # Find the overall score
                    str_ = 'overall</div><div class="ratingValue" itemprop="ratingValue">(\d+)</div>'
                    grp = re.search(str_, html_txt)

                    try:
                        overall = int(grp.group(1))
                    except (ValueError, AttributeError):
                        overall = np.nan

                    overall_score.append(overall)

                    # Find the style score
                    str_ = '<div style="font-size: 25px; font-weight: bold; color: #fff; padding: 20px 0px; ">' \
                           '(\d+)<br><div class="style-text">style</div>'
                    grp = re.search(str_, html_txt)

                    try:
                        style = int(grp.group(1))
                    except (ValueError, AttributeError):
                        style = np.nan

                    style_score.append(style)

        # Add the new columns
        df.loc[:, 'nbr_ratings'] = nbr_ratings
        df.loc[:, 'overall_score'] = overall_score
        df.loc[:, 'style_score'] = style_score
        df.loc[:, 'avg'] = avg
        df.loc[:, 'abv'] = abv

        # Delete the column with the links
        df = df.drop(['link'], 1, errors='ignore')

        # Delete columns with -1 as nbr of ratings
        df = df[df['nbr_ratings'] > -1]

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
        df = pd.read_csv(self.data_folder + 'parsed/beers.csv')

        # Drop duplicates. No idea why they're here.
        df = df.drop_duplicates('beer_id', keep='first')

        # Open the GZIP file
        f = gzip.open(self.data_folder + 'parsed/ratings.txt.gz', 'wb')
        # Go through all beers
        for i in df.index:
            row = df.ix[i]

            nbr_rat = row['nbr_ratings']
            count = 0

            # Check that this beer has at least 1 rating
            if row['nbr_ratings'] > 0:

                folder = self.data_folder + 'beers/{}/{}/'.format(row['brewery_id'], row['beer_id'])

                list_ = os.listdir(folder)
                list_.sort()

                list_users = []

                for file in list_:

                    # Open the file
                    html_txt = open(folder + file, 'rb').read().decode('ISO-8859-1')

                    # Unescape the HTML characters
                    html_txt = html.unescape(html_txt)

                    # Remove the \n, \r and \t characters
                    html_txt = html_txt.replace('\r', '').replace('\n', '').replace('\t', '')

                    # Search for all the elements
                    str_ = '<div style="display:inline; padding: 0px 0px; font-size: 24px; font-weight: bold; color: ' \
                           '#036;" title="([^o]*) out of 5.0<br /><small>Aroma (\d+)/10<br />Appearance (\d+)/5<br />' \
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

                        if user_name in list_users:
                            add_rev = False
                        else:
                            list_users.append(user_name)
                            add_rev = True

                        text = g.group(13)

                        if '<small style="color: #666666">UPDATED' in text:
                            # Update the date
                            str_ = '<small style="color: #666666">UPDATED: (.+?)</i></small> (.+)'
                            grp_txt = re.search(str_, text)

                            try:
                                str_date = grp_txt.group(1)
                            except:
                                print(folder, file)
                            text = grp_txt.group(2)

                        else:
                            str_date = g.group(12)

                            # Sometimes, the user will add a second position (or a job, not sure)
                            # Therefore, we simply split the str_date
                            splitted = str_date.split(' - ')

                            idx = 0

                            while not (', 20' in splitted[idx] or ', 19' in splitted[idx]):
                                idx += 1

                            str_date = splitted[idx]

                        try:
                            year = int(str_date.split(",")[1])
                        except (ValueError, IndexError):
                            # It's possible that there's an error due to the addition of the explanation
                            # why this rating doesn't count
                            year = int(str_date.split(",")[1].split('<')[0])

                        month = time.strptime(str_date[0:3], '%b').tm_mon
                        day = int(str_date.split(",")[0][4:])

                        date = int(datetime.datetime(year, month, day, 12, 0).timestamp())

                        # Clean the text
                        text = re.sub('<[^>]+>', '', text)

                        if add_rev:
                            count += 1

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

            if count != nbr_rat:
                # If there's a problem in the HTML file, we replace the count of ratings
                # with the number we have now.
                df = df.set_value(i, 'nbr_ratings', count)

        f.close()

        # Save the CSV again
        df.to_csv(self.data_folder + 'parsed/beers.csv', index=False)

    ########################################################################################
    ##                                                                                    ##
    ##                           Get the users from the ratings                           ##
    ##                                                                                    ##
    ########################################################################################

    def get_users_from_ratings(self):
        """
        STEP 8

        Go through the file ratings.txt.gz and get all the users who have rated the beers
        """

        # Load the file ratings.txt.gz in the data/parsed folder
        iterator = parse(self.data_folder + 'parsed/ratings.txt.gz')

        users = {}

        # Go through the elements in the iterator
        for item in iterator:
            # Get the user name
            user_name = item['user_name']

            # Check if it's in the JSON for the users
            if user_name not in users.keys():
                users[user_name] = {'user_id': item['user_id'], 'nbr_ratings': 1}
            else:
                # And update the number of ratings
                users[user_name]['nbr_ratings'] += 1

        # Prepare the JSON DataFrame
        json_df = {'user_name': [], 'nbr_ratings': [], 'user_id': []}
        for key in users.keys():
            json_df['user_name'].append(key)
            json_df['nbr_ratings'].append(users[key]['nbr_ratings'])
            json_df['user_id'].append(users[key]['user_id'])

        # Transform it into a DF
        df = pd.DataFrame(json_df)

        # Save the CSV
        df.to_csv(self.data_folder + 'parsed/users.csv', index=False)

    ########################################################################################
    ##                                                                                    ##
    ##                     Parse the user page to get some information                    ##
    ##                                                                                    ##
    ########################################################################################

    def parse_all_users(self):
        """
        STEP 10

        Parse all the users to get some information

        !!! Make sure step 9 was done with the crawler !!!
        """

        # Load the DF of users
        df = pd.read_csv(self.data_folder + 'parsed/users.csv')

        location = []
        joined = []

        folder = self.data_folder + 'users/'

        for i in df.index:
            row = df.ix[i]

            file = str(row['user_id']) + '.html'

            # Open the file
            html_txt = open(folder + file, 'rb').read().decode('ISO-8859-1')

            # Unescape the HTML characters
            html_txt = html.unescape(html_txt)

            # Get the joining date
            str_ = 'Member since ([^<]*)'

            grp = re.search(str_, html_txt)
            try:
                str_date = grp.group(1)

                # Transform string to epoch
                month = time.strptime(str_date.split(' ')[0], '%b').tm_mon
                day = int(str_date.split(' ')[1])
                year = int(str_date.split(' ')[2])
                date = int(datetime.datetime(year, month, day, 12, 0).timestamp())
            except AttributeError:
                date = np.nan

            joined.append(date)

            # Get the location
            str_ = '<span class="glyphicon glyphicon-map-marker" aria-hidden="true"></span> ([^<]*)'
            grp = re.search(str_, html_txt)

            try:
                place = grp.group(1).replace('\n', '').replace('\r', '').replace('\t', '')

                # Remove the space at the end of the string
                while place[-1] == ' ':
                    place = place[:-1]

                arr = place.split(', ')

                if len(arr) == 1:
                    place = arr[0]  # .replace(',', '')
                else:
                    place = arr[-1]

                if place in self.us_states:
                    place = 'United States, ' + place

                ## MANUAL FIXING ##
                ## IN THE US ##

                if place in ['Huntsville,', 'Mobile,', 'Wedowee,']:
                    place = 'United States, Alabama'

                if place in ['Fairbanks,', 'Seward,', 'Soldotna,']:
                    place = 'United States, Alaska'

                if place == 'Little Rock,':
                    place = 'United States, Arkansas'

                if place in ['Gilbert,', 'Phoenix,', 'Prescott Valley,', 'Prescott,', 'Scottsdale,', 'Sierra Vista,',
                             'Surprise,', 'Tempe,', 'Tucson,', 'mesa,']:
                    place = 'United States, Arizona'

                if place in ['Aliso Viejo,', 'Atwater,', 'Burbank,', 'Brentwood,', 'California,', 'Carlsbad,',
                             'Clovis,', 'Corona,', 'Davis,', 'Escondido,', 'Eureka,', 'Fountain Valley,', 'Fremont,',
                             'Long Beach,', 'Los Angeles,', 'Los Gatos,', 'Lucerne Valley,', 'Magalia,',
                             'Malibu,', 'Mission Viejo,', 'Modesto,', 'Mountain View / San Luis Obispo,', 'Oakland,',
                             'Oceanside,', 'Porterville,', 'Rancho Santa Margarita,', 'Riverside,', 'Rocklin,',
                             'Sacramento,', 'San Diego,', 'San Francisco,', 'San Jose,', 'San Rafael,', 'Santa Cruz,',
                             'Santa Rosa,', 'South Pasadena,', 'Tarzana,', 'Travis AFB,', 'Vandenberg AFB,',
                             'Victorville,', 'WHITTIER,', 'West Sacramento,', 'Woodland Hills,', 'anaheim,',
                             'apple valley,', 'los angeles,', 'modesto,', 'oakland,', 'pinole,', 'redding,',
                             'riverside,', 'san diego,', 'stockton,', 'vacaville,']:
                    place = 'United States, California'

                if place in ['Boulder,', 'Broomfield,', 'Colorado Springs,', 'Denver,', 'Fort Collins,', 'Lakewood,',
                             'Littleton,', 'Loveland,', 'beavercreek,', 'colorado springs,']:
                    place = 'United States, Colorado'

                if place in ['Haddam,', 'Milford,', 'Niantic,', 'Somers,', 'West Hartford,', 'fairfield,', 'groton ct,',
                             'meriden,']:
                    place = 'United States, Connecticut'

                if place in ['Boynton Beach,', 'Cape Coral,', 'Cocoa,', 'Coral Springs,', 'DELRAY BCH,', 'Gainesville,',
                             'Jacksonville,', 'Lakeland,', 'Mary Esther,', 'Miami,', 'Mount Dora,', 'Niceville,',
                             'Northport,', 'Orlando,', 'Pembroke Pines,', 'Plantation,', 'Port Charlotte,',
                             'Port St Lucie,', 'Sebastian,', 'Tallahassee,', 'Tampa,', 'central florida,', 'sarasota,',
                             'winter garden,']:
                    place = 'United States, Florida'

                if place in ['Atlanta,', 'Decatur,', 'Lawrenceville (Atlanta),', 'Lawrenceville,', 'Norcross,',
                             'Powder Springs,', 'Ringgold,Ga.,']:
                    place = 'United States, Georgia'

                if place in ['Albany Park,', 'CHICAGO,', 'Carbondale,', 'Carpentersville,', 'Champaign,', 'Chicago,',
                             'Chicagoland,', 'Edwardsville,', 'Forest Glen,', 'Granite City,', 'Joliet,', 'Lisle,',
                             'New Lenox,', 'Plainfield,', 'River Forest,', 'Schaumburg,', 'South Elgin,',
                             'Stillman Valley,', 'Urbana,', 'central Illinois,', 'chicago,', 'hinsdale,', 'lisle,']:
                    place = 'United States, Illinois'

                if place in ['Bloomington,', 'Fishers,', 'Greenfield,', 'Indianapolis,', 'Indy,', 'Whiting,',
                             'fort wayne,']:
                    place = 'United States, Indiana'

                if place in ['Bettendorf,', 'CEDAR RAPIDS,', 'IOWA CITY,', 'Iowa City,', 'Johnston,',
                             'Windsor Heights,']:
                    place = 'United States, Iowa'

                if place in ['Fort Riley,', 'Kansas City,', 'Lenexa,', 'Winfield,']:
                    place = 'United States, Kansas'

                if place in ['Bowling Green,', 'Louisville,', 'clay,']:
                    place = 'United States, Kentucky'

                if place in ['Baton Rouge,', 'Bossier,city,', 'Kenner,', 'Louisiana,', 'New Orleans,', 'new orleans,']:
                    place = 'United States, Louisiana'

                if place in ['Gardiner,', 'Sabattus,', 'Saco,', 'Waterville,']:
                    place = 'United States, Maine'

                if place in ['Baltimore,', 'Darnestown,', 'Frederick,', 'Glen Arm,', 'North Bethesda,', 'Pikesville,',
                             'baltimore,', 'gaithersburg,', 'middle river,']:
                    place = 'United States, Maryland'

                if place in ['Boston,', 'Cohasset,', 'Concord,', 'East Bridgewater,', 'FITCHBURG,', 'Lowell City,',
                             'Natick,', 'Newbedford,', 'Newton,', 'Salem,', 'Somerville,', 'Waltham,', 'Woburn,',
                             'boston,', 'salem,', 'walpole,', 'westford,']:
                    place = 'United States, Massachusetts'

                if place in ['Ann Arbor,', 'Au Gres,', 'East Lansing,', 'Bay CIty,', 'Bloomfield Hills,', 'Clarkston,',
                             'Freeland,', 'Grand Rapids,', 'Grandville,', 'ISHPEMING,', 'Kalamazoo,',
                             'Kalamazoo..Bells Paradise,', 'Lansing,', 'MI,', 'Michigan,', 'Rogers,', 'Warren,',
                             'warren,']:
                    place = 'United States, Michigan'

                if place in ['Burnsville,', 'Cannon Falls,', 'Eden Prairie,', 'Gardner,', 'Garvin,', 'Minneapolis,',
                             'North Branch,', 'Saint Paul,', 'Wayzata,', 'Winnebago,', 'minneapolis,']:
                    place = 'United States, Minnesota'

                if place in ['Gulfport,', 'Jackson,', 'Ocean Springs,']:
                    place = 'United States, Mississippi'

                if place in ['Independence,', 'Jefferson,', 'Nixa,', 'Raytown,', 'St Charles,', 'St. Louis,']:
                    place = 'United States, Missouri'

                if place in ['Billings,', 'Wibaux,']:
                    place = 'United States, Montana'

                if place in ['North Platte,', 'OMAHA,', 'Omaha,']:
                    place = 'United States, Nebraska'

                if place in ['Las Vegas,', 'Sparks,']:
                    place = 'United States, Nevada'

                if place in ['Barnegat,', 'Burlington,', 'Collingswood,', 'Moorestown,', 'Newark,', 'North Brunswick,',
                             'Nutley,', 'Pitman,', 'Princeton,', 'Teaneck,', 'Waldwick,', 'West Deptford,',
                             'glen ridge,', 'morristown,']:
                    place = 'United States, New Jersey'

                if place in ['Albuquerque,', 'Los Ranchos,', 'Santa Fe,']:
                    place = 'United States, New Mexico'

                if place in ['Albany,', 'Brooklyn,', 'CENTERPORT,', 'Columbia,', 'Commack,', 'Feura Bush,', 'Flushing,',
                             'Fort Plain,', 'Gansevoort,', 'Gladstone,', 'Ithaca,', 'Katonah,', 'Lindenhurst,',
                             'New York,', 'North Tonawanda,', 'Pelham,', 'Rochester,', 'The Big Apple,', 'Tonawanda,',
                             'Westchester,', 'White Plains,', 'albany,', 'brooklyn,', 'fredonia,', 'lockport,',
                             'patchogue,', 'port jeff sta,']:
                    place = 'United States, New York'

                if place in ['Boone,', 'Charlotte,', 'Greensboro,', 'Louisburg,', 'Norlina,', 'Raleigh,', 'Shelby,',
                             'Tarawa Terrace,', 'Wilmington,', 'Winston-Salem,', 'fayetteville,', 'indian trail,']:
                    place = 'United States, North Carolina'

                if place in ['Centerville,', 'Cincinnati,', 'Cleveland,', 'Columbus,', 'Dayton,', 'HAMILTON OHIO,',
                             'Powell,', 'SAINT BERNARD,', 'Springboro,', 'Springfield,', 'Tiffin,', 'akron,',
                             'cleveland,', 'middle point,', 'north royalton,', 'oregonia,']:
                    place = 'United States, Ohio'

                if place in ['Jenks,', 'Middleberg,', 'NORMAN,', 'Shawnee,', 'owasso,']:
                    place = 'United States, Oklahoma'

                if place in ['Astoria,', 'Bend,', 'Eugene,', 'Hillsboro,', 'Oregon City,', 'Portland,', 'Scio,']:
                    place = 'United States, Oregon'

                if place in ['Aliquippa,', 'East Stroudsburg,', 'Erie,', 'Harrison,', 'Lock Haven,', 'Lower Burrell,',
                             'Mechanicsburg,', 'Mount Pocono,', 'New Cumberland,', 'PA,', 'Philadelphia,', 'Philly,',
                             'Pittsburgh,', 'Pocono Summit,', 'Red Lion,', 'Ridley Park,', 'Valley Forge,', 'cresson,',
                             'fenelton,', 'philadelphia,', 'roaring spring,']:
                    place = 'United States, Pennsylvania'

                if place == 'North Providence,':
                    place = 'United States, Rhode Island'

                if place in ['Bluffton,', 'Charleston,', 'Clemson,', 'travelers rest,']:
                    place = 'United States, South Carolina'

                if place == 'Spearfish,':
                    place = 'United States, South Dakota'

                if place in ['Chattanooga,', 'Knoxville,']:
                    place = 'United States, Tennessee'

                if place in ['Amarillo City,', 'Aransas Pass,', 'Arlington,', 'Austin,', 'Baytown,', 'Bryan,',
                             'Carrollton,', 'Dallas,', 'El Paso,', 'Frisco (Dallas),', 'Hewitt,', 'Houston,', 'Irving,',
                             'Killeen,', 'Kingwood,', 'Nolanville,', 'Republic of Texas,', 'San Antonio,', 'Timpson,',
                             'anna,', 'dallas,', 'helotes,', 'kyle,', 'plano,']:
                    place = 'United States, Texas'

                if place in ['Herriman,', 'LEHI,', 'Salt Lake City,', 'West Valley City,', 'clinton,',
                             'north salt lake,']:
                    place = 'United States, Utah'

                if place == 'montpelier,':
                    place = 'United States, Vermont'

                if place in ['Virginia Beach,', 'Nellysford,', 'Norfolk,', 'Richmond,', 'Staunton,']:
                    place = 'United States, Virginia'

                if place in ['Bellingham,', 'Bremerton,', 'Chehalis,', 'DC Metro Area,', 'Kelso,', 'Millcreek,',
                             'Oak Harbor,', 'Olympia,', 'Puyallup,', 'Renton,', 'Rosedale,', 'Seattle,', 'Tacoma,',
                             'Washington DC', 'Washington,', 'Washougal,']:
                    place = 'United States, Washington'

                if place in ['Beckley,', 'Elkins,', 'Huntington,']:
                    place = 'United States, West Virginia'

                if place in ['Wauwatosa,', 'Eau Claire,', 'Green Bay,', 'Madison,', 'Milwaukee,', 'New Berlin,',
                             'Oshkosh,', 'Phillips,', 'River Falls,', 'Stevens Point,', 'Stoughton,', 'Whitefish Bay,']:
                    place = 'United States, Wisconsin'

                if place == 'Sheridan,':
                    place = 'United States, Wyoming'

                ## OUTSIDE US ##

                if place in ['Australia,', 'Brisbane,', 'Geelong,', 'Newtown,', 'Pental Island,', 'Tasmania,',
                             'brunswick,']:
                    place = 'Australia'

                if place in ['Vienna,', 'Wien,']:
                    place = 'Austria'

                if place == 'flanders,':
                    place = 'Belgium'

                if place in ['Mostar,', 'Sarajevo,']:
                    place = 'Bosnia and Herzegovina'

                if place == 'Sofia,':
                    place = 'Bulgaria'

                if place in ['campinas,', 'santa branca,']:
                    place = 'Brazil'

                if place in ['Alberta', 'Brandon,', 'British Columbia', 'Milton,', 'Montreal,', 'New Brunswick',
                             'Ontario', 'Ottawa,', 'Quebec', 'Québec', 'Toronto,', 'Victoria,', 'Waterloo,',
                             'jonquiere,']:
                    place = 'Canada'

                if place == 'valparaiso,':
                    place = 'Chile'

                if place == 'canton':
                    place = 'China'

                if place == 'CROATIA,':
                    place = 'Croatia'

                if place == 'ostrava,':
                    place = 'Czech Republic'

                if place == 'copenhagen,':
                    place = 'Denmark'

                if place in ['Butt Burp Egypt,', 'Mount Sinai,']:
                    place = 'Egypt'

                if place in ['coventry,', 'Durham,', 'BROMLEY,', 'Banbury,', 'Bedford,', 'Berwick,', 'Bingley,',
                             'Birmingham,', 'Brighton,', 'Bristol,', 'Byrness,', 'Cambridge,', 'Carlisle,', 'Chelsea,',
                             'East Molesey,', 'Exeter,', 'Faversham,', 'Greater London', 'HAYWARDS HEATH,',
                             'Hillsborough,', 'Houghton,', 'Kendal,', 'Lancaster,', 'Leicester,', 'Lockport,',
                             'London,', 'Manchester,', 'Nottingham,', 'Oxford,', 'Plymouth,', 'Plynouth,',
                             'Portsmouth,', 'PoultonLancashire,', 'Reading,', 'Solihull,', 'Southampton,', 'Stafford,',
                             'Wells,', 'Westminster,', 'Woodley,', 'Worcester,', 'jarrow,', 'nottingham,',
                             'summertown,', 'taunton,']:
                    place = 'England'

                if place in ['Macon,', 'st germain en laye,']:
                    place = 'France'

                if place in ['Berlin,', 'Hadamar,', 'Marienwerder bei Bernau bei Berl,']:
                    place = 'Germany'

                if place == 'sepolia,':
                    place = 'Greece'

                if place in ['Pearl,', 'hawaii,']:
                    place = 'Hawaii'

                if place in ['Budapest,', 'Budaörs,', 'Dunakeszi,', 'Esztergom,', 'Fót,', 'Hajdúnánás,']:
                    place = 'Hungary'

                if place == 'Dublin,':
                    place = 'Ireland'

                if place in ['Italia,', 'Venice,', 'roma,']:
                    place = 'Italy'

                if place == 'KENYA,':
                    place = 'Kenya'

                if place == 'Lebanon,':
                    place = 'Lebanon'

                if place == 'La Paz,':
                    place = 'Mexico'

                if place in ['Breda,', 'Holland,', 'leiden,']:
                    place = 'Netherlands'

                if place == 'Bergen,':
                    place = 'Norway'

                if place == 'Palestine/West Bank':
                    place = 'Palestine'

                if place in ['D±browa Górnicza,', 'Mysłowice,', 'UPPER SILESIA,', 'Wrocław,', 'poznan,']:
                    place = 'Poland'

                if place == 'Fatima,':
                    place = 'Portugal'

                if place in ['Black Earth,', 'Moscow,', 'SAINT PETERSBURG,', 'Saint-Petersburg,']:
                    place = 'Russia'

                if place == 'St Helena':
                    place = 'Saint Helena'

                if place in ['Aberdeen,', 'Edinburgh,', 'Glasgow,', 'Midlothian,', 'Motherwell,']:
                    place = 'Scotland'

                if place == 'Belgrade,':
                    place = 'Serbia'

                if place in ['Pova\x9eská Bystrica,', 'Trnava,']:
                    place = 'Slovakia'

                if place in ['Compostela (Galiza),', 'BARCELONA,', 'Badalona,', 'Barcelona,', 'Bilbao,', 'CATALONIA,',
                             'Catalunya,', 'Figueres,', 'Galicia,', 'Galiza,', 'Getxo (Basque Country),', 'Gijón,',
                             'Girona,', 'Manresa,', 'Sabadell,', 'Sant Cugat,', 'Sant Julià de Vilatorta,',
                             'Sant Quirze De Besora,', 'barcelona,', 'spain,', 'toledo,']:
                    place = 'Spain'

                if place in ['Ljungbyholm,', 'Malmö,', 'Nossebro,', 'Stockholm,', 'Vallentuna,', 'Örebro,']:
                    place = 'Sweden'

                if place == 'pully,':
                    place = 'Switzerland'

                if place in ['CARDIFF,', 'Cardiff,']:
                    place = 'Wales'

                if place in ['APO AE,', 'APO,', 'Anytown,', 'Arcadia,', 'Bartlett,', 'Belgrade / Hamburg,', 'Benton,',
                             'Bled/SF,', 'Capital City,', 'Coolest place on EArth,', 'Cranford,', 'Echo,', 'FPO AP,',
                             'Graveyard,', 'Gùrny Slùnsk / Oberschlesien,', 'Hook,', 'K,', 'Keystone,',
                             'Marijuanaville,', 'Mendota,', 'Moab,', 'Monroe,', 'Mutriku/Rio Gallegos,',
                             'New England,', 'Operation Joint Forge,', 'Sa,', 'Savage,', 'Sittingbourne / Bydgoszcz,',
                             'The Sea,', 'USA,', 'United Kingdom,', 'Val Verde,', 'WY & Chicagoland,', 'anywhere usa,',
                             'beanercentral,', 'bibilau,', 'http://westchesterbeer.com,', 'imperial,', 'mtn home afb,',
                             'n/a', 'pampa,']:
                    place = np.nan

                # Change to conventional name
                if place in self.country_to_change.keys():
                    place = self.country_to_change[place]

            except (AttributeError, IndexError):
                place = np.nan

            location.append(place)

        df.loc[:, 'joined'] = joined
        df.loc[:, 'location'] = location

        # Save the CSV again
        df.to_csv(self.data_folder + 'parsed/users.csv', index=False)
