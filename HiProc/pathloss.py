#***************************************************************************#
#   Copyright (c) 2016 - 2017, University of California, Berkeley.          #
#                                                                           #
#   Author(s):  Ali Moin, EECS Department, UC Berkeley.                     #
#               Pierluigi Nuzzo, EE Department, USC.                        #
#                                                                           #
#   This file is distributed under the terms in the attached LICENSE file.  #
#***************************************************************************#


# Takes a subset of nodes as input, and writes the generated path loss map to Castalia Parameters folder,
# and return it too

from configs import *
import os

# 0 Chest
# 1	Left hip
# 2	Right hip
# 3	Left ankle
# 4	Right ankle
# 5	Right wrist
# 6	Left upper arm
# 7	Head
# 8	Back
# 9	Left wrist

# Path Loss Matrix:
pathLossMap = [[0, 70,77, 76, 82, 73, 82, 73, 87, 67],
                [70, 0,	81,	79,	84,	79,	85,	81,	90,	77],
                [77, 81, 0,	75,	74,	68,	69,	76,	84,	81],
                [76, 79, 75, 0,	59,	71,	77,	80,	85,	75],
                [82, 84, 74, 59, 0,	67,	81,	86,	86,	71],
                [73, 79, 68, 71, 67, 0,	64,	75,	77,	61],
                [82, 85, 69, 77, 81, 64, 0,	70,	75,	69],
                [73, 81, 76, 80, 86, 75, 70, 0,	81,	75],
                [87, 90, 84, 85, 86, 77, 75, 81, 0,	77],
                [67, 77, 81, 66, 71, 61, 69, 75, 77, 0]]


def make_pathloss(nodes):
    print('Building path loss for nodes ' + str(nodes))
    pathloss = ''
    for i in range(len(nodes)):
        pathloss += str(i) + '>'
        for j in range(len(nodes)):
            if j != i:
                pathloss += str(j) + ':' + str(pathLossMap[nodes[i]][nodes[j]]) + ','
        pathloss += '\n'
    # write the pathloss in parameter file
    text_file = open(os.path.join(castalia_path, 'Simulations/Parameters/WirelessChannel/BANmodels/pathLossMap.txt'), "w")
    text_file.write(pathloss)
    text_file.close()
    return pathloss
