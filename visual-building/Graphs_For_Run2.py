import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd

import os
from typing import List
from pathlib import Path
from plotnine import *


# # Reading Pyo Output File
# The raw output from Pyomo is stored in a text file, so we transform it into a dataframe

# In[88]:


#
# This block reads text from the file into lists, converting lines seperated with
# a '|' into entries of lists
#
# eg: 'TotalAcerage    | 24324.0' => ['TotalAcerage', 24324.0]
#

raw_file = Path('C:/sfs/GitHub/ForMOM/minimodel-running/run2/rawPyoOut_MiniModel2_FirstRun.txt')

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
#remove rows with 0 in acres
df_cmb = df_cmb.loc[df_cmb['acres'] != 0]

# TODO: Convert other lists into dataframes
dfshadowprice = None

dfslackge = None

dfslackle = None



dfvars

#%%
# # Making Visuals
# Now with a dataframe, lets make some visuals

#create stacked bars grpahs
#forest type over time
# =============================================================================
# dfvars['year'] = dfvars['year'].astype(str)
# dfvars.dtypes
# (ggplot(dfvars,aes('year', 'acres', fill = 'for_type'))
#  + geom_col()
#  + ggtitle("Forest Type Acres Over Time")
# )
# 
# 
# # mng over time
# (ggplot(dfvars,aes('year', 'acres', fill = 'mng'))
#  + geom_col()
#  +ggtitle("Management Acres Over Time")
# )
# =============================================================================

#%%
# create unique dataframes for each year in model
#change year to int64
# =============================================================================
# df_cmb.dtypes
# df_cmb['year'] = pd.to_numeric(df_cmb['year'])
# df_cmb.dtypes
# 
# #create year specific dataframes
# df_cmb2021 = df_cmb.loc[df_cmb['year'] == 2021]
# df_cmb2025 = df_cmb.loc[df_cmb['year'] == 2025]
# df_cmb2030 = df_cmb.loc[df_cmb['year'] == 2030]
# df_cmb2050 = df_cmb.loc[df_cmb['year'] == 2050]
# 
# #create lists from columns if lists are needed for visuals
# years = df_cmb['year'].tolist()
# for_type = df_cmb['for_type'].tolist()
# acres = df_cmb['acres'].tolist()
# mng = df_cmb['mng'].tolist()
# 
# =============================================================================
#%%

#create sunburst plot with plotly
# sunburst hierarchy: year>forest type>management>acres as value
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
from plotly.graph_objs import *
init_notebook_mode()
fig = px.sunburst(data_frame = df_cmb, path=['year', 'for_type','mng'],values='acres',hover_data=['acres'],maxdepth=-1,width=1000,height=800,color_discrete_sequence=px.colors.qualitative.Dark24)
plot(fig)

#%% create tree diagrams

figtm = px.treemap(df_cmb, path=['year', 'for_type','mng'], values='acres')
figtm.update_traces(root_color='lightgrey')
figtm.update_layout(margin = dict(t=50, l=25, r=25, b=25))
plot(figtm)

