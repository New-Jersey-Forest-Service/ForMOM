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

def extract_forest_types(cur: sqlite3.Cursor, tables: list):
	# creates a map from STAND_CN (int) -> for_type (str)
	stand_fortype_map = {}

	for table_name in tables:
		query = f'SELECT GROUPS, STAND_CN FROM {table_name}'
		cur.execute(query)

		for row in cur:
			stand_cn = int(row[1])
			str_groups = str(row[0]).split(" ")
			FOR_TYPE_IND = 7
			# This is making a lot of assumptions about the db :(
			for_type = str(str_groups[FOR_TYPE_IND]).split("=")[1]

			if not stand_cn in stand_fortype_map.keys():
				stand_fortype_map[stand_cn] = for_type
	
	return stand_fortype_map


def do_replacement(cur: sqlite3.Cursor, table_name:str, cn_to_fortype_dict: list) -> None:
	for ind, key in enumerate(list(cn_to_fortype_dict.keys())):
		stand_cn = key
		for_type = cn_to_fortype_dict[key]

		query = f'''
			UPDATE {table_name} SET STAND_ID = "{for_type}"
			WHERE STAND_CN = {stand_cn}
		'''
		cur.execute(query)

def do_id_replace(cur: sqlite3.Cursor):
	# Actual processing
	fortype_dict = extract_forest_types(cur, 
	   ["FVS_STANDINIT_PLOT_20152019T", 
		"FVS_PLOTINIT_PLOT_20152019T",
		"FVS_STANDINIT_PLOT",
		"FVS_STANDINIT_PLOT"])

	# Now do replacements
	do_replacement(cur, "FVS_PLOTINIT_PLOT", fortype_dict)
	do_replacement(cur, "FVS_STANDINIT_PLOT", fortype_dict)
	do_replacement(cur, "FVS_TREEINIT_PLOT", fortype_dict)

	do_replacement(cur, "FVS_PLOTINIT_PLOT_20152019T", fortype_dict)
	do_replacement(cur, "FVS_STANDINIT_PLOT_20152019T", fortype_dict)
	do_replacement(cur, "FVS_TREEINIT_PLOT_20152019T", fortype_dict)

	print("Finished ID Replace")


if __name__ == '__main__':
	DB_PATH = "./FIADB_NJ.db"
	db_connection = sqlite3.connect(DB_PATH)
	cur = db_connection.cursor()

	do_id_replace(cur)

	db_connection.commit()
	db_connection.close()


