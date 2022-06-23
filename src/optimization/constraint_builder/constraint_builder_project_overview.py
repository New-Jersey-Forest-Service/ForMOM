'''
Constraint Builder Constraints Overview Screen
'''

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


# Exposed GUI Elements
_frmConstrsDisplay: tk.Frame = None


# State Variables
_constrGroupList: List[models.StandardConstraintGroup] = None

_passedGlobalState: models.GlobalState = None
_passedRoot: tk.Tk = None


# This will be useful for scrolling
# https://stackoverflow.com/questions/68056757/how-to-scroll-through-tkinter-widgets-that-were-defined-inside-of-a-function








#
# Update Calls
#

def updateDeleteConstrGroup (constrInd: int) -> None:
	global _constrGroupList
	# Do updating
	print(f"Deleteting {_constrGroupList[constrInd].name}")

	_constrGroupList.pop(constrInd)

	redrawConstrListFrame(_constrGroupList)


def updateNewConstrGroup () -> None:
	global _constrGroupList

	print(f"Adding a new constraint")
	_constrGroupList.append(models.StandardConstraintGroup.createEmptyConstraint(_passedGlobalState.varTags))

	redrawConstrListFrame(_constrGroupList)


def updateSaveProject () -> None:
	print("Saving project file")
	pass


def updateExportCSV () -> None:
	print("Exporting to csv")
	pass










#
# Transition Calls
#

def transitionToEditing (constrInd: int) -> None:
	global _constrGroupList, _passedGlobalState, _passedRoot
	print(f"Editing {_constrGroupList[constrInd].name}")

	_passedGlobalState.constrGroupList = _constrGroupList

	for child in _passedRoot.winfo_children():
		child.destroy()

	constraint_builder_standard_constr.buildConstraintBuildingGUI(_passedRoot, _passedGlobalState, constrInd)














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
		
		lblName = tk.Label(frmConstr, text=constrGroup.name)
		lblName.grid(row=0, column=0, sticky="w")

		btnDelete = tk.Button(frmConstr, text="Delete", command=lambda ind=ind: updateDeleteConstrGroup(ind))
		btnDelete.grid(row=0, column=1, sticky="e")

		btnEdit = tk.Button(frmConstr, text="Edit >", command=lambda ind=ind: transitionToEditing(ind))
		btnEdit.grid(row=0, column=2, sticky="e")














#
# Main GUI Construction
#

def buildProjectOverviewGUI(root: tk.Tk, globalState: models.GlobalState) -> None:
	global _constrGroupList, _passedRoot, _passedGlobalState

	_passedGlobalState = globalState
	_passedRoot = root
	_constrGroupList = globalState.constrGroupList

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
	# TODO: To remove future polymorphism, add a general constriantinfo class
	_constrGroupList: List[models.StandardConstraintGroup] = [
		models.StandardConstraintGroup(
			selected_tags=dict(),
			split_by_groups=list(),
			name="MaxAcresBySpecies",
			default_compare=models.ComparisonSign.EQ,
			default_value=0
		),
		models.StandardConstraintGroup(
			selected_tags=dict(),
			split_by_groups=list(),
			name="SPBForcing",
			default_compare=models.ComparisonSign.EQ,
			default_value=0
		)
	]

	root = tk.Tk()
	buildProjectOverviewGUI(root)
	root.mainloop()

