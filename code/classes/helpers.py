#! /usr/bin/env python
# coding=utf-8
#
# Copyright © 2017 Gael Lederrey <gael.lederrey@epfl.ch>
#
# Distributed under terms of the MIT license.

import numpy as np


def round_(x, base=50):
    """
    Round a number to closest (floor) number with the given base
    :param x: Number to round
    :param base: Base for rounding
    :return: Rounded number
    """
    return int(base * np.floor(float(x)/base))