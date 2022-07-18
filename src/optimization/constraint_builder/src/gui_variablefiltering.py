
import copy
from enum import Enum
import random
import tkinter as tk
from tkinter import ttk
from typing import Dict, List

import proc_constraints as proc
import gui_projectoverview
import linting as lint
import models
from gui_consts import *
import devtesting
import proc_render as render



# Exposed GUI
_excLeftVarDict: Dict[str, tk.StringVar] = None
_excLeftLsbDict: Dict[str, tk.Listbox] = None
_incLeftVarDict: Dict[str, tk.StringVar] = None
_incLeftLsbDict: Dict[str, tk.Listbox] = None

_excRightVarDict: Dict[str, tk.StringVar] = None
_excRightLsbDict: Dict[str, tk.Listbox] = None
_incRightVarDict: Dict[str, tk.StringVar] = None
_incRightLsbDict: Dict[str, tk.Listbox] = None

_txtConstPreview: tk.Text = None
_btnContinue: tk.Button = None

_entPrefix: tk.Entry = None
_cbbOpSelector: ttk.Combobox = None
_entDefConst: tk.Entry = None
_entDefLeftCoef: tk.Entry = None
_entDefRightCoef: tk.Entry = None

_splitVarDict: Dict[str, tk.StringVar] = None

class Side(Enum):
	LEFT = 0
	RIGHT = 1

class IncExc(Enum):
	INC = 0
	EXC = 0

# LSB_LOOKUP[Side][Exclude?]
LSB_LOOKUP: Dict[Side, Dict[bool, Dict[str, tk.Listbox]]] = None

# State Variables
_varData: models.VarsData = None
_constrGroupSetup: models.SetupConstraintGroup = None

_errWithGeneralInfo: str = None

_passedProjectState: models.ProjectState = None
_passedRoot: tk.Tk = None
_passedConstrInd: int = -1






#
# Updates
#

def updateGeneralConstrInfo() -> None:
	'''
	Writes the current fields into the _constrGroupSetup object but only
	if valid, and checks for bad input
	'''
	global _errWithGeneralInfo, _constrGroupSetup

	print(" > In update general constr info")

	_errWithGeneralInfo = None

	# Prefix
	prefix = str(_entPrefix.get())
	prefixErr = lint.lintConstrGroupName(prefix)
	if prefixErr:
		_errWithGeneralInfo = prefixErr
	else:
		_constrGroupSetup.namePrefix = prefix
	
	# Comparison
	selector = _cbbOpSelector.get().strip()
	compType = models.ComparisonSign.fromSybols(selector)
	if compType == None:
		print(f'[[ !! Warning ]] Found illegal comparison selector option: "{selector}"')
	else:
		_constrGroupSetup.defComp = compType
	
	# Constant
	# TODO: Really this try / catch should be refactored into the linting file
	try:
		val = _entDefConst.get().strip()
		constant = float(val)
		_constrGroupSetup.defConstant = constant
	except:
		_errWithGeneralInfo = "Default constant is in an invalid number format"

	# Left Coefficient
	try:
		val = _entDefLeftCoef.get().strip()
		constant = float(val)
		_constrGroupSetup.defLeftCoef = constant
	except:
		_errWithGeneralInfo = "Default left coefficient is in an invalid number format"

	# Right Coefficient
	try:
		val = _entDefRightCoef.get().strip()
		constant = float(val)
		_constrGroupSetup.defRightCoef = constant
	except:
		_errWithGeneralInfo = "Default left coefficient is in an invalid number format"

	# Split-By Tags
	allTags = _varData.tag_order
	splitBys = []

	for tag in allTags:
		status = _splitVarDict[tag].get()
		if status == '1':
			splitBys.append(tag)
		elif status != '0':
			print(f"[[ !! Warning ]] Illegal state of checkbox string var found: {status}")
	_constrGroupSetup.splitBy = splitBys

	redrawForUpdate()


def updateMoveTags(tag:str, toExclude: bool, side: Side) -> None:
	DICT_LOOKUP = {
		Side.LEFT: _constrGroupSetup.selLeftTags,
		Side.RIGHT: _constrGroupSetup.selRightTags
	}

	lsb = LSB_LOOKUP[side][toExclude][tag]
	selectedItems = []
	selectedInds = lsb.curselection()
	for ind in selectedInds:
		selectedItems.append(lsb.get(ind))
	
	for item in selectedItems:
		if toExclude:
			DICT_LOOKUP[side][tag].remove(item)
		else:
			DICT_LOOKUP[side][tag].append(item)

	redrawForUpdate()










#
# Redraws
#

def redrawForSetup ():
	redrawGeneralInfoFrame()

	# Also in redrawForUpdate
	redrawIncExcLists()
	redrawPreviewBox()
	redrawContinueButton()


def redrawForUpdate ():
	redrawIncExcLists()
	redrawPreviewBox()
	redrawContinueButton()




def redrawGeneralInfoFrame ():
	# Tkinter is weird and this _must_ be the first thing to be updated
	for tag in _constrGroupSetup.splitBy:
		_splitVarDict[tag].set(1)

	_entPrefix.delete(0, tk.END)
	_entPrefix.insert(0, _constrGroupSetup.namePrefix)

	_cbbOpSelector.set(str(_constrGroupSetup.defComp.toSymbols()))

	_entDefConst.delete(0, tk.END)
	_entDefConst.insert(0, _constrGroupSetup.defConstant)

	_entDefRightCoef.delete(0, tk.END)
	_entDefRightCoef.insert(0, _constrGroupSetup.defRightCoef)

	_entDefLeftCoef.delete(0, tk.END)
	_entDefLeftCoef.insert(0, _constrGroupSetup.defLeftCoef)



def redrawIncExcLists ():
	# Left Side
	lIncTags = _constrGroupSetup.selLeftTags

	lExcTags = copy.deepcopy(_varData.tag_members)
	for tagGroup in _varData.tag_order:
		for mem in lIncTags[tagGroup]:
			if mem in lExcTags[tagGroup]:
				lExcTags[tagGroup].remove(mem)

	for tagGroup in lIncTags:
		incVar = _incLeftVarDict[tagGroup]
		excVar = _excLeftVarDict[tagGroup]

		incVar.set(lIncTags[tagGroup])
		excVar.set(lExcTags[tagGroup])

	# Right Side
	rIncTags = _constrGroupSetup.selRightTags

	rExcTags = copy.deepcopy(_varData.tag_members)
	for tagGroup in _varData.tag_order:
		for mem in rIncTags[tagGroup]:
			if mem in rExcTags[tagGroup]:
				rExcTags[tagGroup].remove(mem)
	
	for tagGroup in rIncTags:
		incVar = _incRightVarDict[tagGroup]
		excVar = _excRightVarDict[tagGroup]

		incVar.set(rIncTags[tagGroup])
		excVar.set(rExcTags[tagGroup])


def redrawPreviewBox ():
	global _txtConstPreview

	print("(from gui) Redrawing preview box")

	constrStr = None
	
	if _errWithGeneralInfo:
		constrStr = _errWithGeneralInfo
	else:
		constGroup = proc.buildConstraintGroup(_constrGroupSetup, _varData)
		constrStr = render.renderConstraintGroup(constGroup, _varData.delim)

	_txtConstPreview.delete("1.0", tk.END)
	_txtConstPreview.insert("1.0", constrStr)


def redrawContinueButton ():
	global _btnContinue

	if _errWithGeneralInfo:
		_btnContinue['state'] = 'disabled'
	else:
		_btnContinue['state'] = 'normal'





#
# Transitions
#

# TODO
def transitionToFineTune ():
	return


def transitionToOverview ():
	global _passedRoot, _passedProjectState
	print("Going to overview")

	# Update State
	_passedProjectState.setupList[_passedConstrInd] = _constrGroupSetup

	# Clear Root
	for child in _passedRoot.winfo_children():
		child.destroy()

	# Transition
	gui_projectoverview.buildGUI_ProjectOverview(_passedRoot, _passedProjectState)



