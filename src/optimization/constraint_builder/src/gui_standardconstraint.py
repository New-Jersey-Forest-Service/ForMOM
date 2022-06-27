
import copy
import csv
import math
from pathlib import Path
import traceback
import tkinter as tk
from enum import Enum, auto, unique
from tkinter import filedialog, ttk
from typing import Dict, List, Union

import constraintprocesser as proc
import gui_projectoverview
import linting as lint
import models
from gui_consts import *

# TODO: Make this read from a VarTagsInfo
# TODO: Make this output a StandardConstraintGroup

# Exposed GUI elements
_incLsbDict: Dict[str, tk.Listbox] = None
_excLsbDict: Dict[str, tk.Listbox] = None

_incVarDict: Dict[str, tk.StringVar] = None
_excVarDict: Dict[str, tk.StringVar] = None

_txtConstPreview: tk.Text = None

_entPrefix: tk.Entry = None
_cbbOpSelector: ttk.Combobox = None
_entDefaultRtside: tk.Entry = None
_entDefaultCoef: tk.Entry = None

_btnBackToOverview: tk.Button = None

_splitVarDict: Dict[str, tk.StringVar] = None


# State Variables
_varTagsInfo = None
_constrGroup: models.StandardConstraintGroup = None

_errWithGeneralInfo: str = None

_passedProjectState: models.ProjectState = None
_passedRoot: tk.Tk = None
_passedConstrInd: int = 0


#
# Update Calls
#

def updateGeneralConstrInfo():
	global _constrGroup, _varTagsInfo, _errWithGeneralInfo

	_errWithGeneralInfo = None

	# Name is always just a string cast
	# TODO: Lint
	prefix = str(_entPrefix.get())
	prefixErr = lint.lintConstrGroupName(prefix)
	if prefixErr:
		_errWithGeneralInfo = prefixErr
	else:
		_constrGroup.constr_prefix = prefix

	# Selector needs to be checked
	selector = _cbbOpSelector.get().strip()
	compType = models.ComparisonSign.fromSybols(selector)
	if compType == None:
		print(f'[[ !! Warning ]] Found illegal comparison selector option: "{selector}"')
	else:
		_constrGroup.default_compare = compType
	
	# Right side value
	try:
		rightSide = _entDefaultRtside.get().strip()
		convertedValue = float(rightSide)
		_constrGroup.default_rightside = convertedValue
	except:
		_errWithGeneralInfo = "Invalid right-hand side"

	# Default coefficient
	try:
		coeff = _entDefaultCoef.get().strip()
		attemptConvert = float(coeff)
		_constrGroup.default_coef = attemptConvert
	except:
		_errWithGeneralInfo = "Invalid coefficient"

	redrawForUpdate(_varTagsInfo, _constrGroup)


def updateSplitByGroups():
	global _constrGroup, _varTagsInfo

	allGroups = _varTagsInfo.tag_order
	splitBys = []

	for group in allGroups:
		status = _splitVarDict[group].get()

		if status == '1':
			splitBys.append(group)	
		elif status != '0':
			print(f"[[ !! Warning ]] Illegal state of checkbox string var found: {status}")

	_constrGroup.split_by_groups = splitBys

	redrawForUpdate(_varTagsInfo, _constrGroup)


def updateAddToIncTags(tagGroup: str):
	global _constrGroup, _varTagsInfo

	lsb = _incLsbDict[tagGroup]

	selectedItems = []
	selectedInds = lsb.curselection()
	for ind in selectedInds:
		selectedItems.append(lsb.get(ind))

	for item in selectedItems:
		_constrGroup.selected_tags[tagGroup].append(item)

	redrawForUpdate(_varTagsInfo, _constrGroup)


def updateTakeFromIncTags(tagGroup: str):
	global _constrGroup, _varTagsInfo

	lsb = _excLsbDict[tagGroup]

	selectedItems = []
	selectedInds = lsb.curselection()
	for ind in selectedInds:
		selectedItems.append(lsb.get(ind))

	for item in selectedItems:
		_constrGroup.selected_tags[tagGroup].remove(item)

	# TODO: reset selection (and for the other update method)
	
	redrawForUpdate(_varTagsInfo, _constrGroup)







#
# Transition Calls
#

def transitionToOverview() -> None:
	global _constrGroup, _passedConstrInd, _passedRoot, _passedProjectState

	# Update State
	_passedProjectState.constrGroupList[_passedConstrInd] = _constrGroup

	# Reset root
	for child in _passedRoot.winfo_children():
		child.destroy()

	# Transition
	gui_projectoverview.buildProjectOverviewGUI(_passedRoot, _passedProjectState)






#
# Redraw Calls
#

def redrawForSetup(varTags: models.VarTagsInfo, constr: models.StandardConstraintGroup) -> None:
	redrawStandardInfo(constr)
	redrawSplitByGroups(constr)

	redrawForUpdate(varTags, constr)


