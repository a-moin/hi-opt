#***************************************************************************#
#   Copyright (c) 2016 - 2017, University of California, Berkeley.          #
#                                                                           #
#   Author(s):  Ali Moin, EECS Department, UC Berkeley.                     #
#               Pierluigi Nuzzo, EE Department, USC.                        #
#                                                                           #
#   This file is distributed under the terms in the attached LICENSE file.  #
#***************************************************************************#


# Generates all possible node combinations based on topological constraints

import cplex
# Import PuLP modeler functions
from pulp import *
import pylab
import itertools

# Create the 'prob' variable to contain the problem data
prob = LpProblem("HI Lifetime", LpMinimize)

# The variables
nIndex = ["n0", "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9"]       # nodes
n = LpVariable.dicts("", nIndex, 0, 1, LpInteger)
d = LpVariable("dummy", 0, 1, LpInteger)

prob += d, ""

# node constraints
prob += n["n0"] == 1, "Central Node"
prob += n["n1"] + n["n2"] >= 1, ""
prob += n["n3"] + n["n4"] >= 1, ""
prob += n["n5"] + n["n9"] >= 1, ""
prob += lpSum(n) <= 6, ""

prob.writeLP("node_comb.lp")

my_prob = cplex.Cplex()
my_prob.read("node_comb.lp")

my_prob.parameters.mip.pool.absgap.set(0)
my_prob.parameters.mip.pool.intensity.set(4)
my_prob.parameters.mip.limits.populate.set(1000)
my_prob.populate_solution_pool()
my_prob.solution.pool.write("node_comb.sol")
num_sols = my_prob.solution.pool.get_num()

all_combs = []

for i in range(num_sols):
    sol_vals = my_prob.solution.pool.get_values(i, ["_n0", "_n1", "_n2", "_n3", "_n4", "_n5", "_n6", "_n7", "_n8", "_n9"])
    nodes = []
    for j in range(len(nIndex)):
        if sol_vals[j] == 1:
            nodes.append(j)
    all_combs.append(nodes)

print(len(all_combs))

eachN = [0]*3
print(all_combs)
for x in all_combs:
    if len(x) == 4:
        eachN[0] += 1
    if len(x) == 5:
        eachN[1] += 1
    if len(x) == 6:
        eachN[2] += 1
print(eachN)