'''
Constraint Builder Constraints Overview Screen
'''

import copy
import csv
import tkinter as tk
from tkinter import ttk
from typing import List

import proc_constraints as proc
import proc_render as render
import gui_variablefiltering
import gui_newcsv
import models
from gui_consts import *
import devtesting
import io_file

# Exposed GUI Elements
_frmConstrsDisplay: tk.Frame = None


# State Variables
_constrGroupList: List[models.SetupConstraintGroup] = None

_passedProjectState: models.ProjectState = None
_passedRoot: tk.Tk = None


# This will be useful for scrolling
# https://stackoverflow.com/questions/68056757/how-to-scroll-through-tkinter-widgets-that-were-defined-inside-of-a-function








#
# Update Calls
#

def updateDeleteConstrGroup (constrInd: int) -> None:
	global _constrGroupList
	print(f"Deleteting {_constrGroupList[constrInd].namePrefix}")

	_constrGroupList.pop(constrInd)

	redrawConstrListFrame(_constrGroupList)


def updateNewConstrGroup () -> None:
	global _constrGroupList
	print(f"Adding a new constraint")

	_constrGroupList.append(models.SetupConstraintGroup.createEmptySetup(_passedProjectState.varData))

	redrawConstrListFrame(_constrGroupList)


# TODO: Move so much of this into fileio
def updateSaveProject () -> None:
	print("Saving project file")

	outputFilepathStr = io_file.getSaveAsFilepath(PROJ_FILES)
	if outputFilepathStr == None:
		return

	projectDataStr = models.toOutputStr(_passedProjectState, models.ProjectState)
	with open(outputFilepathStr, 'w') as outFile:
		outFile.write(projectDataStr)


def updateExportCSV () -> None:
	print("Exporting to csv")

	outputFilepathStr = io_file.getSaveAsFilepath(CSV_FILES)
	if outputFilepathStr == None:
		return
	io_file.writeToCSV(outputFilepathStr, _passedProjectState)
	
	print(":D File Written")








#
# Transition Calls
#

def transitionToEditing (constrInd: int) -> None:
	global _constrGroupList, _passedProjectState, _passedRoot
	print(f"Editing {_constrGroupList[constrInd].namePrefix}")

	_passedProjectState.setupList = _constrGroupList

	for child in _passedRoot.winfo_children():
		child.destroy()

	gui_variablefiltering.buildGUI_VariableFiltering(_passedRoot, _passedProjectState, constrInd)


def transitionToObjReplace () -> None:
	global _passedProjectState, _passedRoot
	print(f"Going to objective file replacement screen")

	_passedProjectState.setupList = _constrGroupList

	for child in _passedRoot.winfo_children():
		child.destroy()
	
	newGui = gui_newcsv.GUINewCSV(_passedRoot, _passedProjectState)
	













#
# Redraw Calls
#

def redrawConstrListFrame (constrGroupList: List[models.SetupConstraintGroup]) -> None:
	global _frmConstrsDisplay

	for child in _frmConstrsDisplay.winfo_children():
		child.destroy()

	CONSTRS_PER_ROW = 3
	_frmConstrsDisplay.columnconfigure([x for x in range(CONSTRS_PER_ROW)], weight=1)

	for ind, constrGroup in enumerate(constrGroupList):
		frmConstr = tk.Frame(_frmConstrsDisplay, relief=tk.RIDGE, bd=2)
		frmConstr.grid(
			row=ind//CONSTRS_PER_ROW, 
			column=ind%CONSTRS_PER_ROW, 
			sticky="ew", 
			pady=(0, 10),
			padx=5
			)
		frmConstr.columnconfigure(1, weight=1)
		
		name = render.trimEllipsisRight(constrGroup.namePrefix, WIDTH_BIG)
		lblName = tk.Label(frmConstr, text=name)
		lblName.grid(row=0, column=0, sticky="w", padx=10, pady=5)

		btnDelete = tk.Button(frmConstr, text="Delete", command=lambda ind=ind: updateDeleteConstrGroup(ind))
		btnDelete.grid(row=0, column=1, sticky="e", padx=5, pady=5)

		btnEdit = tk.Button(frmConstr, text="Edit >", command=lambda ind=ind: transitionToEditing(ind))
		btnEdit.grid(row=0, column=2, sticky="e", padx=5, pady=5)














#
# Main GUI Construction
#

def buildGUI_ProjectOverview(root: tk.Tk, projectState: models.ProjectState) -> None:
	global _constrGroupList, _passedRoot, _passedProjectState

	_passedProjectState = projectState
	_passedRoot = root
	_constrGroupList = projectState.setupList

	root.title("Constraint Builder - Project Overview")
	root.rowconfigure(1, weight=1)
	root.columnconfigure(0, weight=1)

	# Header text
	lblHeader = tk.Label(root, text="Project Overview")
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
	btnNew.grid(row=0, column=0)

	return frmNewConstrBtn


def buildExportButtonsFrame(root: tk.Tk) -> tk.Frame:
	frmExport = tk.Frame(root)
	frmExport.columnconfigure([0, 1], weight=1)

	btnChangeCsv = ttk.Button(frmExport, text="Change Objective .csv", command=transitionToObjReplace)
	btnChangeCsv.grid(row=0, column=0, sticky="e")

	btnSaveProj = tk.Button(frmExport, text="Save Project", command=updateSaveProject)
	btnSaveProj.grid(row=0, column=1, sticky="e")

	btnExportProj = tk.Button(frmExport, text="Export to .csv", command=updateExportCSV)
	btnExportProj.grid(row=0, column=2, sticky="e", padx=10, pady=10)

	return frmExport





if __name__ == '__main__':
	projState = devtesting.dummyProjectState()

	root = tk.Tk()
	buildGUI_ProjectOverview(root, projState)
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