def redrawForUpdate(varTags: models.VarTagsInfo, constr: models.StandardConstraintGroup) -> None:
	redrawIncExcLists(varTags, constr)
	redrawPreviewConstraints(varTags, constr)
	redrawExitButton()


def redrawStandardInfo(constr: models.StandardConstraintGroup) -> None:
	'''
		Redraws the constraint name, comparison, and default operator in the top settings pane
	'''
	_entPrefix.delete(0, tk.END)
	_entPrefix.insert(0, constr.constr_prefix)

	_cbbOpSelector.set(str(constr.default_compare.toSymbols()))

	_entDefaultRtside.delete(0, tk.END)
	_entDefaultRtside.insert(0, constr.default_rightside)

	_entDefaultCoef.delete(0, tk.END)
	_entDefaultCoef.insert(0, constr.default_coef)


def redrawSplitByGroups(constr: models.StandardConstraintGroup) -> None:
	'''
		Redraws the split by group check buttons
	'''
	splitbyGroups = constr.split_by_groups

	for group in splitbyGroups:
		_splitVarDict[group].set(1)
	# TODO: Also set the splitbys outside the group to 0


def redrawPreviewConstraints(varTags: models.VarTagsInfo, constr: models.StandardConstraintGroup) -> None:
	global _txtConstPreview

	constrStr = None

	if _errWithGeneralInfo:
		constrStr = _errWithGeneralInfo
	else:
		allConstrs = proc.buildConstraintsFromStandardConstraintGroup(varTags, constr)

		if len(allConstrs) > 0:
			constrStr = generate_sample_constraint_string(allConstrs, -1, -1)
		else:
			constrStr = "No Constraints Exist"

	_txtConstPreview.delete("1.0", tk.END)
	_txtConstPreview.insert("1.0", constrStr)


# TODO: Actually use charHeight & charWidth ?
def generate_sample_constraint_string(constrList: List[models.CompiledConstraint], charHeight:int, charWidth: int) -> str:
	NUM_CONSTRS = 5
	constrs = constrList[:NUM_CONSTRS]

	finalStr = ''

	for constr in constrs:
		varStrList = []
		for ind, varTags in enumerate(constr.var_tags):
			# TODO: Use some kind of rendering class / methods??
			coeff = constr.var_coeffs[ind]
			varStr = "_".join(varTags) # Eww stinky! "_" should be replaced with some type of delimiter string

			if coeff == 1:
				pass
			elif coeff == int(coeff):
				varStr = str(int(coeff)) + "*" + varStr
			else:
				varStr = str(coeff) + "*" + varStr

			varStrList.append(varStr)	
		varsStr = " + ".join(varStrList)

		rightHandStr = str(constr.compare_type.toSymbols()) + " " + str(constr.compare_value)

		finalStr += constr.name + ":" + "\n" 
		finalStr += varsStr + " " + rightHandStr + "\n"
		finalStr += "\n"

	return finalStr


def redrawIncExcLists(varTags: models.VarTagsInfo, constr: models.StandardConstraintGroup) -> None:
	includedTags = constr.selected_tags
	excludedTags = copy.deepcopy(varTags.tag_members)

	for tagGroup in includedTags:
		for tag in includedTags[tagGroup]:
			if tag in excludedTags[tagGroup]:
				excludedTags[tagGroup].remove(tag)

	for tagGroup in includedTags:
		incVar = _incVarDict[tagGroup]
		excVar = _excVarDict[tagGroup]

		incVar.set(includedTags[tagGroup])
		excVar.set(excludedTags[tagGroup])


def redrawExitButton() -> None:
	global _btnBackToOverview

	if _errWithGeneralInfo:
		_btnBackToOverview['state'] = 'disabled'
	else:
		_btnBackToOverview['state'] = 'normal'






#
# Main GUI Construction
#

