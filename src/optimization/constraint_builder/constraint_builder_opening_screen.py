'''
Main Screen

This gives the user the option to load a project or start fresh.
'''

import tkinter as tk


import tkinter as tk
import constraint_builder_obj_import
import constraint_builder_project_overview
import varname_dataclasses as models
import constraint_processer as proc
import copy
from enum import Enum, unique, auto
from typing import List, Union, Dict
from tkinter import ttk, filedialog
import math
import csv


WIDTH_SML = 8
WIDTH_MED = 15
WIDTH_BIG = 35
CSV_FILES = [('CSV Files', '*.csv'), ('All Files', '*.*')]
PROJ_FILES = [('Project Files', '*.cproj'), ('All Files', '*.*')]

_passedProjectState: models.ProjectState = None
_passedRoot: tk.Tk = None




#
# Update Calls
#

def updateNewProj():
	global _passedProjectState

	_passedProjectState = models.ProjectState.createEmptyprojectState()

	transitionToObjImport()


def updateLoadProj():
	global _passedProjectState

	projFilepath: str = filedialog.askopenfilename(
		filetypes=PROJ_FILES,
		defaultextension=PROJ_FILES
		)

	if isInvalidFile(projFilepath):
		return
	
	# YES, ik it's ugly bringing the entire file into main memory :/
	fileData = None
	with open(projFilepath, 'r') as file:
		fileData = file.read()
	if fileData == None:
		return
	
	newProjState = models.fromOutputStr(fileData, models.ProjectState)
	if not isinstance(newProjState, models.ProjectState):
		return

	_passedProjectState = newProjState
	
	transitionToOverview()



def isInvalidFile(dialogOutput) -> bool:
	# For whatever reason, filedialog.askname() can return multiple different things ???
	return dialogOutput == None or len(dialogOutput) == 0 or dialogOutput.strip() == ""






#
# Transition Calls
#

def transitionToObjImport() -> None:
	global _passedProjectState, _passedRoot

	# Reset root
	for child in _passedRoot.winfo_children():
		child.destroy()

	# Transition
	constraint_builder_obj_import.buildObjImport(_passedRoot, _passedProjectState)


def transitionToOverview() -> None:
	global _passedProjectState, _passedRoot

	# Reset root
	for child in _passedRoot.winfo_children():
		child.destroy()

	# Transition
	constraint_builder_project_overview.buildProjectOverviewGUI(_passedRoot, _passedProjectState)




#
# Main GUI Construction
#

def buildOpeningScreen(root: tk.Tk, projectState: models.ProjectState):
	global _passedProjectState, _passedRoot

	_passedProjectState = projectState
	_passedRoot = root

	root.title("Constraint Builder - Main Screen")

	root.columnconfigure(0, weight=1)
	root.rowconfigure(1, weight=1)

	lblHeader = tk.Label(root, text="NJDEP Constraint Builder")
	lblHeader.grid(row=0, column=0, sticky="ew")

	frmOptions = tk.Frame(root)
	frmOptions.grid(row=1, column=0)
	frmOptions.columnconfigure([0, 1], weight=1)

	btnNewProj = tk.Button(frmOptions, text="New Constraint Project", command=updateNewProj)
	btnNewProj.grid(row=0, column=0, sticky="ew")

	btnLoadProj = tk.Button(frmOptions, text="Open Project", command=updateLoadProj)
	btnLoadProj.grid(row=0, column=1, sticky="ew")




if __name__ == '__main__':
	projectState = models.ProjectState(None, None)

	root = tk.Tk()
	buildOpeningScreen(root, projectState)
	root.mainloop()


