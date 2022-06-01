'''
Constraint Builder Gui

The front end for the constraint builder.

Michael Gorbunov
NJDEP 2022
'''

import tkinter as tk
import varname_dataclasses as models
from typing import List
from tkinter import ttk
import math


WIDTH_SML = 8
WIDTH_MED = 15
WIDTH_BIG = 35
CSV_FILES = [('CSV Files', '*.csv'), ('All Files', '*.*')]


# TODO: Learn about tkinter variables (as opposed to globals / state object)
#		 - Do they have support for undo / redos ?
#		 - Honestly they might be a horrible idea
# TODO: Use Label Frames
# TODO: Use frames to diplay coonstraints
# TODO: Remove colons ?

def main():
	build_stage_3()


def build_stage_3():
	root = tk.Tk()
	root.title("Constraint Builder - Stage 3: Coefficients")
	root.rowconfigure(2, weight=1)
	root.columnconfigure([0, 1], weight=1)

	# Header Text
	lblHeader = tk.Label(root, text="Stage 3 - Coefficients", anchor="center")
	lblHeader.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0))


	#
	# Apply to All Options
	frmApplyAll = tk.Frame(root, relief=tk.RAISED, borderwidth=2)
	frmApplyAll.grid(row=1, column=0, padx=10, pady=10)

	lblVarCoeff = tk.Label(frmApplyAll, text="Variable Coefficient")
	entVarCoeff = tk.Entry(frmApplyAll, width=WIDTH_SML)
	btnVarCoeff = tk.Button(frmApplyAll, text="Apply All")
	lblVarCoeff.grid(row=0, column=0, sticky="e")
	entVarCoeff.grid(row=0, column=1, sticky="w")
	btnVarCoeff.grid(row=0, column=2, sticky="e")

	lblOpSelector = tk.Label(frmApplyAll, text="Comparison Sign")
	cbbOpSelector = ttk.Combobox(frmApplyAll, values=('>', '<', '='), width=WIDTH_SML)
	cbbOpSelector['state'] = 'readonly'
	btnOpSelector = tk.Button(frmApplyAll, text="Apply All")
	lblOpSelector.grid(row=1, column=0, sticky="e")
	cbbOpSelector.grid(row=1, column=1, sticky="w")
	btnOpSelector.grid(row=1, column=2, sticky="e")

	lblValue = tk.Label(frmApplyAll, text="Right-side Value")
	entValue = tk.Entry(frmApplyAll, width=WIDTH_SML)
	btnValue = tk.Button(frmApplyAll, text="Apply All")
	lblValue.grid(row=2, column=0, sticky="e")
	entValue.grid(row=2, column=1, sticky="w")
	btnValue.grid(row=2, column=2, sticky="e")


	#
	# Fine Tune Options
	frmFineTune = tk.Frame(root, relief=tk.RAISED, borderwidth=2)
	frmFineTune.grid(row=1, column=1, padx=10, pady=10)

	lblRightSide = tk.Label(frmFineTune, text="Right-Side Only")
	btnRightSideExport = tk.Button(frmFineTune, text="Export Current")
	btnRightSideImport = tk.Button(frmFineTune, text="Import")
	lblRightSide.grid(row=0, column=0, sticky="e")
	btnRightSideExport.grid(row=0, column=1, sticky="ew")
	btnRightSideImport.grid(row=0, column=2, sticky="ew")

	lblEverything = tk.Label(frmFineTune, text="Everything")
	btnEverythingExport = tk.Button(frmFineTune, text="Export Current")
	btnEverythingImport = tk.Button(frmFineTune, text="Import")
	lblEverything.grid(row=1, column=0, sticky="e")
	btnEverythingExport.grid(row=1, column=1, sticky="ew")
	btnEverythingImport.grid(row=1, column=2, sticky="ew")


	#
	# Preview Constraints
	sampleConstraints = [
		models.CompiledConstraint(
			name='dummyName',
			var_tags=[
				['167N', '2021', 'SPB'],
				['167N', '2021', 'PLSQ'],
				['167N', '2021', 'PLWF']
			],
			var_coeffs = [
				1, 1, 1
			],
			compare_type = models.ComparisonSign.EQ,
			compare_value = 43.4
		),

		models.CompiledConstraint(
			name='dummyName_2',
			var_tags=[
				['167S', '2021', 'SPB'],
				['167N', '2025', 'PLWF'],
				['409', '2030', 'PLWF'],
				['167N', '2021', 'SPB'],
				['167N', '2021', 'PLSQ'],
				['167N', '2021', 'PLWF']
			],
			var_coeffs = [
				1, 1, 1, 1.5, 1, 1
			],
			compare_type = models.ComparisonSign.LE,
			compare_value = 3
		)
	]

	# TODO: Make this frame have a scroll bar
	frmPreviewConstr = tk.Frame(root)
	frmPreviewConstr.grid(row=3, column=0, columnspan=2, sticky="new")
	frmPreviewConstr.columnconfigure(1, weight=1)

	for row, constr in enumerate(sampleConstraints):

		varStrList = []
		for ind, varTags in enumerate(constr.var_tags):
			# TODO: Use some kind of rendering class / methods??
			coeff = constr.var_coeffs[ind]
			varStr = "_".join(varTags)

			if abs(coeff - 1.0) > 0.005:
				varStr = str(round(coeff, 2)) + " " + varStr

			varStrList.append(varStr)	
		varsStr = " + ".join(varStrList)

		lblName = tk.Label(frmPreviewConstr, text=constr.name)
		lblCoeffs = tk.Message(frmPreviewConstr, text=varsStr, justify="left", aspect=10000)
		lblCompare = tk.Label(frmPreviewConstr, text=str(constr.compare_type))
		lblRightSide = tk.Label(frmPreviewConstr, text=str(constr.compare_value))

		lblName.grid(row=row, column=0)
		lblCoeffs.grid(row=row, column=1, sticky="ew", pady=(10, 0))
		lblCompare.grid(row=row, column=2)
		lblRightSide.grid(row=row, column=3)


	#
	# Confirmation Button
	btnSaveConstr = tk.Button(root, text="Save Constraint")
	btnSaveConstr.grid(row=4, column=1, sticky="e")


	root.mainloop()


