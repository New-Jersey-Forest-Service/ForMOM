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



@unique
class OBJFileImportStage (Enum):
	FILE_IMPORTING = auto()
	TAG_NAMING = auto()
	DONE = auto()


objFileImportStage = OBJFileImportStage.FILE_IMPORTING

inFilePathStr = ''
inDelim = ''

importErrMsg = ''
tagGroupSamples = []
inTagGroupNames = []

namesErrMsg = ''


# Model state (Non-GUI)
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


def selectObjFile():
	global inFilePathStr, varNamesRaw

	filePath, success = selectFileAndUpdateLabel(lblObjFile, CSV_FILES)
	if not success:
		return
	
	inFilePathStr = filePath

	varNamesRaw = proc.readAllObjVarnames(filePath)
	lblLoadedSampleVar.config(text=varNamesRaw[0])

	processObjFileIfPossible()


def selectDelimiter():
	global inDelim

	inDelim = cbbDelimSelector.get()

	processObjFileIfPossible()


def processObjFileIfPossible():
	global arrEntSpecies
	for child in frmNameGroups.winfo_children():
		child.destroy()
	arrEntSpecies = []

	btnVerifyNames['state'] = 'disable'

	if inDelim == '' or inFilePathStr == '':
		# Cannot process objFile - make frame say that
		lblEmptyMessage = tk.Label(frmNameGroups, text="Select an objective file and delimiter")
		lblEmptyMessage.grid(row=0, column=0)
		return

	errMsg = proc.lintVarNames(varNamesRaw, inDelim)
	if errMsg != None:
		lblError = tk.Label(frmNameGroups, text=f"[[ XX Error ]]\n{errMsg}")
		lblError.grid(row=0, column=0)
		return
	
	# No errors, lets process and print the bad boi
	varnameTags = proc.splitVarsToTags(varNamesRaw, inDelim)
	tagGroupMembersList = proc.makeTagGroupMembersList(varnameTags)


	lblNamesCol = tk.Label(frmNameGroups, text="Name", anchor="center")
	lblExampleMemsCol = tk.Label(frmNameGroups, text="Example Members", anchor="center")
	lblNamesCol.grid(row=0, column=0)
	lblExampleMemsCol.grid(row=0, column=1)

	for ind, exampleGroup in enumerate(tagGroupMembersList):
		entMemName = tk.Entry(frmNameGroups, width=15)
		arrEntSpecies.append(entMemName)

		exampleMemsStr = ", ".join(exampleGroup)
		if len(exampleMemsStr) > WIDTH_BIG:
			exampleMemsStr = exampleMemsStr[:WIDTH_BIG - 4] + " ..."
		lblExampleMems = tk.Label(frmNameGroups, text=exampleMemsStr, anchor="e")

		entMemName.grid(row=ind+1, column=0, padx=5, pady=5, sticky="nse")
		lblExampleMems.grid(row=ind+1, column=1, padx=5, pady=5, sticky="nsw")
	
	btnVerifyNames['state'] = 'normal'
	


def processTaggroupNames():
	global arrEntSpecies, lblNameErrors, btnNextStage

	btnNextStage['state'] = 'disable'

	tagGroupNames = []
	errMsg = None

	for ent in arrEntSpecies:
		tagGroupNames.append(ent.get())
		errMsg = proc.lintTagGroupName(ent.get())
		if errMsg:
			break
	
	if errMsg:
		lblNameErrors['text'] = f'[[ XX Error ]] {errMsg}'
		return

	lblNameErrors['text'] = f'[[ ~~ Sucess ]] group names are vaild'
	btnNextStage['state'] = 'normal'



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

	if isInvalidFile(objFileStr):
		lbl.config(text="No file selected")
		return '', False

	lbl.config(text=shrinkPathString(objFileStr))
	return str(objFileStr), True


def isInvalidFile(dialogOutput) -> bool:
	# For whatever reason, filedialog.askname() can return multiple different things ???
	return dialogOutput == None  \
		or len(dialogOutput) == 0  \
		or dialogOutput.strip() == ""


def shrinkPathString(pathstr: str) -> str:
	pathstr = str(pathstr)
	if len(pathstr) <= WIDTH_BIG:
		return pathstr
	else:
		return '...' + pathstr[3 - WIDTH_BIG:]




def build_stage_1():
	global lblObjFile, lblLoadedSampleVar, cbbDelimSelector, frmNameGroups, btnNextStage, btnVerifyNames, lblNameErrors

	root = tk.Tk()
	root.title("Constraint Builder - Stage 1: Setup Variables")
	root.rowconfigure([1, 2], weight=1)
	root.columnconfigure(0, weight=1)

	# Header Text
	lblHeader = tk.Label(root, text="Stage 1 - Variable Setup", anchor="center")
	lblHeader.grid(row=0, column=0, padx=10, pady=(10, 0))

	#
	# Top half - selecting & parsing the obj file
	frmFileParseSetup = tk.Frame(root, relief=tk.RAISED, bd=2)
	frmFileParseSetup.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

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

	#
	# Bottom half - naming tag groups
	frmNameAndVerify = tk.Frame(root, relief=tk.SUNKEN, bd=2)
	frmNameAndVerify.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
	frmNameAndVerify.columnconfigure(0, weight=1)

	frmNameGroups = tk.Frame(frmNameAndVerify)
	frmNameGroups.grid(row=0, column=0, columnspan=2, pady=10)
	frmNameGroups.columnconfigure([0, 1], weight=1)

	# The list of tag groups & text entries is handled by a function automatically
	btnVerifyNames = tk.Button(frmNameAndVerify, text="Verify Group Names", command=processTaggroupNames)
	lblNameErrors = tk.Label(frmNameAndVerify, text="...", anchor="center")
	btnVerifyNames.grid(row=2, column=0, padx=5, pady=5)
	lblNameErrors.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

	#
	# Next Step Button
	btnNextStage = tk.Button(root, text="Continue >", anchor="center")
	btnNextStage.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="e")

	processObjFileIfPossible()
	root.mainloop()


	pass





if __name__ == '__main__':
	build_stage_1()