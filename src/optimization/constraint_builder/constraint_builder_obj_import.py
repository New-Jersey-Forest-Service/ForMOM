import tkinter as tk
import varname_dataclasses as models
import constraint_processer as proc
from enum import Enum, unique, auto
from typing import List, Union
from tkinter import ttk, filedialog
import math




WIDTH_SML = 8
WIDTH_MED = 15
WIDTH_BIG = 35
CSV_FILES = [('CSV Files', '*.csv'), ('All Files', '*.*')]



# Model State
inFilePathStr = ''
inDelim = ''

importErrMsg = ''
tagGroupSamples = []
inTagGroupNames = []

namesErrMsg = ''

varNamesRaw: List[str] = []


# All the tkinter components that need to be exposed
lblObjFile = None
lblLoadedSampleVar = None
cbbDelimSelector = None
frmNameGroups = None
btnNextStage = None
btnVerifyNames = None
lblNameErrors = None
arrEntSpecies: List[tk.Entry] = []



#
# High Level GUI Calls
#

def updateGUIToMatchState():
	'''
	This function updates the entire gui based on the current
	state. It essentially replaces and all buttons come through here.
	'''

	btnVerifyNames['state'] = 'disable'
	btnNextStage['state'] = 'disable'

	# Stage 1 - Objective File Selection
	objFileSelected = doObjFileSetup()		
	btnVerifyNames['state'] = 'normal'

	# Stage 2 - Filling in Names of Tag Groups
	groupsNamed = doNamingCheck()
	btnNextStage['state'] = 'normal'


def doObjFileSetup() -> bool:
	'''
	Returns true if the objective file has been selected and parsed
	without error.
	'''
	global arrEntSpecies

	for child in frmNameGroups.winfo_children():
		child.destroy()
	arrEntSpecies = []

	if inDelim == '' or inFilePathStr == '':
		# Cannot process objFile - make frame say that
		lblEmptyMessage = tk.Label(frmNameGroups, text="Select an objective file and delimiter")
		lblEmptyMessage.grid(row=0, column=0)
		return False

	errMsg = proc.lintVarNames(varNamesRaw, inDelim)
	if errMsg != None:
		lblError = tk.Label(frmNameGroups, text=f"[[ XX Error ]]\n{errMsg}")
		lblError.grid(row=0, column=0)
		return False
	
	# No errors, lets process and fill out the frame
	varnameTags = proc.splitVarsToTags(varNamesRaw, inDelim)
	tagGroupMembersList = proc.makeTagGroupMembersList(varnameTags)

	fillTagGroupNamingFrame(tagGroupMembersList, frmNameGroups)

	return True


def doNamingCheck() -> bool:
	return True


#
# Stage 1 Bindings

def selectObjFile():
	global inFilePathStr, varNamesRaw

	filePath, success = selectFileAndUpdateLabel(lblObjFile, CSV_FILES)
	if not success:
		inFilePathStr = None
	else:	
		inFilePathStr = filePath
		varNamesRaw = proc.readAllObjVarnames(filePath)
		lblLoadedSampleVar.config(text=varNamesRaw[0])

	updateGUIToMatchState()


def selectDelimiter():
	global inDelim
	inDelim = cbbDelimSelector.get()

	updateGUIToMatchState()



#
# Stage 2 Bindings

def processTagGroupNames():
	'''
	Reads the names of the tag groups and lints them
	'''
	global arrEntSpecies, lblNameErrors

	tagGroupNames = []
	errMsg = None

	for ent in arrEntSpecies:
		tagGroupNames.append(ent.get())
		errMsg = proc.lintTagGroupName(ent.get())
		if errMsg:
			break
	
	if errMsg:
		lblNameErrors['text'] = f'[[ XX Error ]]\n{errMsg}'
	else:
		lblNameErrors['text'] = f'[[ ~~ Sucess ]]\ngroup names are vaild'

	updateGUIToMatchState()






#
# GUI Update Commands
#

def selectFileAndUpdateLabel(lbl, fileTypes) -> Union[str, bool]:
	'''
		Select a file with a chooser
		Update the provided label with the file path

		Returns two variables
		 - filepath (str) ; Never none
		 - succesful (bool) ; true = success
	'''
	objFileStr = filedialog.askopenfilename(
		filetypes=fileTypes,
		defaultextension=fileTypes
		)
	
	isInvalidFile = \
		   objFileStr == None \
		or len(objFileStr) == 0 \
		or type(objFileStr) != str \
		or objFileStr.strip() == ''

	if isInvalidFile:
		lbl.config(text="No file selected")
		return '', False

	lbl.config(text=truncateString(objFileStr))
	return str(objFileStr), True