#
# GUI Constructions
#

def buildGUI_VariableFiltering(root: tk.Tk, projState: models.ProjectState, constrInd: int):
	global _passedRoot, _passedProjectState, _passedConstrInd, _btnContinue, _varData, _constrGroupSetup, LSB_LOOKUP

	_passedRoot = root
	_passedProjectState = projState
	_passedConstrInd = constrInd

	_varData = projState.varData
	_constrGroupSetup = projState.setupList[constrInd]

	root.title("NJDEP Constraint Builder - Variable Filtering")
	root.rowconfigure([3,5], weight=1)
	root.columnconfigure([0, 1], weight=1)

	lblHeader = tk.Label(root, text="Variable Filtering", anchor="center")
	lblHeader.grid(row=0, column=0, padx=10, pady=(10, 0), columnspan=2)

	frmGenInfo = buildGeneralInfoFrame(root, _passedProjectState.varData)
	frmGenInfo.grid(row=1, column=0, padx=10, pady=(0, 10), columnspan=2)

	# TODO: If side by side is too much, stack vertically
	frmLeftVars = buildLeftSelectingFrame(root, _passedProjectState.varData)
	frmLeftVars.grid(row=2, column=0, padx=10, pady=(0, 10))

	frmRightVars = buildRightSelectingFrame(root, _passedProjectState.varData)
	frmRightVars.grid(row=2, column=1, padx=10, pady=(0, 10))

	frmPrevConsts = buildPreviewFrame(root)
	frmPrevConsts.grid(row=3, padx=10, pady=(0, 10), columnspan=2, sticky="nsew")

	# Next Step Button
	frmExportOptions = tk.Frame(root)
	frmExportOptions.grid(row=4, column=0, sticky="new", columnspan=2)
	frmExportOptions.rowconfigure(0, weight=1)
	frmExportOptions.columnconfigure(0, weight=1)

	_btnContinue = tk.Button(frmExportOptions, text="< Overview", anchor="center", command=transitionToOverview)
	_btnContinue.grid(row=0, column=0, padx=10, pady=10, sticky="w")


	# Important for State
	LSB_LOOKUP = {
		Side.RIGHT: {
			True: _excRightLsbDict,
			False: _incRightLsbDict
		},
		Side.LEFT: {
			True: _excLeftLsbDict,
			False: _incLeftLsbDict
		}
	}

	redrawForSetup()




