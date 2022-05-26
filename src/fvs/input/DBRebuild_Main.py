'''
DBRebuild Main

This program takes a raw FIA database and makes it compatabile with FVS.

Michael Gorbunov (Automated manual process by Lauren)
Lauren Gazerwitz (Figured out how to make FVS accept the datatbase)

NJDEP
04/2022
'''

# TODO:
# [~] Handle Malformed DB
#  - [x] Check that all tables needed are found
#  - [ ] Never index into elements without checking their length
# [ ] Cleaner SQL
#  - Run everything through an auto-formatter
# [x] Better Feedback
#  - [x] Debug progress of queries to console
#  - [x] Condense feedback for table deletion
#  - [ ] Add those cool progress bars that pip install uses
# [x] Actually get county counts
#  - This would be helpful on a national scale but 
#    I think it's a little too much effort right now
# [ ] Ask about creating a new DB at the beginning
# [ ] Lint the passed county dict

import sqlite3
import re
import sys
import DBRebuild_StandID as dbStandID


# State Specific Configuration
DB_FILEPATH = './FIADB_NJ.db'
DB_NAME = 'FIADB_NJ.db'
INV_YEARS = [2015, 2016, 2017, 2018, 2019, 2020]
COUNTY_SPLIT_DICT = {
	'167': {
		'167N': [23, 25, 29, 1],
		'167S': [5, 7, 15, 11, 9]
	}
}



# FIA Specific Configuration - These are specified by the programmer
DEFAULT_DB_REGEX = r'FS_FIADB_STATECD_\d{2,2}\.db'
FVS_MAX_TREES = 3000
TABLES_TO_KEEP = [
	'COND', 
	'COUNTY', 
	'FVS_GROUPADDFILESANDKEYWORDS',
	'FVS_PLOTINIT_PLOT',
	'FVS_STANDINIT_PLOT',
	'FVS_TREEINIT_PLOT',
	'PLOT',
	'POP_STRATUM',
	'REF_FOREST_TYPE',
	'REF_FOREST_TYPE_GROUP',
	'REF_SPECIES',
	'SEEDLING',
	'TREE'
]
# Convert to a string for easier formatting
INV_YEARS = [str(x) for x in INV_YEARS]


def main():
	global DB_FILEPATH

	db_con = sqlite3.connect(DB_FILEPATH)
	cur = db_con.cursor()

	print(" [[ STARTING ]] ")

	print()
	print("Deleting tables")
	delete_extra_tables_and_check_for_all_expected_ones(cur)

	print()
	print("Creating tables with specific inventory years")
	create_inventory_year_tables(cur)

	print()
	print("Updating groupaddfilesandkeywords")
	update_groupaddfilesandkeywords(cur)

	print()
	print("Generating County Counts")
	county_count_dict = dbStandID.get_num_fortypes_by_county(
		cur, 
		'FVS_TREEINIT_PLOT_INVYEARST', 
		COUNTY_SPLIT_DICT
	)

	print()
	print("Doing ID Replace")
	dbStandID.do_id_replace(cur, COUNTY_SPLIT_DICT)

	print()
	print("Running command block 2")
	run_script(cur, './commandblock2.sql')

	print()
	print("Checking for large stands")
	check_for_large_stands(cur, county_count_dict)

	print()
	print(" [[ FINISHED ]] ")

	db_con.commit()
	db_con.close()


def run_script(cur: sqlite3.Cursor, path: str) -> None:
	with open(path, 'r') as f:
		cur.executescript(f.read())



#
# Steps 1 -3
# 
# Deleting Tables, Creating Tables, Editing groupaddfilesandkeywords
#

