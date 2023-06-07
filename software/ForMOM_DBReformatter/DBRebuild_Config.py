'''
DBRebuild Config

This file is meant to be edited by the user, and affects how the program is run.

There are example configs in the example-configs folder.
'''

# Path to the database file
DB_FILEPATH = './FIADB_NJ.db'

# Name of the file (should be the end of DB_FILEPATH)
DB_NAME = 'FIADB_NJ.db'

# What years to keep; years not in list will be discarded
INV_YEARS = [2015, 2016, 2017, 2018, 2019, 2020]

# Describes how to split large forest types using
# county codes; see wiki or other examples for more detail
COUNTY_SPLIT_DICT = {
	'167': {
		'167N': [23, 25, 29, 1, 19],
		'167S': [5, 7, 15, 11, 9]
	}
}


