'''
gui_main.py

This file launches the program
'''

from ast import Global
import tkinter as tk
import constraint_builder_project_overview
import constraint_builder_obj_import
from enum import Enum, unique, auto
from typing import List, Dict
from attrs import define, frozen
import varname_dataclasses as models
import constraint_processer as proc



def main():

	# Read in sample data

	# rawNames = proc.readAllObjVarnames(
	# 	'/home/velcro/Documents/Professional/NJDEP/TechWork/ForMOM/src/optimization/constraint_builder/sample_data/minimodel_obj.csv'
	# )
	# varTagsInfo = proc.makeVarTagsInfoObject(rawNames, '_', ['species', 'year', 'management'])
	# constrAllBySpeciesByYear = models.StandardConstraintGroup(
	# 	selected_tags = {
	# 		"species": ["167N", "409"], 
	# 		"year": ["2021", "2050"], 
	# 		"management": ["PLSQ", "PLWF"]},
	# 	split_by_groups = ["species", "year"],
	# 	name = "All",
	# 	default_compare = models.ComparisonSign.LE,
	# 	default_value = 6.9
	# )
	# constrList = [constrAllBySpeciesByYear]

	globalstate = models.GlobalState(None, None)


	# Building
	root = tk.Tk()

	constraint_builder_obj_import.buildObjImport(root, globalstate)

	root.mainloop()



if __name__ == '__main__':
	main()
else:
	print("[[ ERROR ]] This file is not meant to be imported")
	num = 1 / 0
