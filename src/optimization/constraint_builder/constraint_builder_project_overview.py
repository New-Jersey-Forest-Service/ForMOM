'''
Constraint Builder Constraints Overview Screen
'''

import copy
import csv
import json
from pathlib import Path
import tkinter as tk
import constraint_builder_standard_constr
import varname_dataclasses as models
import constraint_processer as proc
from enum import Enum, unique, auto
from typing import List
from tkinter import ttk, filedialog
import math



WIDTH_SML = 8
WIDTH_MED = 15
WIDTH_BIG = 35
CSV_FILES = [('CSV Files', '*.csv'), ('All Files', '*.*')]
PROJ_FILES = [('Project Files', '*.cproj'), ('All Files', '*.*')]


# Exposed GUI Elements
_frmConstrsDisplay: tk.Frame = None


# State Variables
_constrGroupList: List[models.StandardConstraintGroup] = None

_passedProjectState: models.ProjectState = None
_passedRoot: tk.Tk = None


# This will be useful for scrolling
# https://stackoverflow.com/questions/68056757/how-to-scroll-through-tkinter-widgets-that-were-defined-inside-of-a-function








#
# Update Calls
#

def updateDeleteConstrGroup (constrInd: int) -> None:
	global _constrGroupList
	# Do updating
	print(f"Deleteting {_constrGroupList[constrInd].constr_prefix}")

	_constrGroupList.pop(constrInd)

	redrawConstrListFrame(_constrGroupList)


def updateNewConstrGroup () -> None:
	global _constrGroupList

	print(f"Adding a new constraint")
	_constrGroupList.append(models.StandardConstraintGroup.createEmptyConstraint(_passedProjectState.varTags))

	redrawConstrListFrame(_constrGroupList)


def updateSaveProject () -> None:
	print("Saving project file")

	outputFilepathStr = filedialog.asksaveasfilename(
		filetypes=PROJ_FILES,
		defaultextension=PROJ_FILES
		)

	if isInvalidFile(outputFilepathStr):
		return

	projectDataStr = models.toOutputStr(_passedProjectState, models.ProjectState)
	with open(outputFilepathStr, 'w') as outFile:
		outFile.write(projectDataStr)


def isInvalidFile(dialogOutput) -> bool:
    # For whatever reason, filedialog.askname() can return multiple different things ???
    return dialogOutput == None or len(dialogOutput) == 0 or dialogOutput.strip() == ""


def updateExportCSV () -> None:
	print("Exporting to csv")

	outputFilepathStr = filedialog.asksaveasfilename(
		filetypes=CSV_FILES,
		defaultextension=CSV_FILES
		)

	if isInvalidFile(outputFilepathStr):
		return

	with open(outputFilepathStr, 'w') as outFile:
		writer = csv.writer(outFile, delimiter=',', quotechar='"')
		
		# Write top row - all variables names
		delim = _passedProjectState.delim
		allVarNamesSorted = copy.deepcopy(_passedProjectState.varTags.all_vars)
		allVarNamesSorted.sort(key=lambda tags: delim.join(tags))
		allVarNamesRaw = [delim.join(x) for x in allVarNamesSorted]

		writer.writerow(['const_name'] + allVarNamesRaw + ['operator', 'rtSide'])

		# Write each constraint
		rowLen = len(allVarNamesSorted) + 3

		for constGroup in _passedProjectState.constrGroupList:
			individConstrs = proc.compileStandardConstraintGroup(_passedProjectState.varTags, constGroup)

			for constr in individConstrs:
				nextRow = [''] * rowLen
				nextRow[0] = constr.name
				nextRow[-1] = constr.compare_value
				nextRow[-2] = constr.compare_type.name.lower()

				for ind, var in enumerate(allVarNamesSorted):
					coef = 0
					if var in constr.var_tags:
						varInd = constr.var_tags.index(var)
						coef = constr.var_coeffs[varInd]
					nextRow[ind+1] = coef
				
				writer.writerow(nextRow)
	
	print(":D File Written")










#
# Transition Calls
#

def transitionToEditing (constrInd: int) -> None:
	global _constrGroupList, _passedProjectState, _passedRoot
	print(f"Editing {_constrGroupList[constrInd].constr_prefix}")

	_passedProjectState.constrGroupList = _constrGroupList

	for child in _passedRoot.winfo_children():
		child.destroy()

	constraint_builder_standard_constr.buildConstraintBuildingGUI(_passedRoot, _passedProjectState, constrInd)














#
# Redraw Calls
#

