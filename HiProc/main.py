#***************************************************************************#
#   Copyright (c) 2016 - 2017, University of California, Berkeley.          #
#                                                                           #
#   Author(s):  Ali Moin, EECS Department, UC Berkeley.                     #
#               Pierluigi Nuzzo, EE Department, USC.                        #
#                                                                           #
#   This file is distributed under the terms in the attached LICENSE file.  #
#***************************************************************************#


import cplex                        # import IBM CPLEX
from pulp import *                  # import PuLP modeler functions
import pylab
import itertools
import numpy as np
from configs import *
from funcs import *


# Constants:
reTx = [2,5,10,17]                  # number of retransmitted packets in flooding for N = 3..6
P_base = 0.1                        # baseline power
P_tx = [9.55, 11.56, 18.3]          # Tx levels power consumption
P_rx = 17.7                         # Rx power consumption
T_tx = 0.00078125                   # ~1ms Tx Duration per Packet
Rate = 10                           # pkt/s
M = 100                             # big number
sim_time = 600                      # network operation duration to be simulated (in seconds)


if inputFileMode:
    # reads sim results data from the file, and creates "data" dictionary:
    data = {}
    with open('all_results.txt') as f:
        lines = f.readlines()
        for l in range(len(lines)):
            s = lines[l].split('\t')
            data[s[0]] = [round(float(s[1]), 1), round(float(s[2])), float(s[3])]


