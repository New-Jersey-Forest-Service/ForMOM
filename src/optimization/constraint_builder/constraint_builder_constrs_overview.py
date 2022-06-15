'''
Constraint Builder Constraints Overview Screen
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


# This will be useful for scrolling
# https://stackoverflow.com/questions/68056757/how-to-scroll-through-tkinter-widgets-that-were-defined-inside-of-a-function


def main():
	root = tk.Tk()
	root.title("Constraint Builder - Stage 3: Constraints Overview")
	root.rowconfigure(1, weight=1)
	root.columnconfigure(0, weight=1)

	# Header text
	lblHeader = tk.Label(root, text="Stage 3 - Constraints Overview")
	lblHeader.grid(row=0, column=0, padx=10, pady=(10, 0))

	#
	# Constraint Groups Display

	# TODO: To remove future polymorphism, add a general constriantinfo class
	sampleConstraintGroups: List[models.StandardConstraintGroup] = [
		models.StandardConstraintGroup(
			selected_tags=None,
			split_by_groups=None,
			name="Im14AndThisIsDeep",
			default_compare=None,
			default_value=0
		),
		models.StandardConstraintGroup(
			selected_tags=None,
			split_by_groups=None,
			name="AgedLikeMilk",
			default_compare=None,
			default_value=0
		)
	]

	frmConstrsDisplay = tk.Frame(root)
	frmConstrsDisplay.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")
	frmConstrsDisplay.columnconfigure(0, weight=1)

	# Construct frames for the actual constraints
	for ind, constrGroup in enumerate(sampleConstraintGroups):
		frmConstr = tk.Frame(frmConstrsDisplay, relief=tk.RIDGE, bd=2)
		frmConstr.grid(row=ind, column=0, sticky="ew", pady=(0, 10))
		frmConstr.columnconfigure(1, weight=1)
		
		lblName = tk.Label(frmConstr, text=constrGroup.name)
		lblName.grid(row=0, column=0, sticky="w")

		btnDelete = tk.Button(frmConstr, text="Delete")
		btnDelete.grid(row=0, column=1, sticky="e")

		btnEdit = tk.Button(frmConstr, text="Edit >")
		btnEdit.grid(row=0, column=2, sticky="e")

	# Add final button
	ind = len(sampleConstraintGroups)

	frmNewConstrBtn = tk.Frame(frmConstrsDisplay)
	frmNewConstrBtn.grid(row=ind, column=0, sticky="ew", pady=(0, 10))
	frmNewConstrBtn.columnconfigure(0, weight=1)

	btnNew = tk.Button(frmNewConstrBtn, text="New Constraint Group", anchor="center")
	btnNew.grid(row=0, column=0, sticky="ew")




	#
	# Exporting Buttons
	frmExport = tk.Frame(root)
	frmExport.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="ew")
	
	frmExport.columnconfigure(0, weight=1)

	btnSaveProj = tk.Button(frmExport, text="Save Project")
	btnSaveProj.grid(row=0, column=0, sticky="e")

	btnExportProj = tk.Button(frmExport, text="Export to .csv")
	btnExportProj.grid(row=0, column=1, sticky="e")

	root.mainloop()





if __name__ == '__main__':
	main()