def build_stage_2():
	root = tk.Tk()
	root.title("Constraint Builder - Stage 2: Variable Selection")
	root.rowconfigure([3,5], weight=1)
	root.columnconfigure(0, weight=1)

	# Header Text
	lblHeader = tk.Label(root, text="Stage 2 - Variable Selection", anchor="center")
	lblHeader.grid(row=0, column=0, padx=10, pady=(10, 0))

	#
	# General Constraint Info
	frmGenConInfo = tk.Frame(root, relief=tk.RAISED, borderwidth=2)
	frmGenConInfo.grid(row=1, column=0, padx=10, pady=10)

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

	#
	# Variable Selecting
	varDict = {
		'species': ['167N', '167S', '409'], 
		'year': ['2021', '2025', '2030', '2050'], 
		'mng': ['PLSQ', 'PLWF', 'RBWF', 'RxB', 'SPB', 'SPWF', 'STQO', 'TB', 'TBWF', 'TRWF', 'TRxB', 'WFNM']
	}
	varTagGroups = ['species', 'year', 'mng']

	frmVariableSelecting = tk.Frame(root, relief=tk.RAISED, borderwidth=2)
	frmVariableSelecting.rowconfigure([0, 1, 2, 3, 4, 5], weight=1) # TODO: If more than 5 rows
	frmVariableSelecting.grid(row=2, column=0, padx=10, pady=(5, 10))

	TAG_GROUPS_PER_ROW = 3

	for ind, tagGroup in enumerate(varTagGroups):
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

		exListVar = tk.StringVar(value=varDict[tagGroup])
		lsbExcluded = tk.Listbox(frmTagSel, listvariable=exListVar, width=WIDTH_MED)
		lsbExcluded['selectmode'] = 'extended'
		lsbExcluded.grid(row=2, column=0, padx=10)

		# Buttons for excluded panel
		frmExSelButtons = tk.Frame(frmTagSel)
		frmExSelButtons.rowconfigure(0, weight=1)
		frmExSelButtons.grid(row=3, column=0, pady=5)

		btnExSelectAll = tk.Button(frmExSelButtons, text="All")
		btnExTransfer = tk.Button(frmExSelButtons, text="->")
		btnExSelectAll.grid(row=0, column=0, sticky="w")
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

		btnIncTransfer = tk.Button(frmIncSelButtons, text="<-")
		btnIncSelectAll = tk.Button(frmIncSelButtons, text="All")
		btnIncTransfer.grid(row=0, column=0, sticky="w")
		btnIncSelectAll.grid(row=0, column=1, sticky="e")


	#
	# Frame for the split by selection
	frmSplitBy = tk.Frame(root, relief=tk.RAISED, borderwidth=2)
	frmSplitBy.rowconfigure(0, weight=1)
	frmSplitBy.grid(row=4, column=0, padx=10, pady=(5, 10))

	lblSplitBy = tk.Label(frmSplitBy, text="Split by")
	lblSplitBy.grid(row=0, column=0)
	frmSplitByBoxes = tk.Frame(frmSplitBy)
	frmSplitByBoxes.rowconfigure(0, weight=1)
	frmSplitByBoxes.grid(row=0, column=1)

	for ind, varGroup in enumerate(varTagGroups):
		ckbGroupSplit = tk.Checkbutton(frmSplitByBoxes, text=varGroup)
		ckbGroupSplit.grid(row=0, column=ind, padx=5)


	#
	# Preview Constraints
	sampleConstraints = [
		models.CompiledConstraint(
			name='dummyName',
			var_tags=[
				['167N', '2021', 'SPB'],
				['167N', '2021', 'PLSQ'],
				['167N', '2021', 'PLWF']
			],
			var_coeffs = [
				1, 1, 1
			],
			compare_type = models.ComparisonSign.EQ,
			compare_value = 43.4
		),

		models.CompiledConstraint(
			name='dummyName_2',
			var_tags=[
				['167S', '2021', 'SPB'],
				['167N', '2025', 'PLWF'],
				['409', '2030', 'PLWF'],
				['167N', '2021', 'SPB'],
				['167N', '2021', 'PLSQ'],
				['167N', '2021', 'PLWF']
			],
			var_coeffs = [
				1, 1, 1, 1.5, 1, 1
			],
			compare_type = models.ComparisonSign.LE,
			compare_value = 3
		)
	]

	frmConstPreview = tk.Frame(root)
	frmConstPreview.grid(row=5, column=0, sticky="nsew")
	frmConstPreview.rowconfigure(1, weight=1)
	frmConstPreview.columnconfigure(0, weight=1)

	lblConstPreview = tk.Label(frmConstPreview, text="Preview Constraints")
	txtConstPreview = tk.Text(frmConstPreview, height=6)
	lblConstPreview.grid(row=0, column=0, sticky="wn", padx=10)
	txtConstPreview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 20))

	sampleConstString = generate_sample_constraint_string(
		sampleConstraints, 6, 25
		)
	txtConstPreview.insert("1.0", sampleConstString)


	#
	# Next Step Button
	btnNextStep = tk.Button(root, text="Fine Tune >", anchor="center")
	btnNextStep.grid(row=6, column=0, padx=10, pady=10, sticky="e")


	root.mainloop()


