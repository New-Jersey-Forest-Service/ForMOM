
import tkinter as tk
import varname_dataclasses as models
import constraint_processer as proc
import copy
from enum import Enum, unique, auto
from typing import List, Union, Dict
from tkinter import ttk, filedialog
import math


WIDTH_SML = 8
WIDTH_MED = 15
WIDTH_BIG = 35
CSV_FILES = [('CSV Files', '*.csv'), ('All Files', '*.*')]


# TODO: Make this read from a VarTagsInfo
# TODO: Make this output a StandardConstraintGroup

# TODO: Go eat a second dinner after finishing this file


# Exposed GUI elements
incLsbDict: Dict[str, tk.Listbox] = None
excLsbDict: Dict[str, tk.Listbox] = None

incVarDict: Dict[str, tk.StringVar] = None
excVarDict: Dict[str, tk.StringVar] = None

txtConstPreview: tk.Text = None


# Exposed State
varTagsInfo = None
constrAllBySpeciesByYear = None



#
# Update Calls
#

def updateAddToIncTags(tagGroup: str):
	global constrAllBySpeciesByYear, varTagsInfo

	lsb = incLsbDict[tagGroup]

	selectedItems = []
	selectedInds = lsb.curselection()
	for ind in selectedInds:
		selectedItems.append(lsb.get(ind))

	for item in selectedItems:
		constrAllBySpeciesByYear.selected_tags[tagGroup].append(item)

	redrawAll(varTagsInfo, constrAllBySpeciesByYear)


def updateTakeFromIncTags(tagGroup: str):
	global constrAllBySpeciesByYear, varTagsInfo

	lsb = excLsbDict[tagGroup]

	selectedItems = []
	selectedInds = lsb.curselection()
	for ind in selectedInds:
		selectedItems.append(lsb.get(ind))

	for item in selectedItems:
		constrAllBySpeciesByYear.selected_tags[tagGroup].remove(item)

	# TODO: reset selection (and for the other update method)
	
	redrawAll(varTagsInfo, constrAllBySpeciesByYear)






#
# Redraw Calls
#

def redrawAll(varTags: models.VarTagsInfo, constr: models.StandardConstraintGroup):
	redrawIncExcLists(varTags, constr)
	redrawPreviewConstraints(varTags, constr)


def redrawPreviewConstraints(varTags: models.VarTagsInfo, constr: models.StandardConstraintGroup):
	global txtConstPreview

	allConstrs = proc.compileStandardConstraintGroup(varTags, constr)
	constrStr = generate_sample_constraint_string(allConstrs, -1, -1)

	txtConstPreview.delete("1.0", tk.END)
	txtConstPreview.insert("1.0", constrStr)


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


def redrawIncExcLists(varTags: models.VarTagsInfo, constr: models.StandardConstraintGroup):
	includedTags = constr.selected_tags
	excludedTags = copy.deepcopy(varTags.tag_groups)

	for tagGroup in includedTags:
		for tag in includedTags[tagGroup]:
			if tag in excludedTags[tagGroup]:
				excludedTags[tagGroup].remove(tag)

	for tagGroup in includedTags:
		incVar = incVarDict[tagGroup]
		excVar = excVarDict[tagGroup]

		incVar.set(includedTags[tagGroup])
		excVar.set(excludedTags[tagGroup])








#
# Main GUI Construction
#

def buildConstraintBuildingGUI(root: tk.Tk):
	global varTagsInfo, constrAllBySpeciesByYear
	global txtConstPreview


	#
	# Sample Data Used
	rawNames = proc.readAllObjVarnames(
		'/home/velcro/Documents/Professional/NJDEP/TechWork/ForMOM/src/optimization/constraint_builder/sample_data/minimodel_obj.csv'
	)
	varTagsInfo = proc.makeVarTagsInfoObject(rawNames, '_', ['species', 'year', 'management'])

	constrAllBySpeciesByYear = models.StandardConstraintGroup(
		selected_tags = {
			"species": ["167N", "409"], 
			"year": ["2021", "2050"], 
			"management": ["PLSQ", "PLWF"]},
		split_by_groups = ["species", "year"],
		name = "All"
	)



	root.title("Constraint Builder - Stage 2: Standard Constraint Building")
	root.rowconfigure([3,5], weight=1)
	root.columnconfigure(0, weight=1)

	lblHeader = tk.Label(root, text="Stage 2 - Standard Constraint Building", anchor="center")
	lblHeader.grid(row=0, column=0, padx=10, pady=(10, 0))

	# General Constraint Info
	frmGenConInfo = buildGeneralConstraintFrame(root)
	frmGenConInfo.grid(row=1, column=0, padx=10, pady=10)

	# Variable Selecting
	frmVariableSelecting = buildVarSelectingFrame(root, varTagsInfo)
	frmVariableSelecting.grid(row=2, column=0, padx=10, pady=(5, 10))

	# Split by Groups
	frmSplitBy = buildSplitByFrame(root, varTagsInfo)
	frmSplitBy.grid(row=4, column=0, padx=10, pady=(5, 10))

	# Constraint Previews
	frmConstPreview = buildConstrPreviewFrame(root)
	frmConstPreview.grid(row=5, column=0, sticky="nsew")

	# Next Step Button
	btnNextStep = tk.Button(root, text="Fine Tune >", anchor="center")
	btnNextStep.grid(row=6, column=0, padx=10, pady=10, sticky="e")


	redrawAll(varTagsInfo, constrAllBySpeciesByYear)



