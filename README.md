<div align="center"> 
  <img src= "https://github.com/New-Jersey-Forest-Service/ForMOM/assets/101826099/8dde7d22-1bbb-470e-a368-b3bde741ccaa" />
</div>

<h1 align="center"> ForMOM </h1>
Forest Management Optimization Model

A set of tools to optimize forest management for carbon, presently 
being developed to assess practices in the state of New Jersey. 

The ForMOM project is possible due to the combined effort of many NJFS 
employees. This project is organized by Bill Zipse, and has been the 
consistent work of Lauren Gazerwitz, Courtney Willitts, Michael Gorbunov, Ben 
Pisano, Bernie Isaacson & Justin Gimmillaro, with participation from Mike 
Hart, Rosa Yoo & Jason Grabowsky (Rutgers University).

The FIADB re-organization work was primarily accomplished by Lauren 
Gazerwitz, the FVS work was primarily accomplished by Courtney Willitts, 
Bernie Isaacson, and Justin Gimmillaro, and the data processing and building 
of visuals was primarily completed by Bernie Isaacson and Ben Pisano. The 
development of the database automation process, the constraint builder, and 
the .csv to .dat converter were completed by Michael Gorbunov.

If you have 
questions specifically about the software
here, please reach out at [William.Zipse@dep.nj.gov](William.Zipse@dep.nj.gov).



# Project Overview

Roughly speaking there are two steps in the process of forest management optimization.
 
 - **Step 1**: Simulate different management scenarios for different forest types
 - **Step 2**: Add constraints and optimize to find the optimal management

The simulation of forest management is done primarily with FVS. We take the state inventory 
from FIA, re-organize it into distinct forest types, and then run it through FVS.

Most of the code in this repository is to assist with step 2. After getting values from FVS,
we write constraints using a custom program for constraint building. The constraints
are then aggregated and the linear optimization problem is solved using Pyomo, a python package.

The optimization software is for optimization, not carbon optimization. It can be used for any
optimization problem.


## Step 1 - Simulating Managements

Before optimizing managements, we simulate them. We take state data from FIA, re-organize it by forest type and year, and run it through FVS.
The FVS runs are not in this repository. but the tool we use to re-organize the database are located in
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

The ForMOM Project maintains three pieces of software

 - [ForMOM DB Reformatter](https://github.com/New-Jersey-Forest-Service/ForMOM-DBReformatter) - for simplifying FIADB data
 - [ForMOM Builder](https://github.com/New-Jersey-Forest-Service/ForMOM-Builder) - for building constraints and models
 - [ForMOM Runner](https://github.com/New-Jersey-Forest-Service/ForMOM-Runner) - for running linear optimization models

Each of them live in their own repo, which are linked in the above bullet points. Additionally, you find info on the Wiki.

