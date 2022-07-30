#!/usr/bin/env python
# coding: utf-8

# In[364]:


import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd

import os
from typing import List
from pathlib import Path
from plotnine import *
import squarify
#from plotnine.data import * use this for sample data with ggplot2

np.random.seed(444)


# # Reading Pyo Output File
# The raw output from Pyomo is stored in a text file, so we transform it into a dataframe

# In[88]:


#
# This block reads text from the file into lists, converting lines seperated with
# a '|' into entries of lists
#
# eg: 'TotalAcerage    | 24324.0' => ['TotalAcerage', 24324.0]
#

raw_file = Path('C:/sfs/GitHub/ForMOM/MiniModelRunning/run2/rawPyoOut_MiniModel2_1Development.txt')

# All 4 lists look like [['167N_2021_PLSQ', 221277.0], ... ]
vars_list = []
shadowprice_list = []
slackge_list = []
slackle_list = []

list_map = {
    '== Variables': vars_list,
    '== Shadow Prices': shadowprice_list,
    '== Slacks for GE': slackge_list,
    '== Slacks for LE': slackle_list
}

with open(raw_file, 'r') as f:
    EOF = ''
    
    read_data = False
    active_list = None
    
    line = 'not EOF'
    while line != EOF:
        line = f.readline()
        stripped = line.strip()

        # Check if we have a new section
        if stripped in list_map.keys():
            read_data = True
            active_list = list_map[stripped]
            
        # Check if we're at the end of a section
        elif stripped == '':
            read_data = False
        
        # Write data if we're within a data section
        elif read_data:
            splitline = line.split("|")
            splitline[0] = splitline[0].strip()
            splitline[1] = float(splitline[1])
            active_list.append(splitline)


# In[134]:


#
# Now we convert the lists into dataframes
#


# Convert the variable list into a dataframe
dfvars = pd.DataFrame(vars_list)
dfvars.columns = ['varname', 'acres']

# This line removes all variables without 3 components seperated by '_'
# this is meant for the dummy variables
badnames = dfvars[dfvars['varname'].map(
    lambda x: len(x.split('_')) != 3
)]
dfvars = dfvars.drop(badnames.index)

# The varname column is now split in 3 based on the '_'
# See: https://stackoverflow.com/questions/37333299/splitting-a-pandas-dataframe-column-by-delimiter
dfvars[['for_type', 'year', 'mng']] = dfvars['varname'].str.split('_', expand=True)
dfvars = dfvars.drop(columns='varname')

# Set the variables as indexes
dfvars_index = dfvars.set_index(['for_type', 'year', 'mng'])

# create a dataframe with forest type and mng together in a column
df_cmb = dfvars
df_cmb["fortype_mng"] = df_cmb['for_type'].astype(str) + "_" + df_cmb['mng']

# TODO: Convert other lists into dataframes
dfshadowprice = None

dfslackge = None

dfslackle = None



dfvars

#%%
# # Making Visuals
# Now with a dataframe, lets make some visuals

# stacked bars
#forest type over time
dfvars['year'] = dfvars['year'].astype(str)
dfvars.dtypes
(ggplot(dfvars,aes('year', 'acres', fill = 'for_type'))
 + geom_col()
 + ggtitle("Forest Type Acres Over Time")
)



# mng over time
(ggplot(dfvars,aes('year', 'acres', fill = 'mng'))
 + geom_col()
 +ggtitle("Management Acres Over Time")
)

#%%
# pull out year df's from df_cmb to create tree maps for each year
#change year to int64
df_cmb.dtypes
df_cmb['year'] = pd.to_numeric(df_cmb['year'])
df_cmb.dtypes
#remove rows with 0 in acres
df_cmb = df_cmb.loc[df_cmb['acres'] != 0]
#create year specific dataframes
df_cmb2021 = df_cmb.loc[df_cmb['year'] == 2021]
df_cmb2025 = df_cmb.loc[df_cmb['year'] == 2025]
df_cmb2030 = df_cmb.loc[df_cmb['year'] == 2030]
df_cmb2050 = df_cmb.loc[df_cmb['year'] == 2050]





# create tree maps
#2021
squarify.plot(sizes=df_cmb2021['acres'], label=df_cmb2021['fortype_mng'], alpha=.8)
plt.axis('off')
plt.show()

#create sunburst
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
from plotly.graph_objs import *
#create lists from columns
years = df_cmb['year'].tolist()
for_type = df_cmb['for_type'].tolist()
acres = df_cmb['acres'].tolist()
mng = df_cmb['mng'].tolist()


fig = px.sunburst(data_frame = df_cmb, path=['year', 'for_type','mng'],values='acres',hover_data=['acres'],maxdepth=-1,width=1000,height=800,color_discrete_sequence=px.colors.qualitative.Dark24)
plot(fig)

# In[334]:


year_list = dfvars.index                     .droplevel(['mng', 'for_type'])                     .unique()                      .astype(int)                     .to_list()
year_list.sort()
year_list_str = [str(x) for x in year_list]
year_list


# In[367]:


fortype_list = dfvars.index                     .droplevel(['mng', 'year'])                     .unique()                     .astype(str)                     .to_list()
fortype_list.sort()
fortype_list


# In[399]:


mng_list = dfvars.index                 .droplevel(['for_type', 'year'])                 .unique()                 .astype(str)                 .to_list()
mng_list.sort()
mng_list


# ### Figure 1 - Management by Forest Type over Time

# In[398]:


WIDTH = 0.65
fig, ax = plt.subplots(ncols=1, nrows=len(fortype_list), figsize=(8, 30))

for ind, ft in enumerate(fortype_list):
    df_ft = dfvars.loc[ft]
    
    #
    # Step 1: Pull out data
    
    # I gave up trying to find a more pythonic / pandas friendly way to do
    # all this. What I did here is definitely not ideal
    loc_mnglist = df_ft.index.droplevel(['year']).unique().to_list()
    list_dict  ={}
    for mng in loc_mnglist:
        list_dict[mng] = []
    
    for year in year_list:
        dfyr = df_ft.loc[str(year)]
        for mng in loc_mnglist:
            list_dict[mng].append(float(dfyr.loc[mng]['acres']))
    
    #
    # Step 2: Draw Graph
    ft_ax = ax[ind]
    
    bottoms = [0] * len(list_dict[loc_mnglist[0]])
    for mng in loc_mnglist:
        series = list_dict[mng]
        ft_ax.bar(year_list_str, series, WIDTH, label=mng, bottom=bottoms)
        bottoms = [bottoms[i] + x for i, x in enumerate(series)]
    
    ft_ax.set_title(f'{ft} over time')
    ft_ax.legend(bbox_to_anchor=(1, 0.5), loc='center left')
    ft_ax.set_ylabel('Total Acres')
    ft_ax.set_xlabel('Year')
    
    # This adds commas to big numbers, '10000' => '10,000'
    # See: https://stackoverflow.com/questions/25973581/how-do-i-format-axis-number-format-to-thousands-with-a-comma-in-matplotlib
    ft_ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))


# ### Figure 2 - Acres of Forest Types Over Time

# In[431]:


fig, ax = plt.subplots()

# Yea... I give up trying to use Pandas for now
varsdict = dfvars.to_dict()


# In[ ]:




