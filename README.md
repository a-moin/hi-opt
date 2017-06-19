# hi-opt: Human Intranet Optimization Platform

## Requirements
- Castalia Network Simulator; available at: https://github.com/boulis/Castalia
	- Castalia is based on OMNeT++ simulator, so you need to install it first as discussed in Castalia's installation manual.
	- The current version of Castalia only works with OMNeT's older version 4.x (been tested with 4.6).
- Python
- Pulp LP modeler Python package; available at: https://pypi.python.org/pypi/PuLP
- IBM ILOG CPLEX Optimization Studio with its Python API

## Installation
- Install Castalia, Python, Pulp, and CPLEX.
- The following folders should be added to the default Castalia installation. You can either replace the whole "Castalia-3.2" folder with the one provided in this repo, or copy only these folders if you already had Castallia installed with your own settings:
	- Castalia-3.2/src/node/application/hiMesh
	- Castalia-3.2/src/node/application/hiStar
	- Castalia-3.2/src/node/communication/mac/hiTdmaMac 
	- Castalia-3.2/out/gcc-release/src/node/application/hiMesh 
	- Castalia-3.2/out/gcc-release/src/node/application/hiStar 
	- Castalia-3.2/out/gcc-release/src/node/communication/mac/hiTdmaMac 
	- Castalia-3.2/Simulations/HIBAN 
	- Castalia-3.2/Simulations/Parameters/Radio/CC2650.txt 

## Package Structure
- **`all_cases_run.py`**: Running this script generates the results for all feasible cases, and saves them in a file (`all_results.txt`).
- **`anneal.py`**: Simulated annealing algorithm for comparison (package available at https://github.com/perrygeo/simanneal)
- **`configs.py`**: Main configurations to be set by user.
- **`exhaustiveSearch.py`**: Reads all cases from `all_results.txt`, sorts them, and prints the optimized results for each PDRmin.
- **`funcs.py`**: Miscellaneous internal functions for running simulations and calculating statistics.
- **`main.py`**: Main optimization algorithm.
- **`patloss.py`**: The average path loss values can be changed here. The script generates the requierd `pathLossMap.txt` for Castalia for each simulation run.

## Running Optimization
- Open `configs.py` and specify the following parameters:
    - **castalia_path**: Your Castalia's installation path.
    - **PDRmin**: Minimum PDR constraint.
    - **inputFileMode**: There are two modes for running the optimizer:
        - ***inputFileMode = False***: The full algorithm will be run with the required simulations. This can take a long time depending on the input constraints.
        - ***inputFileMode = True***: This mode is useful when you want to try different constraints on the same problem. In this case, you have to first run `all_cases_run.py` script which simulates all feasible cases and saves them in `all_results.txt`. This will take a very long time. However, the optimization algorithm will look up through this file from now on instead of running simulations each time. **Note**: `all_results.txt` is provided to you for the sample problem discussed in the paper, so you don't need to run `all_cases_run.py` for that problem.
- Run `main.py`. The optimal solution would be printed on the screen.
 
## Problems?
If you face any problems or discover any bugs, please let us know: *MyLastName AT berkeley DOT edu*

For more info, you can read and cite our paper:

**A. Moin, P. Nuzzo, A. L. Sangiovanni-Vincentelli, and J. M. Rabaey, "Optimized Design of a Human Intranet Network," 2017 54th ACM/EDAC/IEEE Design Automation Conference (DAC), Austin, TX, 2017.**
