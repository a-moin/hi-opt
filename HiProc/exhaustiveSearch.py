#***************************************************************************#
#   Copyright (c) 2016 - 2017, University of California, Berkeley.          #
#                                                                           #
#   Author(s):  Ali Moin, EECS Department, UC Berkeley.                     #
#               Pierluigi Nuzzo, EE Department, USC.                        #
#                                                                           #
#   This file is distributed under the terms in the attached LICENSE file.  #
#***************************************************************************#


# Reads all the cases from the results file, sorts them, and prints the optimized results for each PDRmin

import matplotlib.pyplot as plt
from math import *
import numpy as np


data = {}

with open('all_results') as f:
    lines = f.readlines()
    for l in range(len(lines)):
        s = lines[l].split('\t')
        data[s[0]] = [round(float(s[1]), 1), round(float(s[2])), float(s[3])]

data_sorted = sorted(data.items(), key=lambda e: (e[1][1], -e[1][0]))

for pdrMin in np.arange(50,100.1,0.5):
    for case in data_sorted:
        if case[1][0] >= pdrMin:
            print(str(pdrMin) + ': ' + str(case))
            break
    print('\n')
