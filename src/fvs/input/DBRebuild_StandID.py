'''
This script generates the Replace_ID tables that are needed to swap out
the FIA IDs with stand IDs for FVS.

It will actually modify the database, so there is no need for 
extra csvs, etc.

Note, this script does not create duplicate tables 'IDReplace'

Michael Gorbunov
"FVSStandID.ipynb" by Bill Zipse was used as reference
'''

import sqlite3
import sys

# TODO: Less magic numbers
#   - [ ] Somehow explain or derive the 7
# TODO: Less magic names
#	- [ ] Use dataclases or attrs classes instead of dicts
# TODO: Better integration
#	- [ ] Rewrite the structs to use cur.executemany()

def parse_as_int_if_valid(float_str: str) -> int:
	try:
		float(float_str)
		return int(float(float_str))
	except:
		return -1


def extract_forest_types(cur: sqlite3.Cursor, tables: list, county_split_dict: dict):
	# creates a map from STAND_CN (int) -> for_type (str)
	stand_fortype_map = {}

	fortypes_to_split = list(county_split_dict.keys())

	for table_name in tables:
		query = f'SELECT GROUPS, STAND_CN, COUNTY FROM {table_name}'
		cur.execute(query)

		for row in cur:
			stand_cn = int(row[1])

			str_groups = str(row[0]).split(" ")
			FOR_TYPE_IND = 7
			# This is making a lot of assumptions about the db :(
			for_type = str(str_groups[FOR_TYPE_IND]).split("=")[1]

			# Do the county split
			if for_type in fortypes_to_split:
				county = parse_as_int_if_valid(row[2])
				for_type = county_split_id(for_type, county, str_groups, stand_cn, county_split_dict)

			if not stand_cn in stand_fortype_map.keys():
				stand_fortype_map[stand_cn] = for_type
	
	return stand_fortype_map


def county_split_id (for_type: str, county: int, str_groups: str, stand_cn: str, county_split_dict: dict) -> str:
	for new_fortype in county_split_dict[for_type].keys():
		if county in county_split_dict[for_type][new_fortype]:
			return new_fortype
	
	# The for loop above is expected to return
	print(" > [[ Warning ]]")
	print(f" > \tFound {for_type} forest type outside of specified counties")
	print(f" > \tGroups: {str_groups}")
	print(f" > \tStand CN: {stand_cn}")
	print(f" > \tCounty: {county}")
	return for_type



def do_replacement(cur: sqlite3.Cursor, table_name:str, cn_to_fortype_dict: list) -> None:
	print(f" > Doing ID Replacement for {table_name}")

	for ind, key in enumerate(list(cn_to_fortype_dict.keys())):
		stand_cn = key
		for_type = cn_to_fortype_dict[key]

		query = f'''
			UPDATE {table_name} SET STAND_ID = "{for_type}"
			WHERE STAND_CN = {stand_cn}
		'''
		cur.execute(query)

		if (ind % 1000 == 0):
			print(f" > Executed 1000 ID Replacements")


def do_id_replace(cur: sqlite3.Cursor, county_split_dict: dict) -> None:
	# Actual processing
	fortype_dict = extract_forest_types(
		cur, 
	   ["FVS_STANDINIT_PLOT", "FVS_PLOTINIT_PLOT"],
		county_split_dict
		)

	# Now do replacements
	do_replacement(cur, "FVS_PLOTINIT_PLOT", fortype_dict)
	do_replacement(cur, "FVS_STANDINIT_PLOT", fortype_dict)
	do_replacement(cur, "FVS_TREEINIT_PLOT", fortype_dict)

	do_replacement(cur, "FVS_PLOTINIT_PLOT_INVYEARST", fortype_dict)
	do_replacement(cur, "FVS_STANDINIT_PLOT_INVYEARST", fortype_dict)
	do_replacement(cur, "FVS_TREEINIT_PLOT_INVYEARST", fortype_dict)

	print("Finished ID Replace")


if __name__ == '__main__':
	DB_PATH = "./FIADB_NJ.db"
	db_connection = sqlite3.connect(DB_PATH)
	cur = db_connection.cursor()

	print("WARNING: This file only runs the ID replacement steps.")
	print("\tIt is automatically run from the main file, so you")
	print("\tdo not need to run this seperately.")
	print()

	usr_input = str(input("Do you still wish to continue? (y/n)"))
	print()

	if (usr_input.strip().lower() != 'y'):
		print("Ok, exiting")
		sys.exit(0)
	else:
		print("Ok, continuing")


	do_id_replace(cur)

	db_connection.commit()
	db_connection.close()