def hi_solver(pdr_min):

    # Create the 'prob' variable to contain the problem data
    prob = LpProblem("HI Lifetime", LpMinimize)

    # The variables
    nIndex = ["n0", "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9"]       # nodes
    n = LpVariable.dicts("", nIndex, 0, 1, LpInteger)

    pIndex = ["P1", "P2", "P3"]                         # power levels
    p = LpVariable.dicts("", pIndex, 0, 1, LpInteger)

    NIndex = ["N3", "N4", "N5", "N6"]                # number of mesh reTx
    N = LpVariable.dicts("", NIndex, 0, 1, LpInteger)

    spIndex = []                # star,power
    for pp in pIndex:
        spIndex.append("s"+pp)
    sp = LpVariable.dicts("", spIndex, 0, 1, LpInteger)

    sp_exp = [(sp[x], y) for x,y in zip(spIndex, P_tx)]

    snIndex = []                # star, node
    for nn in nIndex:
        snIndex.append("s"+nn)
    sn = LpVariable.dicts("", snIndex, 0, 1, LpInteger)

    mpNIndex = []               # mesh, power, reTx
    for pp in pIndex:
        for NN in NIndex:
            mpNIndex.append("m"+pp+NN)
    mpN = LpVariable.dicts("", mpNIndex, 0, 1, LpInteger)

    P_tx_reTx = [pp*rr for pp in P_tx for rr in reTx]
    mpN_exp = [(mpN[x], y) for x, y in zip(mpNIndex, P_tx_reTx)]

    mnNIndex = []               # mesh, node, reTx
    for nn in nIndex:
        for NN in NIndex:
            mnNIndex.append("m"+nn+NN)
    mnN = LpVariable.dicts("", mnNIndex, 0, 1, LpInteger)

    P_rx_reTx = [pp*rr for pp in len(nIndex)*[P_rx] for rr in reTx]
    mnN_exp = [(mnN[x], y) for x, y in zip(mnNIndex, P_rx_reTx)]

    mNIndex = []               # mesh, reTx
    for NN in NIndex:
        mNIndex.append("m"+NN)
    mN = LpVariable.dicts("", mNIndex, 0, 1, LpInteger)

    mN_exp = [(mN[x], y) for x,y in zip(mNIndex, reTx)]

    s = LpVariable("Star", 0, 1, LpInteger)
    m = LpVariable("Mesh", 0, 1, LpInteger)
    c = LpVariable("CSMA", 0, 1, LpInteger)
    t = LpVariable("TDMA", 0, 1, LpInteger)

    always1 = LpVariable("Always1", 1, 1, LpInteger)

    # The objective function is added to 'prob' first
    prob += sim_time * (P_base * always1 + Rate * T_tx * (LpAffineExpression(sp_exp) + 2*P_rx*(lpSum(sn)-s) + LpAffineExpression(mpN_exp) + \
                                    LpAffineExpression(mnN_exp) - P_rx*LpAffineExpression(mN_exp))), "Total Energy"

    # Extra Constraint on Total Energy, if needed:
    # prob += sim_time * (P_base + Rate * T_tx * (LpAffineExpression(sp_exp) + 2*P_rx*(lpSum(sn)-s) + LpAffineExpression(mpN_exp) + \
    #                                 LpAffineExpression(mnN_exp) - P_rx*LpAffineExpression(mN_exp))) >= 1735, "XYZ"

    # node constraints
    prob += n["n0"] == 1, "Central Node"
    prob += n["n1"] + n["n2"] >= 1, ""
    prob += n["n3"] + n["n4"] >= 1, ""
    prob += n["n5"] + n["n9"] >= 1, ""
    prob += lpSum(n) <= 6, ""
    prob += lpSum(N) == 1, "Total number of nodes"

    prob += lpSum(n) - 3 <= (1 - N["N3"]) * M, ""
    prob += 3 - lpSum(n) <= (1 - N["N3"]) * M, ""
    prob += lpSum(n) - 4 <= (1 - N["N4"]) * M, ""
    prob += 4 - lpSum(n) <= (1 - N["N4"]) * M, ""
    prob += lpSum(n) - 5 <= (1 - N["N5"]) * M, ""
    prob += 5 - lpSum(n) <= (1 - N["N5"]) * M, ""
    prob += lpSum(n) - 6 <= (1 - N["N6"]) * M, ""
    prob += 6 - lpSum(n) <= (1 - N["N6"]) * M, ""

    prob += s + m == 1, "Routing"
    prob += c + t == 1, "MAC"
    prob += lpSum(p) == 1, "Power level"

    # auxiliary constraints

    # star,power
    for sspp,pp in zip(spIndex,pIndex):
        prob += sp[sspp] <= s, ""
        prob += sp[sspp] <= p[pp], ""
        prob += sp[sspp] >= s + p[pp] - 1, ""

    # star, node
    for ssnn,nn in zip(snIndex,nIndex):
        prob += sn[ssnn] <= s, ""
        prob += sn[ssnn] <= n[nn], ""
        prob += sn[ssnn] >= s + n[nn] - 1, ""

    # mesh, power, reTx
    for mmpN, (pp, NN) in zip(mpNIndex, itertools.product(pIndex, NIndex)):
        prob += mpN[mmpN] <= m, ""
        prob += mpN[mmpN] <= p[pp], ""
        prob += mpN[mmpN] <= N[NN], ""
        prob += mpN[mmpN] >= m + p[pp] + N[NN] - 2, ""

    # mesh, node, reTx
    for mmnN, (nn, NN) in zip(mnNIndex, itertools.product(nIndex, NIndex)):
        prob += mnN[mmnN] <= m, ""
        prob += mnN[mmnN] <= n[nn], ""
        prob += mnN[mmnN] <= N[NN], ""
        prob += mnN[mmnN] >= m + n[nn] + N[NN] - 2, ""

    # mesh, reTx
    for mmN,NN in zip(mNIndex,NIndex):
        prob += mN[mmN] <= m, ""
        prob += mN[mmN] <= N[NN], ""
        prob += mN[mmN] >= m + N[NN] - 1, ""

    # Dummy condition for iterations:
    prob += always1 >= 0, "SolDel"

    # The problem data is written to an .lp file
    prob.writeLP("cplex/HI_lifetime.lp")

    my_prob = cplex.Cplex()
    my_prob.parameters.mip.pool.absgap.set(0)
    my_prob.parameters.mip.pool.intensity.set(4)
    my_prob.parameters.mip.limits.populate.set(1000)
    my_prob.set_log_stream("cplex/cplex.out")                   # output log file for CPLEX
    my_prob.set_error_stream("cplex/cplex.out")
    my_prob.set_warning_stream("cplex/cplex.out")
    my_prob.set_results_stream("cplex/cplex.out")

    iteration = 1
    total_sim_time = 0
    num_sims = 0

    for cntr in range(100):
        my_prob.read("cplex/HI_lifetime.lp")

        my_prob.populate_solution_pool()
        my_prob.solution.pool.write("cplex/HI_lifetime.sol")
        num_sols = my_prob.solution.pool.get_num()
        if num_sols == 0:
            break
        objVal = my_prob.solution.get_objective_value()

        res = {}                    # results for this iteration
        for i in range(num_sols):
            sol_vals = my_prob.solution.pool.get_values(i,["_n0","_n1","_n2","_n3","_n4","_n5","_n6","_n7","_n8","_n9",
                "CSMA","Star","_P1","_P2","_P3"])
            nodes = []
            for j in range(len(nIndex)):
                if sol_vals[j] > 0:
                    nodes.append(j)
            if sol_vals[len(nIndex)] == 1:
                mac = 'CSMA'
            else:
                mac = 'TDMA'
            if sol_vals[len(nIndex)+1] == 1:
                routing = 'Star'
            else:
                routing = 'Mesh'
            if sol_vals[len(nIndex)+2] == 1:
                pw = '-20dBm'
            elif sol_vals[len(nIndex)+3] == 1:
                pw = '-10dBm'
            else:
                pw = '0dBm'
            dickey = str(nodes) + '|' + mac + '|' + pw + '|' + routing

            if inputFileMode:
                res[dickey] = data[dickey]
                total_sim_time += data[dickey][2]
            else:
                if mac == 'CSMA':
                    mac = ',CSMA'
                else:
                    mac = ''
                if routing == 'Star':
                    routing = ',star'
                else:
                    routing = ''
                if pw == '0dBm':
                    pw = ',varyTxPower=\\\"0dBm\\\"'
                elif pw == '-10dBm':
                    pw = ',varyTxPower=\\\"-10dBm\\\"'
                else:
                    pw = ',varyTxPower=\\\"-20dBm\\\"'
                single_res = single_run(nodes, routing, mac, pw, Rate, sim_time)
                res[dickey] = [round(single_res[0]*100, 1), round(single_res[1]), single_res[2]]
                total_sim_time += single_res[2]
            num_sims += 1

        res_sorted = sorted(res.items(), key=lambda e: (e[1][1], -e[1][0]))
        print(res_sorted)
        for i in range(len(res_sorted)):
            if res_sorted[i][1][0] >= PDRmin:
                print('Found the answer in iteration ' + str(iteration) + ': ' + str(res_sorted[i]) + '\nTotal time: ' + str(total_sim_time/3600) + ' hrs')
                return [PDRmin, res_sorted[i], iteration, total_sim_time, num_sims]
        print('Not found in iterration ' + str(iteration))
        iteration += 1

        # Now add the current objVal as a constraint:
        del prob.constraints["SolDel"]
        prob += sim_time * (P_base + Rate * T_tx * (LpAffineExpression(sp_exp) + 2*P_rx*(lpSum(sn)-s) + LpAffineExpression(mpN_exp) + \
                                        LpAffineExpression(mnN_exp) - P_rx*LpAffineExpression(mN_exp))) >= objVal+1, "SolDel"
        # The problem data is written to an .lp file
        prob.writeLP("cplex/HI_lifetime.lp")

opt_solution = hi_solver(PDRmin)
print('PDRmin, res, iterate, tot_time(s), n_sims')
print(opt_solution)

# # if want to run the whole optimizer for different values of PDRmin:
# pdr_sweep = []
# for PDRmin in np.arange(50,100.1,0.5):
#     pdr_sweep.append(hi_solver(PDRmin, data))
# print('PDRmin, res, iterate, tot_time, n_sims')
# print(pdr_sweep)
#
# text_file = open('pdr_sweep.txt', "w")
# for i in range(len(pdr_sweep)):
#     text_file.write(str(pdr_sweep[i])+'\n')
# text_file.close()
