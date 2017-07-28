#! /usr/bin/env python
# coding=utf-8
#
# Copyright © 2017 Gael Lederrey <gael.lederrey@epfl.ch>
#
# Distributed under terms of the MIT license.

import numpy as np
import gzip


def round_(x, base=50):
    """
    Round a number to closest (floor) number with the given base
    :param x: Number to round
    :param base: Base for rounding
    :return: Rounded number
    """
    return int(base * np.floor(float(x)/base))


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
