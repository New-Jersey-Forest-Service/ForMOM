'''
Constraint Builder Objective File Import
'''

import math
import tkinter as tk
from enum import Enum, auto, unique
from pathlib import Path
from tkinter import ttk
from typing import List

import proc_constraints as proc
import gui_projectoverview
import io_file
import linting as lint
import models
from gui_consts import *
import devtesting

# Exposed gui elements
_lblObjFile: tk.Label = None
_lblLoadedSampleVar: tk.Label = None
_cbbDelimSelector: ttk.Combobox = None

_frmNameGroups: tk.Frame = None
_lblVerifyNames: tk.Label = None

_nameEntVarList: List[tk.StringVar] = None

_btnNextStage: tk.Button = None


#
# Data State
_objSampleVar: str = None
_errWithObjFile: str = None
_errWithNamesList: str = None

# user input
_objFileStr: str = None
_groupnameList: List[str] = None
_delimiter: str = None

# useful processed values
_varNamesRaw: List[str] = None
_tagLists: List[List[str]] = None

_passedRoot: tk.Tk = None
_passedProjectState: models.ProjectState = None




#
# Update Calls
#

def updateNewObjFile() -> None:
	'''
		Select objective csv with a chooser
	'''
	global _objFileStr

	newPath = io_file.getOpenFilepath(CSV_FILES)
	if newPath != None:
		_objFileStr = newPath

	processParseFile()
	multiRedrawFileUpdate()


def updateNewDelim() -> None:
	global _delimiter, _cbbDelimSelector

	_delimiter = _cbbDelimSelector.get()

	processParseFile()
	multiRedrawFileUpdate()


def updateGroupName() -> None:
	'''
		Reads the groupname string variables
	'''
	global _nameEntVarList, _groupnameList, _errWithNamesList

	_groupnameList = [x.get() for x in _nameEntVarList]
	_errWithNamesList = lint.lintAllTagGroupNames(_groupnameList)

	multiRedrawNameUpdate()


#
# Processing Calls
#

def processParseFile() -> None:
	global _varNamesRaw, _objSampleVar, _errWithObjFile, _tagLists


	# TODO: This processing call really should be a single thing no?
	_varNamesRaw = None
	_objSampleVar = None
	_errWithObjFile = None
	_tagLists = None

	if _objFileStr == None:
		return
	
	# TODO: Lint file name (in processing module)
	_varNamesRaw = io_file.readVarnamesRaw(Path(_objFileStr))
	_objSampleVar = _varNamesRaw[0]

	if _delimiter == None:
		return
	_errWithObjFile = lint.lintAllVarNamesRaw(_varNamesRaw, _delimiter)

	if _errWithObjFile:
		return
	_tagLists = proc.makeTagGroupMembersList(_varNamesRaw, _delimiter)



#
# Transition Calls
#

def transitionToOverview() -> None:
	global _passedRoot, _passedProjectState

	# Write Data
	_passedProjectState.varTags = proc.buildVarTagsInfoObject(_varNamesRaw, _delimiter, _groupnameList)
	_passedProjectState.constrGroupList = []

	# Clear Root
	for child in _passedRoot.winfo_children():
		child.destroy()

	# Transition
	gui_projectoverview.buildGUI_ProjectOverview(_passedRoot, _passedProjectState)


#
# Redraw Calls
#

def multiRedrawFileUpdate() -> None:
	global _objFileStr, _objSampleVar, _tagLists, _groupnameList

	# Exclusively for file update
	redrawFilestr(_objFileStr)
	redrawSamplevar(_objSampleVar)
	redrawNamingFrame(_tagLists)

	redrawNamingStatus(_groupnameList)


def multiRedrawNameUpdate() -> None:
	global _groupnameList

	redrawNamingStatus(_groupnameList)


def redrawFilestr(objFileStr: str) -> None:
	'''
		Updates the label for the file path string
	'''
	prevStr = ""

	if objFileStr == None:
		prevStr = "Select a file"
	else:
		prevStr = objFileStr
		if len(prevStr) > WIDTH_BIG:
			prevStr = "... " + prevStr[4-WIDTH_BIG:]

	_lblObjFile['text'] = prevStr


def redrawSamplevar(objSampleVar: str) -> None:
	'''
		Updates the label for the sample variable	
	'''
	prevStr = objSampleVar if objSampleVar != None else "Select a file"
	_lblLoadedSampleVar['text'] = prevStr


def redrawNamingFrame(tagLists: List[List[str]]) -> None:
	'''
		Rebuilds the frame for naming tag groups
	'''
	global _frmNameGroups, _nameEntVarList

	if _nameEntVarList == None:
		_nameEntVarList = []

	for child in _frmNameGroups.winfo_children():
		child.destroy()

	if _errWithObjFile:
		lblMessage = tk.Label(_frmNameGroups, text=_errWithObjFile, anchor="center")
		lblMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
	elif tagLists == None:
		lblMessage = tk.Label(_frmNameGroups, text="Select a file", anchor="center")
		lblMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
	else:
		if len(_nameEntVarList) > len(tagLists):
			_nameEntVarList = _nameEntVarList[:len(tagLists)]
		_nameEntVarList = _nameEntVarList + \
			[None] * (len(tagLists) - len(_nameEntVarList))

		for ind, exampleMems in enumerate(tagLists):
			strVarGroupname = _nameEntVarList[ind]
			if strVarGroupname == None:
				strVarGroupname = tk.StringVar()
				strVarGroupname.trace("w", lambda name, index, mode,
				                      sv=strVarGroupname: updateGroupName())
				_nameEntVarList[ind] = strVarGroupname

			entMemName = tk.Entry(_frmNameGroups, width=15, textvariable=strVarGroupname)

			exampleMemsStr = ", ".join(exampleMems)
			if len(exampleMemsStr) > WIDTH_BIG:
				exampleMemsStr = exampleMemsStr[:WIDTH_BIG - 4] + " ..."
			lblExampleMems = tk.Label(_frmNameGroups, text=exampleMemsStr, anchor="e")

			entMemName.grid(row=ind+1, column=0, padx=5, pady=5, sticky="nse")
			lblExampleMems.grid(row=ind+1, column=1, padx=5, pady=5, sticky="nsw")