def generate_sample_constraint_string(constrList: List[models.CompiledConstraint], charHeight:int, charWidth: int) -> str:
	# TODO: Make this simpler
	numConstrs = 5
	constrs = constrList[:numConstrs]

	finalStr = ''

	for constr in constrs:
		varStrList = []
		for ind, varTags in enumerate(constr.var_tags):
			# TODO: Use some kind of rendering class / methods??
			coeff = constr.var_coeffs[ind]
			varStr = "_".join(varTags)

			if abs(coeff - 1.0) > 0.005:
				varStr = str(round(coeff, 2)) + " " + varStr

			varStrList.append(varStr)	
		varsStr = " + ".join(varStrList)

		rightHandStr = str(constr.compare_type) + " " + str(constr.compare_value)

		totalLen = len(varStr) + len(rightHandStr)
		if totalLen > charWidth:
			charsToCut = totalLen - charWidth
			varStr = varStr[: len(varStr) - charsToCut - 4]
			varStr[-4:] = " ..."

		finalStr += constr.name + ":" + "\n" 
		finalStr += varsStr + " " + rightHandStr + "\n"
		finalStr += "\n"

	return finalStr


def build_stage_1():
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

	btnObjFile = tk.Button(frmFileParseSetup, text="Objective .csv")
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

	#
	# Bottom half - naming tag groups
	exampleGroupMembersStrs = [
		['167N', '167S', '409', '104'],
		['2021', '2025', '2030', '2050'],
		['SPB', 'NoMng', 'WFNM']
	]

	frmNameAndVerify = tk.Frame(root, relief=tk.SUNKEN, bd=2)
	frmNameAndVerify.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
	frmNameAndVerify.columnconfigure(0, weight=1)

	frmNameGroups = tk.Frame(frmNameAndVerify)
	frmNameGroups.grid(row=0, column=0, columnspan=2, pady=10)
	frmNameGroups.columnconfigure([0, 1], weight=1)

	lblNamesCol = tk.Label(frmNameGroups, text="Name", anchor="center")
	lblExampleMemsCol = tk.Label(frmNameGroups, text="Example Members", anchor="center")
	lblNamesCol.grid(row=0, column=0)
	lblExampleMemsCol.grid(row=0, column=1)

	for ind, exampleGroup in enumerate(exampleGroupMembersStrs):
		entMemName = tk.Entry(frmNameGroups, width=15)

		exampleMemsStr = ", ".join(exampleGroup)
		if len(exampleMemsStr) > WIDTH_BIG:
			exampleMemsStr = exampleMemsStr[:WIDTH_BIG - 4] + " ..."
		lblExampleMems = tk.Label(frmNameGroups, text=exampleMemsStr, anchor="e")

		entMemName.grid(row=ind+1, column=0, padx=5, pady=5, sticky="nse")
		lblExampleMems.grid(row=ind+1, column=1, padx=5, pady=5, sticky="nsw")

	btnVerifyNames = tk.Button(frmNameAndVerify, text="Verify Group Names", anchor="center")
	btnVerifyNames.grid(row=2, column=0, padx=4, pady=5)

	#
	# Next Step Button
	btnNextStage = tk.Button(root, text="Continue >", anchor="center")
	btnNextStage.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="e")

	root.mainloop()


	pass




if __name__ == '__main__':
	main()