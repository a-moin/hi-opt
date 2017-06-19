#***************************************************************************#
#   Copyright (c) 2016 - 2017, University of California, Berkeley.          #
#                                                                           #
#   Author(s):  Ali Moin, EECS Department, UC Berkeley.                     #
#               Pierluigi Nuzzo, EE Department, USC.                        #
#                                                                           #
#   This file is distributed under the terms in the attached LICENSE file.  #
#***************************************************************************#


from pathloss import *
from subprocess import Popen, PIPE, STDOUT
from operator import truediv
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import fileinput
import os
from configs import *


# runs the simulation and writes results in output.txt
def run_sim(config='General'):
    print('Config: ' + config)
    print('Running Castalia simulation...')
    cmd1 = 'cd ' + castalia_path + '/Simulations/HIBAN'
    cmd2 = '../../bin/Castalia -c ' + config + ' -o output.txt -r 1'
    proc = Popen("{}; {}".format(cmd1, cmd2), shell=True, stdin=PIPE,
          stdout=PIPE, stderr=STDOUT, close_fds=True)
    stdout, nothing = proc.communicate()


def sim_results(output='cons -n'):
    cmd1 = 'cd ' + castalia_path + '/Simulations/HIBAN'
    cmd2 = '../../bin/CastaliaResults -i output.txt --precision=6 -s ' + output
    proc = Popen("{}; {}".format(cmd1, cmd2), shell=True, stdin=PIPE,
                  stdout=PIPE, stderr=STDOUT, close_fds=True)
    stdout, nothing = proc.communicate()
    return stdout


# reads the file formatted data, and writes it in a list of rows and columns
def read_table(data):
    table = []
    lines = data.split('\n')
    for i in range(len(lines)):
        if len(lines[i]) > 0:
            if lines[i].split()[0] == '|':
                row = lines[i][1:len(lines[i])-1].replace(" ", "")
                table.append(row.split('|'))
    return table


# reads the number of sent and received packets and returns the PDR
def calc_pdr():
    sent_table = read_table(sim_results('sent'))
    received_table = read_table(sim_results('received'))
    print(received_table)
    print(sent_table)
    res = []
    res.append(received_table[0])
    res.append(map(truediv, [float(x) for x in received_table[1]], [float(x) for x in sent_table[1]]))
    return res


# reads the energy consumed in 60s sim and calculates node lifetime (in days) based on CR2032 coin cell (first dying)
def calc_lifetime(isStar=False):
    energy = read_table(sim_results())
    print(energy)
    battery = 2430      # 3V 225mAh -> 675mWh -> 2430J
    node_lifetime = []
    node_lifetime.append(energy[0])
    lifetimes = [battery/float(enrgy)/60/24 for enrgy in energy[1]]
    if isStar:
        node_lifetime.append(sorted(lifetimes)[1])
    else:
        node_lifetime.append(sorted(lifetimes)[0])

    return node_lifetime


# reads the energy consumed in 60s sim and calculates the node lifetime (in days) based on CR2032 coin cell
def lifetime_avg():
    energy = read_table(sim_results('Energy'))
    print(energy)
    battery = 2430      # 3V 225mAh -> 675mWh -> 2430J
    node_lifetime = energy
    node_lifetime[1] = [battery/float(enrgy)/60/24 for enrgy in energy[1]]
    return node_lifetime


# gets the list of nodes, and plots the PDR for the network with each node as hub
def choose_hub(nodes):
    make_pathloss(nodes)
    config = 'numNodes=' + str(len(nodes)) + ',star,hubAddress'
    run_sim(config)
    hub_pdr = calc_pdr()
    plt.bar(range(len(hub_pdr[1])), [x*100 for x in hub_pdr[1]], 0.35)
    plt.ylabel('PDR (%)')
    plt.title('PDR for each hub choice (Star,TDMA,PacketRate=30pkt/s,TxPower=-25dBm')
    plt.xticks(np.arange(len(hub_pdr[1])) + 0.35 / 2., hub_pdr[0])
    plt.show()


def make_radio(nodes, isStar=False):
    tx = [27.3, 20.1, 18.3, 14.71, 11.56, 10.40, 9.55]
    rx = 17.7
    N = len(nodes)

    if isStar:
        pw = [x + (N - 1) * rx * 2 for x in tx]
    else:
        pw = [x + (N - 1) * rx for x in tx]
    pw_str = 'Tx_mW '
    for i in range(len(pw)):
        pw_str += str(pw[i]) + ' '

    for line in fileinput.input(os.path.join(castalia_path, 'Simulations/Parameters/Radio/CC2650.txt'), inplace=1):
        if 'Tx_mW' in line:
            line = pw_str + '\n'
        sys.stdout.write(line)

    return pw


# Function Name: single_run
#
# Inputs:
#     nodes: The set of existing nodes in network
#     routing: Routing layer options: ',star' for star, and '' for mesh
#     MAC: MAC layer options: ',CSMA' for CSMA, and '' for TDMA
#     TxPw: Tx power level (PHY) options: ',varyTxPower=\\\"-20dBm\\\"',
#           ',varyTxPower=\\\"-10dBm\\\"', or ',varyTxPower=\\\"0dBm\\\"'
#     rate: packets per second, default: 10
#     sim_time: simulation duration in seconds, default: 600s
#
# Output: [PDR, energy, cpu_duration]


def single_run(nodes, routing, MAC, TxPw, rate=10, sim_time=600):
    start_time = time.time()
    make_pathloss(nodes)
    make_radio(nodes, isStar=(routing == ',star'))

    config = 'numNodes=' + str(len(nodes)) + routing + MAC + TxPw
    run_sim(config)

    enr = read_table(sim_results())[1]
    enr_mw = [float(en) * 1000 for en in enr]
    if routing == ',star':
        energy = sorted(enr_mw, reverse=True)[1]
    else:
        energy = sorted(enr_mw, reverse=True)[0]

    end_time = time.time()

    return float(read_table(sim_results('received'))[1][0])/(rate*sim_time/(len(nodes)-1)), energy, end_time - start_time
