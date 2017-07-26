#! /usr/bin/env python
# coding=utf-8
#
# Copyright © 2017 Gael Lederrey <gael.lederrey@epfl.ch>
#
# Distributed under terms of the MIT license.

########################################################################################
##                                                                                    ##
##          This file gives an example for parsing the file ratings.txt.gz.           ##
##            You can copy the function parse in order to parse this file.            ##
##                                                                                    ##
########################################################################################

import gzip


def parse(filename):
    """
    Parse a txt.gz file and return a generator for it

    Copyright © 2017 Gael Lederrey <gael.lederrey@epfl.ch>

    :param filename: name of the file
    :return: Generator to go through the file
    """
    file = gzip.open(filename, 'rb')
    entry = {}
    # Go through all the lines
    for line in file:
        # Transform the string-bytes into a string
        line = line.decode("utf-8").strip()

        # We check for a colon in each line
        colon_pos = line.find(":")
        if colon_pos == -1:
            # if no, we yield the entry
            yield entry
            entry = {}
            continue
        # otherwise, we add the key-value pair to the entry
        key = line[:colon_pos]
        value = line[colon_pos + 2:]
        entry[key] = value


def run():
    """
    Example how to use the function parse
    """

    # Load the file ratings.txt.gz in the data/parsed folder
    iterator = parse('../data/parsed/ratings.txt.gz')

    print('The username of the first ten ratings are:')

    nbr = 0
    # Go through the elements in the iterator
    for item in iterator:

        # Get the user name in this case.
        # Look at the README.md for all the elements in the itens
        username = item['user_name']

        # Print it
        print(username)

        nbr += 1

        # After 10 usernames printed, we stop
        if nbr == 10:
            break


if __name__ == '__main__':
    run()
