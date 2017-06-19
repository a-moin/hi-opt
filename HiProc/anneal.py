#***************************************************************************#
#   Copyright (c) 2016 - 2017, University of California, Berkeley.          #
#                                                                           #
#   Author(s):  Ali Moin, EECS Department, UC Berkeley.                     #
#               Pierluigi Nuzzo, EE Department, USC.                        #
#                                                                           #
#   This file is distributed under the terms in the attached LICENSE file.  #
#***************************************************************************#


import random
import numpy as np
import simanneal

# s = [n0, n1, ..., n9, rt, MAC, pw]
PDRmin = 100
PDR_FAIL = 1e6
INFEAS = 1e8
t_sim = 0
data = {}
searched = {}
with open('all_results.txt') as f:
    lines = f.readlines()
    for l in range(len(lines)):
        s = lines[l].split('\t')
        data[s[0]] = [round(float(s[1]), 1), round(float(s[2])), float(s[3])]


class HIannealer(simanneal.Annealer):

    def move(self):
        # choose a random entry in the matrix
        i = random.randrange(len(self.state))
        # flip the entry 0 <=> 1
        if i == 12:
            self.state[i] = (self.state[i] + 1) % 3
        else:
            self.state[i] = 1 - self.state[i]

    def energy(self):
        # evaluate the function to minimize
        global t_sim
        global searched
        nodes = []
        for j in range(10):
            if self.state[j] > 0:
                nodes.append(j)
        if self.state[11] == 1:
            mac = 'CSMA'
        else:
            mac = 'TDMA'
        if self.state[10] == 1:
            routing = 'Star'
        else:
            routing = 'Mesh'
        if self.state[12] == 0:
            pw = '-20dBm'
        elif self.state[12] == 1:
            pw = '-10dBm'
        else:
            pw = '0dBm'
        dickey = str(nodes) + '|' + mac + '|' + pw + '|' + routing

        if dickey in data:
            if dickey not in searched:
                searched[dickey] = data[dickey]
                t_sim += data[dickey][2]
            PDR = data[dickey][0]
            if PDR >= PDRmin:
                return data[dickey][1]
            else:
                return PDR_FAIL
        else:
            return INFEAS


s = []
for r in range(12):
    s.append(random.randint(0, 1))
s.append(random.randint(0, 2))
opt = HIannealer(s)
opt.steps = 8000
opt.Tmin = 17.0
opt.Tmax = 480000.0
print(opt.anneal())
print(t_sim/3600)
print(len(searched))


# steps = 6000
#
# for i in range(50):
#     correct = True
#     print('Steps: ' + str(steps))
#     for j in range(10):
#         s = []
#         for r in range(12):
#             s.append(random.randint(0,1))
#         s.append(random.randint(0,2))
#
#         opt = HIannealer(s)
#         opt.steps = steps
#         opt.Tmin = 17.0
#         opt.Tmax = 480000.0
#
#         ann_res = opt.anneal()
#         print(ann_res)
#         if ann_res[1] != 3826.0:
#             correct = False
#             break
#     if correct is True:
#         print(steps)
#         break
#     steps += 1000
