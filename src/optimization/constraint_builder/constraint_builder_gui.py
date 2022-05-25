'''
Constraint Builder Gui

The front end for the constraint builder.

Michael Gorbunov
NJDEP 2022
'''

import tkinter as tk
from tkinter import ttk


PATH_DISPLAY_LEN = 35
EXAMPLE_MEMS_LEN = 30
CSV_FILES = [('CSV Files', '*.csv'), ('All Files', '*.*')]


# TODO: Learn about tkinter variables (as opposed to globals / state object)

def main():

	root = tk.Tk()
	root.title("Constraint Builder - Stage 1: Setup Variables")
	root.rowconfigure([0, 1, 2], weight=1)
	root.columnconfigure(0, weight=1)

	# Header Text
	lblHeader = tk.Label(root, text="Stage 1 - Variable Setup", anchor="center")
	lblHeader.grid(row=0, column=0, padx=10, pady=(10, 0))

	#
	# Top half - selecting & parsing the obj file
	frmFileParseSetup = tk.Frame(root, relief=tk.RAISED, bd=2)
	frmFileParseSetup.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

	btnObjFile = tk.Button(frmFileParseSetup, text="Objective .csv")
	lblObjFile = tk.Label(frmFileParseSetup, text="No file selected", width=PATH_DISPLAY_LEN, anchor="w")
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
		if len(exampleMemsStr) > EXAMPLE_MEMS_LEN:
			exampleMemsStr = exampleMemsStr[:EXAMPLE_MEMS_LEN - 4] + " ..."
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