# TODO: Refactor this to be less repeated
def buildLeftSelectingFrame(root: tk.Tk, varData: models.VarsData) -> tk.Frame:
	global _incLeftVarDict, _excLeftVarDict, _incLeftLsbDict, _excLeftLsbDict
	TAG_GROUPS_PER_ROW = 3

	_incLeftVarDict = {}
	_excLeftVarDict = {}

	_incLeftLsbDict = {}
	_excLeftLsbDict = {}

	tagGroupsList = varData.tag_order

	frmVariableSelecting = ttk.LabelFrame(root, relief=tk.RAISED, borderwidth=2, text="Left Side Variables")

	# Bro ngl I have no idea what this thing is doing
	numCols = len(tagGroupsList) * 2
	frmVariableSelecting.columnconfigure([x for x in range(numCols)], weight=1)

	for ind, tagGroup in enumerate(tagGroupsList):
		frmTagSel = tk.Frame(frmVariableSelecting)
		frmTagSel.grid(
			row=ind//TAG_GROUPS_PER_ROW, 
			column=ind%TAG_GROUPS_PER_ROW, 
			padx=10, 
			sticky="new"
			)

		lblTagGroup = tk.Label(frmTagSel, text=tagGroup, anchor="center")
		lblTagGroup.grid(row=0, column=0, columnspan=2)

		# Excluded
		lblExcluded = tk.Label(frmTagSel, text=f"Excluded")
		lblExcluded.grid(row=1, column=0, padx=10)

		exListVar = tk.StringVar(value=[]) # Empty Lists for skeleton building
		lsbExcluded = tk.Listbox(frmTagSel, listvariable=exListVar, width=WIDTH_SML)
		lsbExcluded['selectmode'] = 'extended'
		lsbExcluded.grid(row=2, column=0, padx=10)

		# Buttons for excluded panel
		frmExSelButtons = tk.Frame(frmTagSel)
		frmExSelButtons.rowconfigure(0, weight=1)
		frmExSelButtons.grid(row=3, column=0, pady=5)

		btnExSelectAll = tk.Button(frmExSelButtons, text="Select All")
		btnExTransfer = tk.Button(
			frmExSelButtons, 
			text="->", 
			command=lambda tagGroup=tagGroup: updateMoveTags(
				tag=tagGroup, 
				toExclude=False, 
				side=Side.LEFT
				)
			)
		# btnExSelectAll.grid(row=0, column=0, sticky="w")
		btnExTransfer.grid(row=0, column=1, sticky="e")

		# Included
		lblIncluded = tk.Label(frmTagSel, text=f"Included")
		lblIncluded.grid(row=1, column=1, padx=10)

		incListVar = tk.StringVar(value=[])
		lsbIncluded = tk.Listbox(frmTagSel, listvariable=incListVar, width=WIDTH_SML)
		lsbIncluded['selectmode'] = 'extended'
		lsbIncluded.grid(row=2, column=1, padx=10)

		# Buttons for included panel
		frmIncSelButtons = tk.Frame(frmTagSel)
		frmIncSelButtons.rowconfigure(0, weight=1)
		frmIncSelButtons.grid(row=3, column=1, pady=5)

		btnIncTransfer = tk.Button(
			frmIncSelButtons, 
			text="<-",
			command=lambda tagGroup=tagGroup: updateMoveTags(
				tag=tagGroup, 
				toExclude=True, 
				side=Side.LEFT
				)
			)
		btnIncSelectAll = tk.Button(frmIncSelButtons, text="Select All")
		btnIncTransfer.grid(row=0, column=0, sticky="w")
		# btnIncSelectAll.grid(row=0, column=1, sticky="e")

		# Adding to global refernces
		# TODO: Figure out why these are backwards ??
		_incLeftLsbDict[tagGroup] = lsbExcluded
		_excLeftLsbDict[tagGroup] = lsbIncluded

		# TODO: Figure out why these are backwards ??
		_incLeftVarDict[tagGroup] = incListVar
		_excLeftVarDict[tagGroup] = exListVar

	return frmVariableSelecting



