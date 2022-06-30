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
	return

	# with open(filepath, 'w') as outFile:
	# 	writer = csv.writer(outFile, delimiter=',', quotechar='"')
		
	# 	# Write top row - all variables names
	# 	delim = projState.varTags.delim
	# 	allVarNamesSorted = copy.deepcopy(projState.varTags.all_vars)
	# 	allVarNamesSorted.sort(key=lambda tags: delim.join(tags))
	# 	allVarNamesRaw = [delim.join(x) for x in allVarNamesSorted]

	# 	writer.writerow(['const_name'] + allVarNamesRaw + ['operator', 'rtSide'])

	# 	# Write each constraint
	# 	rowLen = len(allVarNamesSorted) + 3

	# 	for constGroup in projState.constrGroupList:
	# 		individConstrs = proc.buildConstraintsFromStandardConstraintGroup(projState.varTags, constGroup)

	# 		for constr in individConstrs:
	# 			nextRow = [''] * rowLen
	# 			nextRow[0] = constr.name
	# 			nextRow[-1] = constr.compare_value
	# 			nextRow[-2] = constr.compare_type.name.lower()

	# 			for ind, var in enumerate(allVarNamesSorted):
	# 				coef = 0
	# 				if var in constr.var_tags:
	# 					varInd = constr.var_tags.index(var)
	# 					coef = constr.var_coeffs[varInd]
	# 				nextRow[ind+1] = coef
				
	# 			writer.writerow(nextRow)