def truncateString(givenStr: str) -> str:
	givenStr = str(givenStr)
	if len(givenStr) <= WIDTH_BIG:
		return givenStr
	else:
		return '...' + givenStr[3 - WIDTH_BIG:]


def fillTagGroupNamingFrame(tagGroupMemberLists: List[List[str]], frm: tk.Frame) -> None:
	lblNamesCol = tk.Label(frm, text="Name", anchor="center")
	lblExampleMemsCol = tk.Label(frm, text="Example Members", anchor="center")
	lblNamesCol.grid(row=0, column=0)
	lblExampleMemsCol.grid(row=0, column=1)

	for ind, exampleGroup in enumerate(tagGroupMemberLists):
		entMemName = tk.Entry(frm, width=15)
		arrEntSpecies.append(entMemName)

		exampleMemsStr = ", ".join(exampleGroup)
		if len(exampleMemsStr) > WIDTH_BIG:
			exampleMemsStr = exampleMemsStr[:WIDTH_BIG - 4] + " ..."
		lblExampleMems = tk.Label(frm, text=exampleMemsStr, anchor="e")

		entMemName.grid(row=ind+1, column=0, padx=5, pady=5, sticky="nse")
		lblExampleMems.grid(row=ind+1, column=1, padx=5, pady=5, sticky="nsw")






#
# GUI Building Commands
#

def buildFileImport(root: tk.Tk) -> tk.Frame:
	global lblObjFile, lblLoadedSampleVar, cbbDelimSelector, frmNameGroups, btnNextStage, btnVerifyNames, lblNameErrors

	frmFileParseSetup = tk.Frame(root, relief=tk.RAISED, bd=2)

	btnObjFile = tk.Button(frmFileParseSetup, text="Objective .csv", command=selectObjFile)
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
	# TODO: Delimiters are radio buttons ?
	cbbDelimSelector = ttk.Combobox(frmFileParseSetup, values=('_', '-', '='))
	cbbDelimSelector['state'] = 'readonly'
	lblDelim.grid(row=2, column=0, sticky="nse", padx=5, pady=5)
	cbbDelimSelector.grid(row=2, column=1, sticky="nsw", padx=5, pady=5)

	cbbDelimSelector.bind("<<ComboboxSelected>>", lambda evnt: selectDelimiter())

	return frmFileParseSetup


def buildTagGroupFrame(root: tk.Tk) -> tk.Frame:
	global lblObjFile, lblLoadedSampleVar, cbbDelimSelector, frmNameGroups, btnNextStage, btnVerifyNames, lblNameErrors

	frmNameAndVerify = tk.Frame(root, relief=tk.SUNKEN, bd=2)
	frmNameAndVerify.columnconfigure(0, weight=1)

	frmNameGroups = tk.Frame(frmNameAndVerify)
	frmNameGroups.grid(row=0, column=0, columnspan=2, pady=10)
	frmNameGroups.columnconfigure([0, 1], weight=1)

	# The list of tag groups & text entries is handled by a function automatically
	btnVerifyNames = tk.Button(frmNameAndVerify, text="Verify Group Names", command=processTagGroupNames)
	lblNameErrors = tk.Label(frmNameAndVerify, text="...", anchor="center")
	btnVerifyNames.grid(row=2, column=0, padx=5, pady=5)
	lblNameErrors.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

	return frmNameAndVerify


def buildObjectiveFileImport(root: tk.Tk):
	global lblObjFile, lblLoadedSampleVar, cbbDelimSelector, frmNameGroups, btnNextStage, btnVerifyNames, lblNameErrors

	root.title("Constraint Builder - Stage 1: Setup Variables")
	root.rowconfigure([1, 2], weight=1)
	root.columnconfigure(0, weight=1)

	lblHeader = tk.Label(root, text="Stage 1 - Variable Setup", anchor="center")
	lblHeader.grid(row=0, column=0, padx=10, pady=(10, 0))

	frmFileImport = buildFileImport(root)
	frmFileImport.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

	frmNameAndVerify = buildTagGroupFrame(root)
	frmNameAndVerify.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")

	btnNextStage = tk.Button(root, text="Continue >", anchor="center")
	btnNextStage.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="e")

	updateGUIToMatchState()





if __name__ == '__main__':
	root = tk.Tk()
	buildObjectiveFileImport(root)
	root.mainloop()