# TODO: Refactor this to be less repeated
def buildRightSelectingFrame(root: tk.Tk, varData: models.VarsData) -> tk.Frame:
	global _incRightVarDict, _incRightLsbDict, _excRightLsbDict, _excRightVarDict
	TAG_GROUPS_PER_ROW = 3

	_incRightVarDict = {}
	_excRightVarDict = {}

	_incRightLsbDict = {}
	_excRightLsbDict = {}

	tagGroupsList = varData.tag_order

	frmVariableSelecting = ttk.LabelFrame(root, relief=tk.RAISED, borderwidth=2, text="Right Side Variables")

	# Bro ngl I have no idea what this thing is doing
	numCols = len(tagGroupsList) * 2
	frmVariableSelecting.columnconfigure([x for x in range(numCols)], weight=1)

	for ind, tagGroup in enumerate(tagGroupsList):
		frmTagSel = tk.Frame(frmVariableSelecting)
		frmTagSel.grid(
			row=ind//TAG_GROUPS_PER_ROW, 
			column=ind%TAG_GROUPS_PER_ROW, 
			padx=10, 
			sticky="new"
			)

		lblTagGroup = tk.Label(frmTagSel, text=tagGroup, anchor="center")
		lblTagGroup.grid(row=0, column=0, columnspan=2)

		# Excluded
		lblExcluded = tk.Label(frmTagSel, text=f"Excluded")
		lblExcluded.grid(row=1, column=0, padx=10)

		exListVar = tk.StringVar(value=[]) # Empty Lists for skeleton building
		lsbExcluded = tk.Listbox(frmTagSel, listvariable=exListVar, width=WIDTH_SML)
		lsbExcluded['selectmode'] = 'extended'
		lsbExcluded.grid(row=2, column=0, padx=10)

		# Buttons for excluded panel
		frmExSelButtons = tk.Frame(frmTagSel)
		frmExSelButtons.rowconfigure(0, weight=1)
		frmExSelButtons.grid(row=3, column=0, pady=5)

		btnExSelectAll = tk.Button(frmExSelButtons, text="Select All")
		btnExTransfer = tk.Button(
			frmExSelButtons, 
			text="->", 
			# See https://stackoverflow.com/questions/7546285/creating-lambda-inside-a-loop
			command=lambda tagGroup=tagGroup: updateMoveTags(
				tag=tagGroup, 
				toExclude=False,
				side=Side.RIGHT
				)
			)
		# btnExSelectAll.grid(row=0, column=0, sticky="w")
		btnExTransfer.grid(row=0, column=1, sticky="e")

		# Included
		lblIncluded = tk.Label(frmTagSel, text=f"Included")
		lblIncluded.grid(row=1, column=1, padx=10)

		incListVar = tk.StringVar(value=[])
		lsbIncluded = tk.Listbox(frmTagSel, listvariable=incListVar, width=WIDTH_SML)
		lsbIncluded['selectmode'] = 'extended'
		lsbIncluded.grid(row=2, column=1, padx=10)

		# Buttons for included panel
		frmIncSelButtons = tk.Frame(frmTagSel)
		frmIncSelButtons.rowconfigure(0, weight=1)
		frmIncSelButtons.grid(row=3, column=1, pady=5)

		btnIncTransfer = tk.Button(
			frmIncSelButtons, 
			text="<-",
			command=lambda tagGroup=tagGroup: updateMoveTags(
				tag=tagGroup, 
				toExclude=True,
				side=Side.RIGHT
				)
			)
		btnIncSelectAll = tk.Button(frmIncSelButtons, text="Select All")
		btnIncTransfer.grid(row=0, column=0, sticky="w")
		# btnIncSelectAll.grid(row=0, column=1, sticky="e")

		# Adding to global refernces
		# TODO: Figure out why these are backwards ??
		_incRightLsbDict[tagGroup] = lsbExcluded
		_excRightLsbDict[tagGroup] = lsbIncluded

		# TODO: Figure out why these are backwards ??
		_incRightVarDict[tagGroup] = incListVar
		_excRightVarDict[tagGroup] = exListVar

	return frmVariableSelecting


def buildPreviewFrame(root: tk.Tk):
	global _txtConstPreview

	frmConstPreview = tk.Frame(root)
	frmConstPreview.rowconfigure(1, weight=1)
	frmConstPreview.columnconfigure(0, weight=1)

	lblConstPreview = tk.Label(frmConstPreview, text="Preview Constraints")
	_txtConstPreview = tk.Text(frmConstPreview, height=6)
	lblConstPreview.grid(row=0, column=0, sticky="wn", padx=10)
	_txtConstPreview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 20))

	return frmConstPreview
	
	