def buildConstraintBuildingGUI(root: tk.Tk, projectState: models.ProjectState, constrInd: int):
	global _varTagsInfo, _constrGroup, _passedRoot, _passedProjectState, _passedConstrInd, _btnBackToOverview

	_varTagsInfo = projectState.varTags
	_constrGroup = projectState.constrGroupList[constrInd]

	_passedRoot = root
	_passedProjectState = projectState
	_passedConstrInd = constrInd



	root.title("Constraint Builder - Stage 2: Standard Constraint Building")
	root.rowconfigure([3,5], weight=1)
	root.columnconfigure(0, weight=1)

	lblHeader = tk.Label(root, text="Stage 2 - Standard Constraint Building", anchor="center")
	lblHeader.grid(row=0, column=0, padx=10, pady=(10, 0))

	# General Constraint Info
	frmGenConInfo = buildGeneralConstraintFrame(root)
	frmGenConInfo.grid(row=1, column=0, padx=10, pady=10)

	# Variable Selecting
	frmVariableSelecting = buildVarSelectingFrame(root, _varTagsInfo)
	frmVariableSelecting.grid(row=2, column=0, padx=10, pady=(5, 10))

	# Split by Groups
	frmSplitBy = buildSplitByFrame(root, _varTagsInfo)
	frmSplitBy.grid(row=4, column=0, padx=10, pady=(5, 10))

	# Constraint Previews
	frmConstPreview = buildConstrPreviewFrame(root)
	frmConstPreview.grid(row=5, column=0, sticky="nsew")

	# Next Step Button
	frmExportOptions = tk.Frame(root)
	frmExportOptions.grid(row=6, column=0, sticky="new")
	frmExportOptions.rowconfigure(0, weight=1)
	frmExportOptions.columnconfigure(0, weight=1)

	_btnBackToOverview = tk.Button(frmExportOptions, text="< Back to Overview", anchor="center", command=transitionToOverview)
	_btnBackToOverview.grid(row=0, column=0, padx=10, pady=10, sticky="w")


	print("\n === Now at Standard Constraint Overview === \n")
	redrawForSetup(_varTagsInfo, _constrGroup)
	updateGeneralConstrInfo()


def buildGeneralConstraintFrame(root: tk.Tk) -> tk.Frame:
	global _entPrefix, _cbbOpSelector, _entDefaultRtside, _entDefaultCoef

	frmGenConInfo = tk.Frame(root, relief=tk.RAISED, borderwidth=2)

	varName = tk.StringVar()
	lblName = tk.Label(frmGenConInfo, text="Constraint Prefix:")
	_entPrefix = tk.Entry(frmGenConInfo, width=WIDTH_BIG, textvariable=varName)
	lblName.grid(row=0, column=0, padx=5, pady=5, sticky="nse")
	_entPrefix.grid(row=0, column=1, padx=5, pady=5, sticky="nsw")

	varName.trace("w", lambda name, index, mode, sv=varName: updateGeneralConstrInfo())

	lblOpType = tk.Label(frmGenConInfo, text="Default Operator Type:")
	# TODO: Pull operator types from global config
	_cbbOpSelector = ttk.Combobox(frmGenConInfo, values=tuple([x.toSymbols() for x in models.ComparisonSign]))
	_cbbOpSelector['state'] = 'readonly'
	lblOpType.grid(row=1, column=0, padx=5, pady=5, sticky="nse")
	_cbbOpSelector.grid(row=1, column=1, padx=5, pady=5, sticky="nsw")

	_cbbOpSelector.bind("<<ComboboxSelected>>", lambda evnt: updateGeneralConstrInfo())

	varDefaultRtside = tk.StringVar()
	lblDefaultRtside = tk.Label(frmGenConInfo, text="Default Right-Side:")
	_entDefaultRtside = tk.Entry(frmGenConInfo, width=WIDTH_MED, textvariable=varDefaultRtside)
	lblDefaultRtside.grid(row=2, column=0, padx=5, pady=5, sticky="nse")
	_entDefaultRtside.grid(row=2, column=1, padx=5, pady=5, sticky="nsw")

	varDefaultRtside.trace("w", lambda name, index, mode, sv=varDefaultRtside: updateGeneralConstrInfo())

	varDefaultCoef = tk.StringVar()
	lblDefaultCoef = tk.Label(frmGenConInfo, text="Default Coefficient:")
	_entDefaultCoef = tk.Entry(frmGenConInfo, width=WIDTH_MED, textvariable=varDefaultCoef)
	lblDefaultCoef.grid(row=3, column=0, padx=5, pady=5, sticky="nse")
	_entDefaultCoef.grid(row=3, column=1, padx=5, pady=5, sticky="nsw")

	varDefaultCoef.trace("w", lambda name, index, mode, sv=varDefaultCoef: updateGeneralConstrInfo())

	return frmGenConInfo


