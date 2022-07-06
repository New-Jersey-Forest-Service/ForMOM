# Constraint-o-Matic
# 2022-05-11
# Bernard Isaacson

# values are acres
# rows are types
# columns are mgmt types
# dimension 3 are years
# dimension 4 public/privateSTEW/privateNOSTEW
# pub, pSTEW, nSTEW
# startvalues are table of acreages by forest types in 2021
# dev acres is # per year

# DEV col is elapsed years * forest type acres/total acres * dev acres 
# ASV is only in years 2021,2025,2030 
# ASV occurs only on pSTEW 

## mgmt types:
# DEV - conversion
# IFM - improved forest mgmt
# AWR - awc restoration
# THN - thinning
# AFF - afforestation
# INV - invasive mgmt
# lookup the    

# years:
# 2021,2025,2030,2050

# constraints: 
# constraint name is row.col.year.pub
# each row in each dim3 must be EQ to rowsum in [i,,1,]  # you cant have more acres in a type than there are in the first year
# sum[TYPE,,allyears,] must EQ n.years          # you cant have more acres than there are 

# ----- dev ----- #
# development in [,,,1] is set to hard 0 (public land)  # you cant have development on public land
# development can only come from [,,,2:3]  (ALL private land) # development can only occur on private land

# ----- thin ----- #
# sum[,THN,year,] must be LTE sum[TYPE,,year,]  # you cant thin more acres than there are in a year
# [TYPE,THN,year,] must be LTE sum[TYPE,year]   # you cant thin more than the acres in the type for the year
# hard 0 - no thinning in the northern hardwoods or awc type

# ----- cedar ----- # 
# sum[(possible cedar types),AWR,year,] must be LTE sum[(possible cedar types),,year,] 
# you cant restore more acres of cedar than there are candidate acres
#  maple-hardwood swamp and nonstocked 
#  sum of the [,AWR,last year,] is total number of cedar acres
# [Maple Hardwood Swamp,AWR,year,] must be LTE some fraction (0.1?) times the [Maple Hardwood Swamp,,year,]
# [Nonstocked,AWR,year,] must be LTE some fraction (0.1?) times the [Nonstocked,,year,]

# ----- INV ----- #
# you cant treat invasives on more acres than there are in each of the types
# [maple beech birch,INV,year,] must be LTE sum [(possible INV types),,year,] 
# [NRO,INV,year,] must be LTE sum [(possible INV types),,year,]
# [Type,INV,year,] must be LTE total or that type 
#   we're not going to treat more than a fraction of a type within a year

# ----- IFM ----- # 
# ----- AFF ----- # 
# no significant afforestation on private lands

# carbon per acre table
# mgmt by 