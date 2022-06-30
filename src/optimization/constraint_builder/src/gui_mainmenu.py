'''
Main Screen

This gives the user the option to load a project or start fresh.
'''

import tkinter as tk

import gui_newproject
import gui_projectoverview
import io_file
import models
from gui_consts import *

_passedProjectState: models.ProjectState = None
_passedRoot: tk.Tk = None




#
# Update Calls
#

def updateNewProj():
	global _passedProjectState

	_passedProjectState = models.ProjectState.createEmptyProjectState()

	transitionToObjImport()


def updateLoadProj():
	global _passedProjectState

	projFilepath: str = io_file.getOpenFilepath(PROJ_FILES)
	
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






#
# Transition Calls
#

def transitionToObjImport() -> None:
	global _passedProjectState, _passedRoot

	# Reset root
	for child in _passedRoot.winfo_children():
		child.destroy()

	# Transition
	gui_newproject.buildGUI_ObjImport(_passedRoot, _passedProjectState)


def transitionToOverview() -> None:
	global _passedProjectState, _passedRoot

	# Reset root
	for child in _passedRoot.winfo_children():
		child.destroy()

	# Transition
	gui_projectoverview.buildGUI_ProjectOverview(_passedRoot, _passedProjectState)




#
# Main GUI Construction
#

def buildGUI_OpeningScreen(root: tk.Tk, projectState: models.ProjectState):
	global _passedProjectState, _passedRoot

	_passedProjectState = projectState
	_passedRoot = root

	root.title("Constraint Builder - Main Screen")

	root.columnconfigure(0, weight=1)
	root.rowconfigure(1, weight=1)

	lblHeader = tk.Label(root, text="NJDEP Constraint Builder", font=("Arial", 16), anchor="center")
	lblHeader.grid(row=0, column=0, sticky="ew", padx=20, pady=10)


	frmOptions = tk.Frame(root)
	frmOptions.grid(row=1, column=0, sticky="")
	# frmOptions.rowconfigure([0, 1], weight=1)
	# frmOptions.columnconfigure(0, weight=1)

	btnNewProj = tk.Button(frmOptions, text="New Constraint Project", command=updateNewProj)
	btnNewProj.grid(row=0, column=0, sticky="ew", pady=5)

	btnLoadProj = tk.Button(frmOptions, text="Open Project", command=updateLoadProj)
	btnLoadProj.grid(row=1, column=0, sticky="ew", pady=5)


	lblSubInfo = tk.Label(root, text="ForMOM Project\nDev: Michael Gorbunov\nTest: Courtney Compton, Bill Zipse", anchor="e", justify="right")
	lblSubInfo.grid(row=2, column=0, sticky="se", padx=20, pady=(0, 20))






if __name__ == '__main__':
	projectState = models.ProjectState.createEmptyProjectState()

	root = tk.Tk()
	buildGUI_OpeningScreen(root, projectState)
	root.mainloop()