def redrawConstrListFrame (constrGroupList: List[models.StandardConstraintGroup]) -> None:
	global _frmConstrsDisplay

	for child in _frmConstrsDisplay.winfo_children():
		child.destroy()

	for ind, constrGroup in enumerate(constrGroupList):
		frmConstr = tk.Frame(_frmConstrsDisplay, relief=tk.RIDGE, bd=2)
		frmConstr.grid(row=ind, column=0, sticky="ew", pady=(0, 10))
		frmConstr.columnconfigure(1, weight=1)
		
		lblName = tk.Label(frmConstr, text=constrGroup.constr_prefix)
		lblName.grid(row=0, column=0, sticky="w")

		btnDelete = tk.Button(frmConstr, text="Delete", command=lambda ind=ind: updateDeleteConstrGroup(ind))
		btnDelete.grid(row=0, column=1, sticky="e")

		btnEdit = tk.Button(frmConstr, text="Edit >", command=lambda ind=ind: transitionToEditing(ind))
		btnEdit.grid(row=0, column=2, sticky="e")














#
# Main GUI Construction
#

def buildProjectOverviewGUI(root: tk.Tk, projectState: models.ProjectState) -> None:
	global _constrGroupList, _passedRoot, _passedProjectState

	_passedProjectState = projectState
	_passedRoot = root
	_constrGroupList = projectState.constrGroupList

	root.title("Constraint Builder - Stage 3: Constraints Overview")
	root.rowconfigure(1, weight=1)
	root.columnconfigure(0, weight=1)

	# Header text
	lblHeader = tk.Label(root, text="Stage 3 - Constraints Overview")
	lblHeader.grid(row=0, column=0, padx=10, pady=(10, 0))

	# Constraint Groups Display
	frmConstrsDisplay = buildConstraintGroupListFrame(root)
	frmConstrsDisplay.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")

	# New Constraint Group
	frmNewConstrBtn = buildConstraintButtonFrame(root)
	frmNewConstrBtn.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="ew")

	# Exporting Buttons
	frmExport = buildExportButtonsFrame(root)
	frmExport.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="ew")


	print("GUI Build, now redrawing some othe info")
	redrawConstrListFrame(_constrGroupList)
	

def buildConstraintGroupListFrame(root: tk.Tk) -> tk.Frame:
	global _frmConstrsDisplay

	_frmConstrsDisplay = tk.Frame(root)
	_frmConstrsDisplay.columnconfigure(0, weight=1)

	return _frmConstrsDisplay


def buildConstraintButtonFrame(root: tk.Tk) -> tk.Frame:
	frmNewConstrBtn = tk.Frame(root)
	frmNewConstrBtn.columnconfigure(0, weight=1)

	btnNew = tk.Button(frmNewConstrBtn, text="New Constraint Group", anchor="center", command=updateNewConstrGroup)
	btnNew.grid(row=0, column=0, sticky="ew")

	return frmNewConstrBtn


def buildExportButtonsFrame(root: tk.Tk) -> tk.Frame:
	frmExport = tk.Frame(root)
	frmExport.columnconfigure(0, weight=1)

	btnSaveProj = tk.Button(frmExport, text="Save Project", command=updateSaveProject)
	btnSaveProj.grid(row=0, column=0, sticky="e")

	btnExportProj = tk.Button(frmExport, text="Export to .csv", command=updateExportCSV)
	btnExportProj.grid(row=0, column=1, sticky="e")

	return frmExport





if __name__ == '__main__':
	varTagsInfo = proc.makeVarTagsInfoObjectFromFile(
		# './sample_data/minimodel_obj.csv', 
		'/home/velcro/Documents/Professional/NJDEP/TechWork/ForMOM/src/optimization/constraint_builder/sample_data/minimodel_obj.csv',
		'_', 
		['for_type', 'year', 'mng']
		)

	# TODO: To remove future polymorphism, add a general constriantinfo class ?
	constrGroupList: List[models.StandardConstraintGroup] = [
		models.StandardConstraintGroup(
			selected_tags={'for_type': ['167N', '167S', '409'], 'year': ["2021", "2025", "2030", "2050"], 'mng': ['RBWF', 'PLSQ', 'TB']},
			split_by_groups=['for_type'],
			constr_prefix="MaxAcresBySpecies",
			default_compare=models.ComparisonSign.EQ,
			default_rightside=0
		),
		models.StandardConstraintGroup.createEmptyConstraint(varTagsInfo)
	]

	projState = models.ProjectState('_', varTagsInfo, constrGroupList)

	root = tk.Tk()
	buildProjectOverviewGUI(root, projState)
	root.mainloop()




'''
	Treet others how you want to be treeted

			  v .   ._, |_  .,
		   `-._\/  .  \ /	|/_
			   \\  _\, y | \//
		 _\_.___\\, \\/ -.\||
		   `7-,--.`._||  / / ,
		   /'	 `-. `./ / |/_.'
					 |	|//
					 |_	/
					 |-   |
					 |   =|
					 |	|
--------------------/ ,  . \--------._
  jg
'''