def redrawNamingStatus(inputNames: List[str]) -> None:
	global _lblVerifyNames, _errWithNamesList, _errWithObjFile

	if inputNames == None or _errWithObjFile != None:
		_lblVerifyNames['text'] = ''
		_btnNextStage['state'] = 'disabled'
	elif _errWithNamesList == None:
		_lblVerifyNames['text'] = 'All tag group names valid'
		_btnNextStage['state'] = 'normal'
	else:
		_lblVerifyNames['text'] = "[[ Error ]]\n" + _errWithNamesList
		_btnNextStage['state'] = 'disabled'


#
# Main GUI Construction
#

def buildGUI_ObjImport(root: tk.Tk, projectState: models.ProjectState):
	global _btnNextStage, _passedRoot, _passedProjectState

	# Reading in references
	_passedRoot = root
	_passedProjectState = projectState

	# GUI Building
	root.title("Constraint Builder - Stage 1: Setup Variables")
	root.rowconfigure([1, 2], weight=1)
	root.columnconfigure(0, weight=1)

	lblHeader = tk.Label(root, text="Stage 1 - Variable Setup", anchor="center")
	lblHeader.grid(row=0, column=0, padx=10, pady=(10, 0))

	# File selection & parsing
	frmFileParseSetup = buildFileParseFrame(root)
	frmFileParseSetup.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

	# Tag gruop naming
	frmNameAndVerify = buildGroupNaming(root)
	frmNameAndVerify.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")

	# Next Step Button
	_btnNextStage = tk.Button(root, text="Continue >", anchor="center", command=transitionToOverview)
	_btnNextStage.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="e")

	multiRedrawFileUpdate()


def buildFileParseFrame(root: tk.Tk) -> tk.Frame:
	global _lblObjFile, _lblLoadedSampleVar, _cbbDelimSelector

	frmFileParseSetup = tk.Frame(root, relief=tk.RAISED, bd=2)

	btnObjFile = tk.Button(
		frmFileParseSetup, text="Objective .csv", command=updateNewObjFile)
	_lblObjFile = tk.Label(
		frmFileParseSetup, text="No file selected", width=WIDTH_BIG, anchor="w")
	btnObjFile.grid(row=0, column=0, sticky="nse", padx=5, pady=5)
	_lblObjFile.grid(row=0, column=1, sticky="nsw", padx=5, pady=5)

	lblSampleVar = tk.Label(frmFileParseSetup, text="Sample Variable:")
	# TODO: Italics
	_lblLoadedSampleVar = tk.Label(
		frmFileParseSetup, text="Load file for variable")
	lblSampleVar.grid(row=1, column=0, sticky="nse", padx=5, pady=5)
	_lblLoadedSampleVar.grid(row=1, column=1, sticky="nsw", padx=5, pady=5)

	lblDelim = tk.Label(frmFileParseSetup, text="Delimiter:")
	# TODO: Pull delimiters from program config
	_cbbDelimSelector = ttk.Combobox(frmFileParseSetup, values=('_', '-', '='))
	_cbbDelimSelector['state'] = 'readonly'
	lblDelim.grid(row=2, column=0, sticky="nse", padx=5, pady=5)
	_cbbDelimSelector.grid(row=2, column=1, sticky="nsw", padx=5, pady=5)

	_cbbDelimSelector.bind("<<ComboboxSelected>>", lambda evnt: updateNewDelim())

	return frmFileParseSetup


def buildGroupNaming(root: tk.Tk) -> tk.Frame:
	global _frmNameGroups, _lblVerifyNames

	frmNameAndVerify = tk.Frame(root, relief=tk.SUNKEN, bd=2)
	frmNameAndVerify.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
	frmNameAndVerify.columnconfigure(0, weight=1)

	# frmNameGroups is populated by the redraw methods
	_frmNameGroups = tk.Frame(frmNameAndVerify)
	_frmNameGroups.grid(row=0, column=0, columnspan=2, pady=10)
	_frmNameGroups.columnconfigure([0, 1], weight=1)

	lblNamesCol = tk.Label(_frmNameGroups, text="Name", anchor="center")
	lblExampleMemsCol = tk.Label(
		_frmNameGroups, text="Example Members", anchor="center")
	lblNamesCol.grid(row=0, column=0)
	lblExampleMemsCol.grid(row=0, column=1)

	_lblVerifyNames = tk.Label(
		frmNameAndVerify, text="Fill in group names", anchor="center")
	_lblVerifyNames.grid(row=2, column=0, padx=4, pady=5)

	return frmNameAndVerify


if __name__ == '__main__':
	projState = devtesting.dummyProjectState()
	root = tk.Tk()
	buildGUI_ObjImport(root, projState)
	root.mainloop()
