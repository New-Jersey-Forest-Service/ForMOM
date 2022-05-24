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

# TODO: Validate 
#   - [ ] Check table names for table_name
#   - [ ] Check that for_type_ind does indeed have "ForType="
#   - [ ] Check that stand_cn uniquely maps to a forest type
#   - [ ] Check that all stand_cns are covered (esp with TREEINIT)
# TODO: Less magic numbers
#   - [ ] Somehow explain or derive the 7
# TODO: Less magic names
#	- [ ] Use dataclases or attrs classes instead of dicts
# TODO: Better integration
#	- [ ] Rewrite the structs to use cur.executemany()


def is_valid_float(float_str: str) -> bool:
	try:
		float(float_str)
		return True
	except:
		return False


def extract_forest_types(cur: sqlite3.Cursor, tables: list):
	# creates a map from STAND_CN (int) -> for_type (str)
	stand_fortype_map = {}

	for table_name in tables:
		query = f'SELECT GROUPS, STAND_CN, COUNTY FROM {table_name}'
		cur.execute(query)

		for row in cur:
			stand_cn = int(row[1])

			str_groups = str(row[0]).split(" ")
			FOR_TYPE_IND = 7
			# This is making a lot of assumptions about the db :(
			for_type = str(str_groups[FOR_TYPE_IND]).split("=")[1]

			# Do the 167 Split
			if (for_type == '167'):
				county = row[2]
				if (is_valid_float(county)):
					county = int(float(county))
				else:
					county = -1

				# if county in (5, 23, 25, 29) => 167 N
				# if county in (1, 7, 11, 15, 19) => 167 S

				if (county in (23, 25, 29, 1)):
					for_type = '167N'
				elif (county in (5, 7, 15, 11, 9)):
					for_type = '167S'
				else:
					print(" > [[ Warning ]]")
					print(" > \tFound 167 forest type outside of specified counties")
					print(f" > \tGroups: {str_groups}")
					print(f" > \tStand CN: {stand_cn}")
					print(f" > \tCounty: {county}")

			if not stand_cn in stand_fortype_map.keys():
				stand_fortype_map[stand_cn] = for_type
	
	return stand_fortype_map


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


def do_id_replace(cur: sqlite3.Cursor) -> None:
	# Actual processing
	fortype_dict = extract_forest_types(cur, 
	   ["FVS_STANDINIT_PLOT",
		"FVS_PLOTINIT_PLOT"])

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


