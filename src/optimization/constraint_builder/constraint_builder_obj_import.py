'''
Constraint Builder Objective File Import
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


# Exposed gui elements / data
lblObjFile: tk.Label = None
lblLoadedSampleVar: tk.Label = None
cbbDelimSelector: ttk.Combobox = None

frmNameGroups: tk.Frame = None
lblVerifyNames: tk.Label = None

nameEntVarList: List[tk.StringVar] = None

btnNextStage: tk.Button = None


#
# Exposed State
objSampleVar: str = None
errWithObjFile: str = None
errWithNamesList: str = None

# user input
objFileStr: str = None
groupnameList: List[str] = None
delimiter: str = None

# useful processed values
varNamesRaw: List[str] = None
tagLists: List[List[str]] = None
# varTagsInfo = None





#
# Update Calls
#

def updateNewObjFile() -> None:
	'''
		Select objective csv with a chooser
	'''
	global objFileStr

	prevStr = objFileStr

	objFileStr = filedialog.askopenfilename(
		filetypes=CSV_FILES,
		defaultextension=CSV_FILES
		)

	if _isValidFile(objFileStr):
		objFileStr = str(objFileStr)
	else:
		objFileStr = prevStr
	
	processParseFile()
	multiRedrawFileUpdate()


def _isValidFile(dialogOutput) -> bool:
	# For whatever reason, filedialog.askname() can return multiple different things ???
	return dialogOutput != None and len(dialogOutput) > 0 and dialogOutput.strip() != ""


def updateNewDelim() -> None:
	global delimiter, cbbDelimSelector

	delimiter = cbbDelimSelector.get()

	processParseFile()
	multiRedrawFileUpdate()


def updateGroupName() -> None:
	'''
		Reads the groupname string variables
	'''
	global nameEntVarList, groupnameList, errWithNamesList

	groupnameList = [x.get() for x in nameEntVarList]
	errWithNamesList = proc.lintMultipleTagGroupNames(groupnameList)

	multiRedrawNameUpdate()




#
# Processing Calls
#

def processParseFile() -> None:
	global varNamesRaw, objSampleVar, errWithObjFile, tagLists

	varNamesRaw = None
	objSampleVar = None
	errWithObjFile = None
	tagLists = None

	if objFileStr == None:
		return
	# TODO: Lint file name (in processing module)
	varNamesRaw = proc.readAllObjVarnames(Path(objFileStr))
	objSampleVar = varNamesRaw[0]

	if delimiter == None:
		return
	errWithObjFile = proc.lintVarNames(varNamesRaw, delimiter)

	if errWithObjFile:
		return
	tagLists = proc.makeTagGroupMembersList(
		proc.splitVarsToTags(varNamesRaw, delimiter)
	)
	










#
# Redraw Calls
#

def multiRedrawFileUpdate() -> None:
	global objFileStr, objSampleVar, tagLists, groupnameList

	# Exclusively for file update	
	redrawFilestr(objFileStr)
	redrawSamplevar(objSampleVar)
	redrawNamingFrame(tagLists)

	redrawNamingStatus(groupnameList)


def multiRedrawNameUpdate() -> None:
	global groupnameList

	redrawNamingStatus(groupnameList)


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
	
	lblObjFile['text'] = prevStr


def redrawSamplevar(objSampleVar: str) -> None:
	'''
		Updates the label for the sample variable	
	'''
	prevStr = objSampleVar if objSampleVar != None else "Select a file"
	lblLoadedSampleVar['text'] = prevStr


def redrawNamingFrame(tagLists: List[List[str]]) -> None:
	'''
		Rebuilds the frame for naming tag groups
	'''
	global frmNameGroups, nameEntVarList

	if nameEntVarList == None:
		nameEntVarList = []

	for child in frmNameGroups.winfo_children():
		child.destroy()

	if errWithObjFile:
		lblMessage = tk.Label(frmNameGroups, text=errWithObjFile, anchor="center")
		lblMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
	elif tagLists == None:
		lblMessage = tk.Label(frmNameGroups, text="Select a file", anchor="center")
		lblMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
	else:
		if len(nameEntVarList) > len(tagLists):
			nameEntVarList = nameEntVarList[:len(tagLists)]
		nameEntVarList = nameEntVarList + [None] * (len(tagLists) - len(nameEntVarList))

		for ind, exampleMems in enumerate(tagLists):
			strVarGroupname = nameEntVarList[ind]
			if strVarGroupname == None:
				strVarGroupname = tk.StringVar()
				strVarGroupname.trace("w", lambda name, index, mode, sv=strVarGroupname: updateGroupName())
				nameEntVarList[ind] = strVarGroupname

			entMemName = tk.Entry(frmNameGroups, width=15, textvariable=strVarGroupname)

			exampleMemsStr = ", ".join(exampleMems)
			if len(exampleMemsStr) > WIDTH_BIG:
				exampleMemsStr = exampleMemsStr[:WIDTH_BIG - 4] + " ..."
			lblExampleMems = tk.Label(frmNameGroups, text=exampleMemsStr, anchor="e")

			entMemName.grid(row=ind+1, column=0, padx=5, pady=5, sticky="nse")
			lblExampleMems.grid(row=ind+1, column=1, padx=5, pady=5, sticky="nsw")


def redrawNamingStatus(inputNames: List[str]) -> None:
	global lblVerifyNames, errWithNamesList, errWithObjFile

	if inputNames == None or errWithObjFile != None:
		lblVerifyNames['text'] = ''
		btnNextStage['state'] = 'disabled'
	elif errWithNamesList == None:
		lblVerifyNames['text'] = 'All tag group names valid'
		btnNextStage['state'] = 'normal'
	else:
		lblVerifyNames['text'] = "[[ Error ]]\n" + errWithNamesList
		btnNextStage['state'] = 'disabled'
	







#
# Main GUI Construction
#

def buildObjImport(root: tk.Tk):
	global btnNextStage
	# Example data
	exampleGroupMembersStrs = [
		['167N', '167S', '409', '104'],
		['2021', '2025', '2030', '2050', '2075', '2100', '212314'],
		['SPB', 'NoMng', 'WFNM']
	]

	root.title("Constraint Builder - Stage 1: Setup Variables")
	root.rowconfigure([1, 2], weight=1)
	root.columnconfigure(0, weight=1)

	lblHeader = tk.Label(root, text="Stage 1 - Variable Setup", anchor="center")
	lblHeader.grid(row=0, column=0, padx=10, pady=(10, 0))

	# File selection & parsing
	frmFileParseSetup = buildFileParseFrame(root)
	frmFileParseSetup.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

	# Tag gruop naming
	frmNameAndVerify = buildGroupNaming(root, exampleGroupMembersStrs)
	frmNameAndVerify.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")

	# Next Step Button
	btnNextStage = tk.Button(root, text="Continue >", anchor="center")
	btnNextStage.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="e")

	multiRedrawFileUpdate()


def buildFileParseFrame(root: tk.Tk) -> tk.Frame:
	global lblObjFile, lblLoadedSampleVar, cbbDelimSelector

	frmFileParseSetup = tk.Frame(root, relief=tk.RAISED, bd=2)

	btnObjFile = tk.Button(frmFileParseSetup, text="Objective .csv", command=updateNewObjFile)
	lblObjFile = tk.Label(frmFileParseSetup, text="No file selected", width=WIDTH_BIG, anchor="w")
	btnObjFile.grid(row=0, column=0, sticky="nse", padx=5, pady=5)
	lblObjFile.grid(row=0, column=1, sticky="nsw", padx=5, pady=5)

	lblSampleVar = tk.Label(frmFileParseSetup, text="Sample Variable:")
	# TODO: Italics
	lblLoadedSampleVar = tk.Label(frmFileParseSetup, text="Load file for variable")
	lblSampleVar.grid(row=1, column=0, sticky="nse", padx=5, pady=5)
	lblLoadedSampleVar.grid(row=1, column=1, sticky="nsw", padx=5, pady=5)

	lblDelim = tk.Label(frmFileParseSetup, text="Delimiter:")
	# TODO: Pull delimiters from program config
	cbbDelimSelector = ttk.Combobox(frmFileParseSetup, values=('_', '-', '='))
	cbbDelimSelector['state'] = 'readonly'
	lblDelim.grid(row=2, column=0, sticky="nse", padx=5, pady=5)
	cbbDelimSelector.grid(row=2, column=1, sticky="nsw", padx=5, pady=5)

	cbbDelimSelector.bind("<<ComboboxSelected>>", lambda evnt: updateNewDelim())

	return frmFileParseSetup


def buildGroupNaming(root: tk.Tk, exampleTagsList: List[List[str]]) -> tk.Frame:
	global frmNameGroups, lblVerifyNames

	frmNameAndVerify = tk.Frame(root, relief=tk.SUNKEN, bd=2)
	frmNameAndVerify.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
	frmNameAndVerify.columnconfigure(0, weight=1)

	# frmNameGroups is populated by the redraw methods
	frmNameGroups = tk.Frame(frmNameAndVerify)
	frmNameGroups.grid(row=0, column=0, columnspan=2, pady=10)
	frmNameGroups.columnconfigure([0, 1], weight=1)

	lblNamesCol = tk.Label(frmNameGroups, text="Name", anchor="center")
	lblExampleMemsCol = tk.Label(frmNameGroups, text="Example Members", anchor="center")
	lblNamesCol.grid(row=0, column=0)
	lblExampleMemsCol.grid(row=0, column=1)

	lblVerifyNames = tk.Label(frmNameAndVerify, text="Fill in group names", anchor="center")
	lblVerifyNames.grid(row=2, column=0, padx=4, pady=5)

	return frmNameAndVerify








if __name__ == '__main__':
	root = tk.Tk()
	buildObjImport(root)
	root.mainloop()