def delete_extra_tables_and_check_for_all_expected_ones(cur: sqlite3.Cursor) -> None:
	'''
		Deletes all tables except for a couple specified ones.
		It will also terminate the program if a specified table is not found.
	'''
	sql_gettables = "SELECT name FROM sqlite_master WHERE type='table'"
	cur.execute(sql_gettables)
	all_tables = [str(x[0]) for x in cur.fetchall()]
	tables_not_found = [x for x in TABLES_TO_KEEP] # Creates copy by value

	num_removed = 0
	num_kept = 0

	for ind, table in enumerate(all_tables):
		if table in TABLES_TO_KEEP:
			num_kept += 1
			tables_not_found.remove(table)
		else:
			num_removed += 1
			cur.execute(f"DROP TABLE {table}")

		if ind % 10 == 0 and ind != 0:
			print(" > Processed 10 tables")

	print(f" > Removed {num_removed} tables and kept {num_kept} tables")
	
	if len(tables_not_found) > 0:
		print(f" > [[ WARNING ]]")
		print(f" > \tDid not find expected tables {','.join(tables_not_found)}")
	else:
		print(f" > Found all expected tables and removed unnecessary ones")

	print()


def create_inventory_year_tables(cur: sqlite3.Cursor) -> None:
	got_to_end = False

	with open('./commandblock1.sql', 'r') as f:
		entire_script = f.read()
		entire_script = entire_script.replace(
			"$$INVENTORY_YEARS$$", 
			", ".join(INV_YEARS)
		)
		cur.executescript(entire_script)
		got_to_end = True
	
	if not got_to_end:
		err_and_exit("Unable to create inventory year tables")

	print(f" > Succesfully created tables for years {', '.join(INV_YEARS)}")
	


def update_groupaddfilesandkeywords(cur: sqlite3.Cursor) -> None:
	TABLE_NAME = 'FVS_GROUPADDFILESANDKEYWORDS'

	# Rename All_FIA_Plots to All_FIA_ForestTypes
	cur.execute(f'''
		UPDATE {TABLE_NAME}
		SET GROUPS = 'All_FIA_ForestTypes' WHERE GROUPS = 'All_FIA_Plots'
		''')

	# Now we have three rows, named 'All_FIA_Conditions', 'All_FIA_ForestTypes', and 'All_FIA_Subplots'
	# There's a column 'FVSKEYWORDS' that is basically a script and it needs some updating
	groups = ['All_FIA_Conditions', 'All_FIA_ForestTypes', 'All_FIA_Subplots']

	for group in groups:
		cur.execute(f'''
			SELECT FVSKEYWORDS FROM {TABLE_NAME} 
			WHERE GROUPS = '{group}'
			''')
		fvskeywords = str(cur.fetchall()[0][0])

		fvskeywords = re.sub(DEFAULT_DB_REGEX, DB_NAME, fvskeywords)	
		fvskeywords = re.sub("_CN =\s?'%Stand_CN%'", "_ID = '%StandID%'", fvskeywords)
		
		cur.execute(f'''
			UPDATE {TABLE_NAME}
			SET FVSKEYWORDS = "{fvskeywords}" WHERE GROUPS = '{group}'
			''')


#
# Step 6
#
# Checking for particularly large stands (> 3000)
#

def check_for_large_stands(cur: sqlite3.Cursor, county_count_dict: dict) -> None:
	trees_in_stand = '''
		SELECT STAND_ID, COUNT(*) AS AMNT 
		FROM FVS_TREEINIT_PLOT 
		GROUP BY STAND_ID'''
	cur.execute(trees_in_stand)

	large_standids = []
	for row in cur:
		standid = row[0]
		numtrees = row[1]

		if (numtrees >= FVS_MAX_TREES):
			large_standids.append(standid)
	
	if len(large_standids) > 0:
		print(f" > [[ Warning ]]")
		print(f" > \tStand IDs {', '.join(large_standids)} have {FVS_MAX_TREES}+ entries in FVS_TREEINIT_PLOT.")
		print(f" > \tConsider splitting up by county codes")
	
	for for_type in large_standids:
		county_codes = list(county_count_dict[for_type].keys())
		county_codes.sort()
		print(f" > [[ Info ]]")
		print(f" > County distribution for {for_type}")

		total = 0
		for county in county_codes:
			amnt = county_count_dict[for_type][county]
			print(" > %4d | %d" % (county, amnt))
			total += amnt
		print(f" >  tot | {total}")



def err_and_exit(err: str) -> None:
	print(f'\t[[ Error ]]\n{err}')
	print(f'Now aborting')
	sys.exit(1)


if __name__ == '__main__':
	main()

