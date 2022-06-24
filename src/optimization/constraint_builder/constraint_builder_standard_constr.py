
import tkinter as tk
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


# TODO: Make this read from a VarTagsInfo
# TODO: Make this output a StandardConstraintGroup

# Exposed GUI elements
_incLsbDict: Dict[str, tk.Listbox] = None
_excLsbDict: Dict[str, tk.Listbox] = None

_incVarDict: Dict[str, tk.StringVar] = None
_excVarDict: Dict[str, tk.StringVar] = None

_txtConstPreview: tk.Text = None

_entName: tk.Entry = None
_cbbOpSelector: ttk.Combobox = None
_entDefaultValue: tk.Entry = None

_splitVarDict: Dict[str, tk.StringVar] = None


# State Variables
_varTagsInfo = None
_constrGroup = None

_passedProjectState: models.ProjectState = None
_passedRoot: tk.Tk = None
_passedConstrInd: int = 0


#
# Update Calls
#

def updateGeneralConstrInfo():
	global _constrGroup, _varTagsInfo

	# Name is always just a string cast
	# TODO: Lint
	_constrGroup.name = str(_entName.get())

	# Selector needs to be checked
	selector = _cbbOpSelector.get().strip()
	compType = None

	# TODO: Move this conversion to the comparison sign class
	if selector == '=':
		compType = models.ComparisonSign.EQ
	elif selector == '<=':
		compType = models.ComparisonSign.LE
	elif selector == '>=':
		compType = models.ComparisonSign.GE
	else:
		print(f'[[ !! Warning ]] Found illegal comparison selector option: "{selector}"')

	if compType:
		_constrGroup.default_compare = compType
	
	# Value needs to be checked
	value = _entDefaultValue.get()
	convertedValue = None

	try:
		convertedValue = float(value.strip())
	except:
		pass	
	
	if convertedValue != None:
		_constrGroup.default_value = convertedValue
	
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
	constraint_builder_project_overview.buildProjectOverviewGUI(_passedRoot, _passedProjectState)






#
# Redraw Calls
#

def redrawAll(varTags: models.VarTagsInfo, constr: models.StandardConstraintGroup) -> None:
	redrawStandardInfo(constr)
	redrawSplitByGroups(constr)

	# These are the ones in redrawForUpdate
	redrawIncExcLists(varTags, constr)
	redrawPreviewConstraints(varTags, constr)


def redrawForUpdate(varTags: models.VarTagsInfo, constr: models.StandardConstraintGroup) -> None:
	redrawIncExcLists(varTags, constr)
	redrawPreviewConstraints(varTags, constr)


def redrawStandardInfo(constr: models.StandardConstraintGroup) -> None:
	'''
		Redraws the constraint name, comparison, and default operator in the top settings pane
	'''
	_entName.delete(0, tk.END)
	_entName.insert(0, constr.name)

	_cbbOpSelector.set(str(constr.default_compare))

	_entDefaultValue.delete(0, tk.END)
	_entDefaultValue.insert(0, constr.default_value)


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

	allConstrs = proc.compileStandardConstraintGroup(varTags, constr)

	if len(allConstrs) > 0:
		constrStr = generate_sample_constraint_string(allConstrs, -1, -1)
	else:
		constrStr = "No Constraint Exist"

	_txtConstPreview.delete("1.0", tk.END)
	_txtConstPreview.insert("1.0", constrStr)


# TODO: Actually use charHeight & charWidth ?
def generate_sample_constraint_string(constrList: List[models.CompiledConstraint], charHeight:int, charWidth: int) -> str:
	# TODO: Make this simpler
	NUM_CONSTRS = 5
	constrs = constrList[:NUM_CONSTRS]

	finalStr = ''

	for constr in constrs:
		varStrList = []
		for ind, varTags in enumerate(constr.var_tags):
			# TODO: Use some kind of rendering class / methods??
			coeff = constr.var_coeffs[ind]
			varStr = "_".join(varTags)

			if abs(coeff - 1.0) > 0.005:
				varStr = str(round(coeff, 2)) + "*" + varStr

			varStrList.append(varStr)	
		varsStr = " + ".join(varStrList)

		rightHandStr = str(constr.compare_type) + " " + str(constr.compare_value)

		finalStr += constr.name + ":" + "\n" 
		finalStr += varsStr + " " + rightHandStr + "\n"
		finalStr += "\n"

	return finalStr


def redrawIncExcLists(varTags: models.VarTagsInfo, constr: models.StandardConstraintGroup) -> None:
	includedTags = constr.selected_tags
	excludedTags = copy.deepcopy(varTags.tag_groups)

	for tagGroup in includedTags:
		for tag in includedTags[tagGroup]:
			if tag in excludedTags[tagGroup]:
				excludedTags[tagGroup].remove(tag)

	for tagGroup in includedTags:
		incVar = _incVarDict[tagGroup]
		excVar = _excVarDict[tagGroup]

		incVar.set(includedTags[tagGroup])
		excVar.set(excludedTags[tagGroup])








#
# Main GUI Construction
#

def buildConstraintBuildingGUI(root: tk.Tk, projectState: models.ProjectState, constrInd: int):
	global _varTagsInfo, _constrGroup, _passedRoot, _passedProjectState, _passedConstrInd

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

	btnNextStep = tk.Button(frmExportOptions, text="< Back to Overview", anchor="center", command=transitionToOverview)
	btnNextStep.grid(row=0, column=0, padx=10, pady=10, sticky="w")


	print("\n === Now at Standard Constraint Overview === \n")
	redrawAll(_varTagsInfo, _constrGroup)
	updateGeneralConstrInfo()


def buildGeneralConstraintFrame(root: tk.Tk) -> tk.Frame:
	global _entName, _cbbOpSelector, _entDefaultValue

	frmGenConInfo = tk.Frame(root, relief=tk.RAISED, borderwidth=2)

	varName = tk.StringVar()
	lblName = tk.Label(frmGenConInfo, text="Constraint Name:")
	_entName = tk.Entry(frmGenConInfo, width=WIDTH_BIG, textvariable=varName)
	lblName.grid(row=0, column=0, padx=5, pady=5, sticky="nse")
	_entName.grid(row=0, column=1, padx=5, pady=5, sticky="nsw")

	varName.trace("w", lambda name, index, mode, sv=varName: updateGeneralConstrInfo())

	lblOpType = tk.Label(frmGenConInfo, text="Default Operator Type:")
	# TODO: Pull operator types from global config
	_cbbOpSelector = ttk.Combobox(frmGenConInfo, values=('>=', '<=', '='))
	_cbbOpSelector['state'] = 'readonly'
	lblOpType.grid(row=1, column=0, padx=5, pady=5, sticky="nse")
	_cbbOpSelector.grid(row=1, column=1, padx=5, pady=5, sticky="nsw")

	_cbbOpSelector.bind("<<ComboboxSelected>>", lambda evnt: updateGeneralConstrInfo())

	varDefaultValue = tk.StringVar()
	lblDefaultValue = tk.Label(frmGenConInfo, text="Default Value:")
	_entDefaultValue = tk.Entry(frmGenConInfo, width=WIDTH_MED, textvariable=varDefaultValue)
	lblDefaultValue.grid(row=2, column=0, padx=5, pady=5, sticky="nse")
	_entDefaultValue.grid(row=2, column=1, padx=5, pady=5, sticky="nsw")

	varDefaultValue.trace("w", lambda name, index, mode, sv=varDefaultValue: updateGeneralConstrInfo())

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
	root = tk.Tk()
	projectState = models.ProjectState()
	buildConstraintBuildingGUI(root, 0)
	root.mainloop()
