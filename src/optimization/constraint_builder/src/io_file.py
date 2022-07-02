'''
File IO

Every (non-trivial) file write, read, validation should come through here
'''

from pathlib import Path
from tkinter import dialog, filedialog
from typing import Any, List, Tuple, Type
import csv
import models
import copy
import proc_constraints as proc



#
# User Input
#

def getSaveAsFilepath (filetypes: List[Tuple[str]]) -> str:
	'''
	Runs the tkinter askopenfilename and returns None
	if the file was invalid. 
	
	For whatever reason there are multiple
	possible invalid outputs from the tkinter askopenfilname
	'''

	filepath = filedialog.asksaveasfilename(
		filetypes=filetypes,
		defaultextension=filetypes
		)

	if _isInvalidFile(filepath):
		return None
	return str(filepath)


def getOpenFilepath (filetypes: List[Tuple[str]]) -> str:
	'''
	Runs the tkinter askopenfilename but returns None
	if the file was invalid. 
	
	For whatever reason there are multiple
	possible invalid outputs from the tkinter askopenfilname
	'''

	filepath = filedialog.askopenfilename(
		filetypes=filetypes,
		defaultextension=filetypes
		)
	
	if _isInvalidFile(filepath):
		return None
	return str(filepath)


def _isInvalidFile (filepath: str) -> bool:
	return filepath == None or \
		len(filepath) == 0 or \
		not isinstance(filepath, str) or \
		filepath.strip() == ""






#
# Reading
#

def readVarnamesRaw (objCSVPath: Path, numVars=-1) -> List[str]:
	'''
	Reads the raw variables names in the provided file.

	If numVars = -1, it will read all of them. Otherwise,
	it only reads upto numVars variables 
	(potentially will return less variables if the file is small)
	'''
	allVarnames = []

	with open(objCSVPath, 'r') as objFile:
		r = csv.reader(objFile)
		lineCount = 0
		for row in r:
			lineCount += 1
			if lineCount == 1:
				continue
			if numVars >= 0 and len(allVarnames) >= numVars:
				break

			allVarnames.append(str(row[0]).strip())

	return allVarnames








#
# Writing
#

def writeToCSV (filepath: str, projState: models.ProjectState):
	with open(filepath, 'w') as outFile:
		writer = csv.writer(outFile)

		delim = projState.varData.delim
		allVarNamesSorted = copy.deepcopy(projState.varData.all_vars)
		allVarNamesSorted.sort(key=lambda tags: "".join(tags))
		allVarNamesRaw = [delim.join(x) for x in allVarNamesSorted]

		writer.writerow(['const_name'] + allVarNamesRaw + ['operator', 'rtSide'])

		rowLen = len(allVarNamesSorted) + 3

		for setupGroup in projState.setupList:
			constrGroup: models.ConstraintGroup = proc.buildConstraintGroup(setupGroup, projState.varData)

			for constr in constrGroup.equations:
				newRow = [''] * rowLen

				name = constr.namePrefix
				if constr.nameSuffix != '':
					name += delim + constr.nameSuffix
				newRow[0] = name
				newRow[-1] = constr.constant
				newRow[-2] = constr.comparison.exportName()

				for ind, var in enumerate(allVarNamesSorted):
					coef = 0.0
					if var in constr.leftVars:
						# leftInd = 
						leftInd = constr.leftVars.index(var)
						coef += constr.leftCoefs[leftInd]
					if var in constr.rightVars:
						rightInd = constr.rightVars.index(var)
						coef -= constr.rightCoefs[rightInd]
					newRow[ind+1] = coef

				writer.writerow(newRow)


