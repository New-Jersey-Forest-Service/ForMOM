# ForMOM
Forest Management Optimization Model

A set of tools to optimize forest management for carbon, presently 
being developed to assess practices in the state of New Jersey. 

This repository is maintained mostly by Michael Gorbunov. If you have questions specifically about the software
here, please reach out at [michael.gorbunov@nj.dep.gov](michael.gorbunov@nj.dep.gov).

However, the entire project is a team effort. ForMOM is organized by Bill Zipse, and has been 
the work of
Lauren Gazerwitz, Courtney Willits, Michael Gorbunov, Bernhard Isaacson, Benjamin Pisano, and Justin Gillmaro.
We've had great input from others - Jason Grabosky, Rosa Yoo, Michael Hart just to name a few.

A majority of the FVS work was done by Courtney, Lauren, and Justin. Bernie (Bernhard) and Ben have helped processing
the data and building visuals.


# Project Overview

Roughly speaking there are two steps in the process of forest management optimization.
 
 - **Step 1**: Simulate different management scenarios for different forest types
 - **Step 2**: Add constraints and optimize to find the optimal management

The simulation of forest management is done primarily with FVS. We take the state inventory 
from FIA, simplify it into distinct forest types, and then run it through FVS.

Most of the code in this repository is to assist with step 2. After getting values from FVS,
we write constraints using a custom program for constraint building. The constraints
are then aggregated and the linear optimization problem is solved using Pyomo, a python package.

The optimization software is for optimization, not carbon optimization. It can be used for any
optimization problem.


## Step 1 - Simulating Managements

Before optimizing managements, we simulate them. We take data from FIA, simplify it, and run it through FVS.
The FVS runs are not in this repository. but the tool we use to rebuild the database are located in
[src/fvs/input](https://github.com/New-Jersey-Forest-Service/ForMOM/tree/main/src/fvs/input). For information
on running it, look to the [wiki page about it](https://github.com/New-Jersey-Forest-Service/ForMOM/wiki/FVS#inputs).

The final output tells us how much carbon is sequestered by forest type, by year, by management. These values give
us the objective function.



## Step 2 - Linear Optimization

With an objective function ([here's an example old one](https://github.com/New-Jersey-Forest-Service/ForMOM/blob/dev-optimization/src/optimization/constraint_builder/sample_data/minimodel_obj.csv)) 
from FVS simulations, we need to build constriants and run the model. Constraint building is done with the custom written **Constraint Builder**.
It allows for easier setting up of problems with 100s of variables and constraints. Once constraints are built, the model can be run.

The process of running the model is currently... not ideal. There are a lot of intermediate data formats, and over or under constrained
setups are difficult to debug. The constraint builder program will give you a csv containing the actual matrix of the linear optimization
problem. This file, along with the objective file get turned into a .dat file by the [csvToDat program](https://github.com/New-Jersey-Forest-Service/ForMOM/tree/dev-optimization/src/optimization/convert_to_dat). Then you can feed this .dat straight into the [pyomo runner](https://github.com/New-Jersey-Forest-Service/ForMOM/blob/dev-optimization/src/optimization/pyomo/PyomoOptimizer.py).

Doing that once would be ok, but to debug the model it's easier to modify the constraint csv, which means re-converting to .dat. The developers
are aware this is an issue.


# Runnable Software



## DBRebuild
Command Line Utility, Located on main in [src/fvs/input](https://github.com/New-Jersey-Forest-Service/ForMOM/tree/main/src/fvs/input).

![20Week_DBRebuild](https://user-images.githubusercontent.com/49537988/178081051-e70ae0e2-faeb-45b7-9502-6a4190c1dbf1.png)

This program takes a raw sqlite3 database from FIA Datamart and simplifies it to be run through FVS more
simply. We have it setup for New Jersey, but it is configurable for other states - there are example configs for MD and WY.
Check out the [wiki page](https://github.com/New-Jersey-Forest-Service/ForMOM/wiki/FVS#inputs) for more information on running it.

**Credits**: The actual simplification process was thought of and developed by Lauren and Courtney, it was only automated by Michael.



## Constraint Builder
GUI Application, Located on dev-optimization branch in [src/optimization/constraint_builder](https://github.com/New-Jersey-Forest-Service/ForMOM/tree/dev-optimization/src/optimization/constraint_builder). The file to run is src/launchgui.py.

![19Week_TwosidedConstrs_Smol](https://user-images.githubusercontent.com/49537988/178080432-701964e5-15b7-4950-bfb8-081804732d44.png)

This program is a generic tool to build constraints. As input you give it an [objective function](https://github.com/New-Jersey-Forest-Service/ForMOM/blob/dev-optimization/src/optimization/constraint_builder/sample_data/minimodel_obj.csv) 
in csv format, and it scrapes the variable names. These variables names are expected to be structured with seperators, eg: '167N_2021_SBNP' has three
tags, '167N', '2021', 'SBNP'. You could for example have a constriant with all variables involving '167N' because it processes with the tags.

The program is under development so there is no usage guide yet. 
**If you want a usage guide or demo**, please don't hesitate to reach out to me at 
[michael.gorbunov@dep.nj.gov](mailto:michael.gorbunov@dep.nj.gov).
You can try it yourself by running launchgui.py and using one of the files in the sample_data folder.

**Credits**: All development by Michael Gorbunov, but a lot of good 
feedback and ideas came from others on the team - specifically Bill, Bernie, and Courtney



## CSV to Dat
GUI Application, Located on dev-optimization branch in [src/optimization/convert_to_dat](https://github.com/New-Jersey-Forest-Service/ForMOM/tree/dev-optimization/src/optimization/convert_to_dat). The file to run is csv_to_datGUI.py

![20Week_CSVToDat](https://user-images.githubusercontent.com/49537988/178082801-357ac544-3d1a-42dd-bb92-abad91ca7347.png)

This program takes two csvs specifying constraints and the objective file, and produces a .dat file.

If the constraint builder were fully fleshed out, this program would be unnecessary, so this will eventually be pruned from the project.

**Credits**: The original csv format was made by Bill, and the converter was written by Michael


## Dependencies

Python version must be >= 3.6.
It was developed in 3.8.0, so if there are issues
use that.

Python dependencies can be found in py_requirements.txt.