def buildGeneralConstraintFrame(root: tk.Tk) -> tk.Frame:
	frmGenConInfo = tk.Frame(root, relief=tk.RAISED, borderwidth=2)

	lblName = tk.Label(frmGenConInfo, text="Constraint Name:")
	entName = tk.Entry(frmGenConInfo, width=WIDTH_BIG)
	lblName.grid(row=0, column=0, padx=5, pady=5, sticky="nse")
	entName.grid(row=0, column=1, padx=5, pady=5, sticky="nsw")

	lblOpType = tk.Label(frmGenConInfo, text="Default Operator Type:")
	cbbOpSelector = ttk.Combobox(frmGenConInfo, values=('>', '<', '='))
	cbbOpSelector['state'] = 'readonly'
	lblOpType.grid(row=1, column=0, padx=5, pady=5, sticky="nse")
	cbbOpSelector.grid(row=1, column=1, padx=5, pady=5, sticky="nsw")
	
	lblDefaultValue = tk.Label(frmGenConInfo, text="Default Value:")
	entDefaultValue = tk.Entry(frmGenConInfo, width=WIDTH_MED)
	lblDefaultValue.grid(row=2, column=0, padx=5, pady=5, sticky="nse")
	entDefaultValue.grid(row=2, column=1, padx=5, pady=5, sticky="nsw")

	return frmGenConInfo


def buildVarSelectingFrame(root: tk.Tk, varTagsInfo: models.VarTagsInfo) -> tk.Frame:
	global incVarDict, excVarDict, incLsbDict, excLsbDict
	TAG_GROUPS_PER_ROW = 3

	incVarDict = {}
	excVarDict = {}

	incLsbDict = {}
	excLsbDict = {}

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
		incLsbDict[tagGroup] = lsbExcluded
		excLsbDict[tagGroup] = lsbIncluded

		# TODO: Figure out why these are backwards ??
		incVarDict[tagGroup] = incListVar
		excVarDict[tagGroup] = exListVar

	return frmVariableSelecting


def buildSplitByFrame(root, varTagsInfo: models.VarTagsInfo) -> tk.Frame:
	frmSplitBy = tk.Frame(root, relief=tk.RAISED, borderwidth=2)
	frmSplitBy.rowconfigure(0, weight=1)

	lblSplitBy = tk.Label(frmSplitBy, text="Split by")
	lblSplitBy.grid(row=0, column=0)
	frmSplitByBoxes = tk.Frame(frmSplitBy)
	frmSplitByBoxes.rowconfigure(0, weight=1)
	frmSplitByBoxes.grid(row=0, column=1)

	for ind, varGroup in enumerate(varTagsInfo.tag_order):
		ckbGroupSplit = tk.Checkbutton(frmSplitByBoxes, text=varGroup)
		ckbGroupSplit.grid(row=0, column=ind, padx=5)

	return frmSplitBy


def buildConstrPreviewFrame(root) -> tk.Frame:
	global txtConstPreview

	frmConstPreview = tk.Frame(root)
	frmConstPreview.rowconfigure(1, weight=1)
	frmConstPreview.columnconfigure(0, weight=1)

	lblConstPreview = tk.Label(frmConstPreview, text="Preview Constraints")
	txtConstPreview = tk.Text(frmConstPreview, height=6)
	lblConstPreview.grid(row=0, column=0, sticky="wn", padx=10)
	txtConstPreview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 20))

	return frmConstPreview




if __name__ == '__main__':
	root = tk.Tk()
	buildConstraintBuildingGUI(root)
	root.mainloop()