def buildGeneralInfoFrame(root: tk.Tk, varData: models.VarsData) -> tk.Frame:
	global _entPrefix, _cbbOpSelector, _entDefConst, _entDefLeftCoef, _entDefRightCoef, _splitVarDict

	frmGenConInfo = ttk.Labelframe(root, relief=tk.RAISED, borderwidth=2, text="General Info")
	frmGenConInfo.columnconfigure([0, 1], weight=1)

	frmSingleFields = tk.Frame(frmGenConInfo)
	frmSingleFields.grid(row=0, column=0, sticky="nsew")

	# Name / Prefix
	varName = tk.StringVar()
	lblName = tk.Label(frmSingleFields, text="Name Prefix:")
	_entPrefix = tk.Entry(frmSingleFields, width=WIDTH_MED, textvariable=varName)
	lblName.grid(row=0, column=0, padx=5, pady=5, sticky="nse")
	_entPrefix.grid(row=0, column=1, padx=5, pady=5, sticky="nsw")

	# Comparison Type
	lblOpType = tk.Label(frmSingleFields, text="Comparison Type:")
	_cbbOpSelector = ttk.Combobox(
		frmSingleFields, 
		width=WIDTH_MED,
		values=tuple([x.toSymbols() for x in models.ComparisonSign])
		)
	_cbbOpSelector['state'] = 'readonly'
	lblOpType.grid(row=1, column=0, padx=5, pady=5, sticky="nse")
	_cbbOpSelector.grid(row=1, column=1, padx=5, pady=5, sticky="nsw")

	# Constant
	varDefaultConst = tk.StringVar()
	lblDefConst = tk.Label(frmSingleFields, text="Constant:")
	_entDefConst = tk.Entry(frmSingleFields, width=WIDTH_MED, textvariable=varDefaultConst)
	lblDefConst.grid(row=2, column=0, padx=5, pady=5, sticky="nse")
	_entDefConst.grid(row=2, column=1, padx=5, pady=5, sticky="nsw")

	# Left Side Coef
	varDefLeftCoef = tk.StringVar()
	lblDefLeftCoef = tk.Label(frmSingleFields, text="Left-Side Coefficients:")
	_entDefLeftCoef = tk.Entry(frmSingleFields, width=WIDTH_MED, textvariable=varDefLeftCoef)
	lblDefLeftCoef.grid(row=3, column=0, padx=5, pady=5, sticky="nse")
	_entDefLeftCoef.grid(row=3, column=1, padx=5, pady=5, sticky="nsw")

	# Right Side Coef
	varDefRightCoef = tk.StringVar()
	lblDefRightCoef = tk.Label(frmSingleFields, text="Right-Side Coefficients:")
	_entDefRightCoef = tk.Entry(frmSingleFields, width=WIDTH_MED, textvariable=varDefRightCoef)
	lblDefRightCoef.grid(row=4, column=0, padx=5, pady=5, sticky="nse")
	_entDefRightCoef.grid(row=4, column=1, padx=5, pady=5, sticky="nsw")

	# Event bindings for single fields
	varName.trace("w", lambda name, index, mode, sv=varName: updateGeneralConstrInfo())
	_cbbOpSelector.bind("<<ComboboxSelected>>", lambda evnt: updateGeneralConstrInfo())
	varDefaultConst.trace("w", lambda name, index, mode, sv=varDefaultConst: updateGeneralConstrInfo())
	varDefRightCoef.trace("w", lambda name, index, mode, sv=varDefRightCoef: updateGeneralConstrInfo())
	varDefLeftCoef.trace("w", lambda name, index, mode, sv=varDefLeftCoef: updateGeneralConstrInfo())

	# Split by
	frmSplitBy = tk.Frame(frmGenConInfo)
	frmSplitBy.grid(row=0, column=1, padx=10, sticky="nsew")

	lblSplitBy = tk.Label(frmSplitBy, text="Split by Tags", anchor="w")
	lblSplitBy.grid(row=0, column=0, sticky="w")

	_splitVarDict = {}

	for ind, tag in enumerate(varData.tag_order):
		varCkb = tk.StringVar(value='0')
		ckbGroupSplit = tk.Checkbutton(frmSplitBy, text=tag, variable=varCkb)
		ckbGroupSplit.grid(row=ind+1, column=0, sticky="w")

		varCkb.trace("w", lambda name, index, mode, sv=varCkb: updateGeneralConstrInfo())
		_splitVarDict[tag] = varCkb

	return frmGenConInfo





if __name__ == '__main__':
	projState = devtesting.dummyProjectState()

	root = tk.Tk()
	buildGUI_VariableFiltering(root, projState, 0)
	root.mainloop()

