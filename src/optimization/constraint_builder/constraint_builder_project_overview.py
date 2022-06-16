'''
Constraint Builder Constraints Overview Screen
'''

from pathlib import Path
import tkinter as tk
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
frmConstrsDisplay: tk.Frame = None


# Exposed State
constrGroupList: List[models.StandardConstraintGroup] = None



# This will be useful for scrolling
# https://stackoverflow.com/questions/68056757/how-to-scroll-through-tkinter-widgets-that-were-defined-inside-of-a-function








#
# Update Calls
#

def updateDeleteConstrGroup (constrInd: int) -> None:
	global constrGroupList
	# Do updating
	print(f"Deleteting {constrGroupList[constrInd].name}")

	constrGroupList.pop(constrInd)

	redrawConstrListFrame(constrGroupList)


def updateEditConstrGroup (constrInd: int) -> None:
	global constrGroupList
	print(f"Editing {constrGroupList[constrInd].name}")

	redrawConstrListFrame(constrGroupList)


def updateNewConstrGroup () -> None:
	global constrGroupList

	newConstr = models.StandardConstraintGroup(
		dict(), 
		list(), 
		"new constraint", 
		models.ComparisonSign.EQUAL, 
		default_value=0
	)

	print(f"Adding a new constraint")
	constrGroupList.append(newConstr)

	updateEditConstrGroup(len(constrGroupList) - 1)
	redrawConstrListFrame(constrGroupList)


def updateSaveProject () -> None:
	print("Saving project file")
	pass


def updateExportCSV () -> None:
	print("Exporting to csv")
	pass










#
# Redraw Calls
#

def redrawConstrListFrame (constrGroupList: List[models.StandardConstraintGroup]) -> None:
	global frmConstrsDisplay

	for child in frmConstrsDisplay.winfo_children():
		child.destroy()

	for ind, constrGroup in enumerate(constrGroupList):
		frmConstr = tk.Frame(frmConstrsDisplay, relief=tk.RIDGE, bd=2)
		frmConstr.grid(row=ind, column=0, sticky="ew", pady=(0, 10))
		frmConstr.columnconfigure(1, weight=1)
		
		lblName = tk.Label(frmConstr, text=constrGroup.name)
		lblName.grid(row=0, column=0, sticky="w")

		btnDelete = tk.Button(frmConstr, text="Delete", command=lambda ind=ind: updateDeleteConstrGroup(ind))
		btnDelete.grid(row=0, column=1, sticky="e")

		btnEdit = tk.Button(frmConstr, text="Edit >", command=lambda ind=ind: updateEditConstrGroup(ind))
		btnEdit.grid(row=0, column=2, sticky="e")














#
# Main GUI Construction
#

def buildProjectOverviewGUI(root: tk.Tk) -> None:
	global constrGroupList

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
	redrawConstrListFrame(constrGroupList)
	

def buildConstraintGroupListFrame(root: tk.Tk) -> tk.Frame:
	global frmConstrsDisplay

	frmConstrsDisplay = tk.Frame(root)
	frmConstrsDisplay.columnconfigure(0, weight=1)

	return frmConstrsDisplay


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
	constrGroupList: List[models.StandardConstraintGroup] = [
		models.StandardConstraintGroup(
			selected_tags=None,
			split_by_groups=None,
			name="Im14AndThisIsDeep",
			default_compare=None,
			default_value=0
		),
		models.StandardConstraintGroup(
			selected_tags=None,
			split_by_groups=None,
			name="AgedLikeMilk",
			default_compare=None,
			default_value=0
		)
	]

	root = tk.Tk()
	buildProjectOverviewGUI(root)
	root.mainloop()