def buildVarSelectingFrame(root: tk.Tk, varTagsInfo: models.VarTagsInfo) -> tk.Frame:
	global _incVarDict, _excVarDict, _incLsbDict, _excLsbDict
	TAG_GROUPS_PER_ROW = 3

	_incVarDict = {}
	_excVarDict = {}

	_incLsbDict = {}
	_excLsbDict = {}

	tagGroupsList = varTagsInfo.tag_order

	frmVariableSelecting = tk.Frame(root, relief=tk.RAISED, borderwidth=2)
	frmVariableSelecting.rowconfigure([0, 1, 2, 3, 4, 5], weight=1) # TODO: If more than 5 rows

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
		lblExcluded = tk.Label(frmTagSel, text=f"Excluded {tagGroup}")
		lblExcluded.grid(row=1, column=0, padx=10)

		exListVar = tk.StringVar(value=[]) # Empty Lists for skeleton building
		lsbExcluded = tk.Listbox(frmTagSel, listvariable=exListVar, width=WIDTH_MED)
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
			command=lambda tagGroup=tagGroup: updateAddToIncTags(tagGroup)
			)
		# btnExSelectAll.grid(row=0, column=0, sticky="w")
		btnExTransfer.grid(row=0, column=1, sticky="e")

		# Included
		lblIncluded = tk.Label(frmTagSel, text=f"Included {tagGroup}")
		lblIncluded.grid(row=1, column=1, padx=10)

		incListVar = tk.StringVar(value=[])
		lsbIncluded = tk.Listbox(frmTagSel, listvariable=incListVar, width=WIDTH_MED)
		lsbIncluded['selectmode'] = 'extended'
		lsbIncluded.grid(row=2, column=1, padx=10)

		# Buttons for included panel
		frmIncSelButtons = tk.Frame(frmTagSel)
		frmIncSelButtons.rowconfigure(0, weight=1)
		frmIncSelButtons.grid(row=3, column=1, pady=5)

		btnIncTransfer = tk.Button(
			frmIncSelButtons, 
			text="<-",
			command =lambda tagGroup=tagGroup: updateTakeFromIncTags(tagGroup)
			)
		btnIncSelectAll = tk.Button(frmIncSelButtons, text="Select All")
		btnIncTransfer.grid(row=0, column=0, sticky="w")
		# btnIncSelectAll.grid(row=0, column=1, sticky="e")

		# Adding to global refernces
		# TODO: Figure out why these are backwards ??
		_incLsbDict[tagGroup] = lsbExcluded
		_excLsbDict[tagGroup] = lsbIncluded

		# TODO: Figure out why these are backwards ??
		_incVarDict[tagGroup] = incListVar
		_excVarDict[tagGroup] = exListVar

	return frmVariableSelecting


def buildSplitByFrame(root, varTagsInfo: models.VarTagsInfo) -> tk.Frame:
	global _splitVarDict

	_splitVarDict = {}

	frmSplitBy = tk.Frame(root, relief=tk.RAISED, borderwidth=2)
	frmSplitBy.rowconfigure(0, weight=1)

	lblSplitBy = tk.Label(frmSplitBy, text="Split by")
	lblSplitBy.grid(row=0, column=0)
	frmSplitByBoxes = tk.Frame(frmSplitBy)
	frmSplitByBoxes.rowconfigure(0, weight=1)
	frmSplitByBoxes.grid(row=0, column=1)

	for ind, varGroup in enumerate(varTagsInfo.tag_order):
		varCkb = tk.StringVar(value='0')
		ckbGroupSplit = tk.Checkbutton(frmSplitByBoxes, text=varGroup, variable=varCkb)
		ckbGroupSplit.grid(row=0, column=ind, padx=5)

		varCkb.trace("w", lambda name, index, mode, sv=varCkb: updateSplitByGroups())
		_splitVarDict[varGroup] = varCkb

	return frmSplitBy


def buildConstrPreviewFrame(root) -> tk.Frame:
	global _txtConstPreview

	frmConstPreview = tk.Frame(root)
	frmConstPreview.rowconfigure(1, weight=1)
	frmConstPreview.columnconfigure(0, weight=1)

	lblConstPreview = tk.Label(frmConstPreview, text="Preview Constraints")
	_txtConstPreview = tk.Text(frmConstPreview, height=6)
	lblConstPreview.grid(row=0, column=0, sticky="wn", padx=10)
	_txtConstPreview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 20))

	return frmConstPreview




if __name__ == '__main__':
	varnamesRaw = proc.readVarnamesRaw(
		# './sample_data/minimodel_obj.csv', 
		Path('/home/velcro/Documents/Professional/NJDEP/TechWork/ForMOM/src/optimization/constraint_builder/sample_data/minimodel_obj.csv')
	)

	varTagsInfo = proc.buildVarTagsInfoObject(
		varnamesRaw,
		'_', 
		['for_type', 'year', 'mng']
		)

	# TODO: To remove future polymorphism, add a general constriantinfo class ?
	constrGroupList: List[models.StandardConstraintGroup] = [
		models.StandardConstraintGroup(
			selected_tags={'for_type': ['167N', '167S', '409'], 'year': ["2021", "2025", "2030", "2050"], 'mng': ['RBWF', 'PLSQ', 'TB']},
			split_by_groups=['for_type'],
			constr_prefix="MaxAcresBySpecies",
			default_compare=models.ComparisonSign.EQ,
			default_rightside=0
		),
		models.StandardConstraintGroup.createEmptyConstraint(varTagsInfo)
	]

	projState = models.ProjectState(varTagsInfo, constrGroupList)

	root = tk.Tk()
	buildConstraintBuildingGUI(root, projState, 0)
	root.mainloop()
