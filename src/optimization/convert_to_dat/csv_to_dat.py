'''
.csv to .dat converter

This script will convert two csvs, one for the
objective function and one for the constraints,
and then spit out a single .dat file.

Michael Gorbunov
William Zipse
NJDEP
'''

import os
import sys
import csv
from typing import Union
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askopenfilename

from model_data_classes import *

#constants for file names
#***Change filenames/paths here (for now)
OBJFILE = 'named_pokomoke_obj.csv'
CONSTRFILE = 'named_pokomoke_constsGe.csv'
OUTPUTDAT = 'named_pokomoke_out.dat'



# ======================================================
#                 (0) Main Calls
# ======================================================

def main():
	# Step 1: Get + Read Input
	objFilepath, constFilepath, paramFilepath = getFilepathsFromInput()
	print()
	print("Now parsing & converting...")

	objData = openAndReadObjectiveCSV(objFilepath)
	constData = openAndReadConstraintCSV(constFilepath)

	# Step 2: Validate the data & produce a FinalModel object
	objData, constData = lintInputData(objData, constData)
	finalModel = convertInputToFinalModel(objData, constData)

	# Step 3: Write the finalModel
	writeParamFile(finalModel, paramFilepath, objFilepath, constFilepath)

	print()
	print(f'All done')
	print(f'View output in {paramFilepath}')


def getFilepathsFromInput () -> Union[str, str, str]:
	# First get the filepaths
	# Try it with choosers

	# print("Let's choose some CSV's for making a Pyomo .dat file!")
	# input("Press any key to choose decision variable CSV.")
	# Tk().withdraw() #hide tk window since this is not a full GUI program
	# objFilepath   = askopenfilename()
	# input("Press any key to choose a constraint CSV.")
	# constFilepath = askopenfilename()
	# print("Next choose a Pyomo .dat file.")
	# print("Note: You will have to right click in the file window")
	# print("to create a new file and then select the file.")
	# input("Press any key to choose a Pyomo .dat filename")
	# paramFilepath = askopenfilename()

	# objFilepath   = getCSVFilepath("Objective File:   ")
	# constFilepath = getCSVFilepath("Constraints File: ")
	# paramFilepath = makeDATFilepath("Output .dat File: ")
	objFilepath = OBJFILE
	constFilepath = CONSTRFILE
	paramFilepath = OUTPUTDAT

	return objFilepath, constFilepath, paramFilepath


def lintInputData (objData: InputObjectiveData, constData: InputConstraintData) -> Union[InputObjectiveData, InputConstraintData]:
	objVars = objData.var_names
	constVars = constData.var_names

	# TODO: Check that all values are floats, strings, etc
	# TODO: Check that the lists have correct lengths


	# [ Check ]: No duplicate or unnamed variables
	errMsg = checkVarNameList(objVars)
	if (errMsg):
		errorAndExit("Error in objective file variable names: " + errMsg)

	errMsg = checkVarNameList(constVars)
	if (errMsg):
		errorAndExit("Error in constraint file variable names: " + errMsg)


	# [ Check ]: Variables in the objective file match those in the
	# 			 constraint file
	errMsg = checkVarNamesMatch(objVarNames=objVars, constVarNames=constVars)
	if (errMsg):
		errorAndExit(errMsg)


	# [ Check + Fix ]: All constraint are named
	filledList, emptyNamesExisted = fillInEmptyNames(constData.const_names, "unnamedConst")
	constData.const_names = filledList
	if (emptyNamesExisted):
		printWarning("Found unnamed constraints, giving them the name 'unnamedConst'")


	# [ Check ]: There exists at least one constraint
	if len(constData.const_names) == 0:
		errorAndExit("No constraints found!")


	# [ Check ]: Remove unrecognized operators
	allOps = constData.vec_operators
	# TODO: This is really ugly for adding new constraint types
	opClasses = ['le', 'eq', 'ge']
	indsToRemove = []

	for ind, op in enumerate(allOps):
		if not op in opClasses:
			indsToRemove.append(ind)
			printWarning(f"Found unrecognized constraint operator {op}" + \
					     f"named '{constData.constraint_names[ind]}'. Skipping it.")

	# Very important we start with the largest indicies first (reversed list)
	for ind in reversed(indsToRemove):
		constData.const_names.pop(ind)
		constData.vec_const_bounds.pop(ind)
		constData.vec_operators.pop(ind)
		constData.mat_constraint_coeffs.pop(ind)


	# [ Check ]: There is at least one of each constraint type
	allOps = constData.vec_operators
	opClasses = ['le', 'eq', 'ge']
	missingOps = opClasses[:]

	for op in allOps:
		if op in missingOps:
			missingOps.remove(op)

	if len(missingOps) != 0:
		printWarning(f"No constraints found for types: {' '.join(missingOps)}. Adding dummy constraints & variables for them")


	# [ Fix ]: Add dummy constraints & vars for each non-existent constraint class
	for op in missingOps:
		dumVar1, suffix = getNextAvailableDummyName(constData.var_names, 'dummy')
		dumVar2, _ = getNextAvailableDummyName(constData.var_names, 'dummy', startInd=suffix+1)

		constData.var_names.append(dumVar1)
		constData.var_names.append(dumVar2)
		objData.var_names.append(dumVar1)
		objData.var_names.append(dumVar2)

		# Resizing all previous constraints to have 0 coeffs for the new variables
		for ind, _ in enumerate(constData.mat_constraint_coeffs):
			constData.mat_constraint_coeffs[ind] += [0, 0]

		# Since we're maximizing the function, making these negative
		# will mean dummyVar1 & 2 always equal 0 and keep the actual objective
		objData.obj_coeffs.append(-1)
		objData.obj_coeffs.append(-1)

		# Construct a list in the form [0, 0, ..., 0, 1, 1] so the constraint
		# involves the two dummy variables
		constraint_coeffs = [0] * len(constData.var_names)
		constraint_coeffs[-2:] = [1, 1]

		dumConstName, _ = getNextAvailableDummyName(constData.const_names, 'dummy' + op.upper())

		constData.const_names.append(dumConstName)
		constData.vec_const_bounds.append(0)
		constData.vec_operators.append(op)
		constData.mat_constraint_coeffs.append(constraint_coeffs)

		printWarning(f'No {op.upper()} constraint found, adding variables' +
			f' "{dumVar1}", "{dumVar2}" and constraint "{dumConstName}"'
			)

	return objData, constData


def convertInputToFinalModel (objData: InputObjectiveData, constData: InputConstraintData) -> FinalModel:
	# All the lists to populate
	var_names = []
	obj_coeffs = []

	le_const_names = []
	le_vec = []
	le_mat = []

	ge_const_names = []
	ge_vec = []
	ge_mat = []

	eq_const_names = []
	eq_vec = []
	eq_mat = []

	# Actually populating the lists
	var_names = objData.var_names
	obj_coeffs = objData.obj_coeffs

	for ind, name in enumerate(constData.const_names):
		# TODO: This .lower().strip() should happen in the linting step
		op = constData.vec_operators[ind].lower().strip()

		if op == 'le':
			le_const_names.append(name)
			le_vec.append(constData.vec_const_bounds[ind])
			le_mat.append(constData.mat_constraint_coeffs[ind])
		elif op == 'ge':
			ge_const_names.append(name)
			ge_vec.append(constData.vec_const_bounds[ind])
			ge_mat.append(constData.mat_constraint_coeffs[ind])
		elif op == 'eq':
			eq_const_names.append(name)
			eq_vec.append(constData.vec_const_bounds[ind])
			eq_mat.append(constData.mat_constraint_coeffs[ind])

	return FinalModel(
		var_names=var_names, obj_coeffs=obj_coeffs,
		le_const_names=le_const_names, le_vec=le_vec, le_mat=le_mat,
		ge_const_names=ge_const_names, ge_vec=ge_vec, ge_mat=ge_mat,
		eq_const_names=eq_const_names, eq_vec=eq_vec, eq_mat=eq_mat
		)


def writeParamFile (modelData: FinalModel, paramFilepath, objFilepath, constFilepath):
	md = modelData

	# Now write the entire model into the .dat file
	with open(paramFilepath, 'w') as paramFile:
		writeTopComment(paramFile, objFilepath, constFilepath)

		# indexing sets
		str_index_vars = " ".join([str(x) for x in md.var_names])
		str_index_le_consts = " ".join([str(x) for x in md.le_const_names])
		str_index_ge_consts = " ".join([str(x) for x in md.ge_const_names])
		str_index_eq_consts = " ".join([str(x) for x in md.eq_const_names])

		paramFile.write(f'\nset index_vars := {str_index_vars};\n')
		paramFile.write(f'\nset index_le_consts := {str_index_le_consts};\n')
		paramFile.write(f'\nset index_ge_consts := {str_index_ge_consts};\n')
		paramFile.write(f'\nset index_eq_consts := {str_index_eq_consts};\n')

		# objective function
		writeVector(paramFile, 'vec_objective', md.obj_coeffs, md.var_names)

		# constraints
		writeVector(paramFile, 'vec_le', md.le_vec, md.le_const_names)
		writeMatrix(paramFile, 'mat_le', md.le_mat, md.le_const_names, md.var_names)

		writeVector(paramFile, 'vec_ge', md.ge_vec, md.ge_const_names)
		writeMatrix(paramFile, 'mat_ge', md.ge_mat, md.ge_const_names, md.var_names)

		writeVector(paramFile, 'vec_eq', md.eq_vec, md.eq_const_names)
		writeMatrix(paramFile, 'mat_eq', md.eq_mat, md.eq_const_names, md.var_names)












# ======================================================
#                 (1) Data Input
# ======================================================

def openAndReadObjectiveCSV (objFilepath: Path) -> InputObjectiveData:
	'''
		Opens and reads the objective file csv, returning
		a InputObjectiveData object.
	'''
	objectiveInput = InputObjectiveData()

	with open(objFilepath, 'r') as objFile:
		objCSVReader = csv.reader(objFile)
		lineCount = 0

		# Read in the objective function
		for row in objCSVReader:
			lineCount += 1

			if (lineCount > 1):
				objectiveInput.var_names.append(row[0])
				objectiveInput.obj_coeffs.append(float(row[1]))

	return objectiveInput


def openAndReadConstraintCSV (constFilepath: Path) -> InputConstraintData:
	'''
		Opens and reads the constraint csv, returning a InputConstraintData class
	'''
	constraintInput = InputConstraintData()

	with open(constFilepath, 'r') as constFile:
		constCSVReader = csv.reader(constFile)
		lineCount = 0

		for row in constCSVReader:
			row = [str(x).strip() for x in row]
			lineCount += 1

			if (lineCount == 1):
				constraintInput.var_names = row[1:-2]
			else:
				operator = row[-2]
				coeffs = row[1:-2]
				constraint_bound = row[-1]
				constraint_name = row[0]

				constraintInput.vec_operators.append(operator)
				constraintInput.mat_constraint_coeffs.append(coeffs)
				constraintInput.vec_const_bounds.append(constraint_bound)
				constraintInput.const_names.append(constraint_name)

	return constraintInput



#
# Filepath Input

def getCSVFilepath (message: str) -> Path:
	'''
		Takes user input for a path and makes
		sure that the file is a csv and exists.

		In the event of an error, this will terminate
		the program. The returned object is never None.
	'''
	pathStr = input(message).strip()

 	# Sometimes the passed in directory is surrounded by quotes
	# This checks for & removes them
	# ex: '/home/velcro' -> /home/velcro
	first_and_last_chars = pathStr[0] + pathStr[-1]
	if first_and_last_chars == "''" or first_and_last_chars == '""':
		pathStr = pathStr[1:-1]

	pathObj = Path(pathStr)

	if not pathObj.exists():
		errorAndExit("Supplied filepath does not exist")
	if pathObj.is_dir():
		errorAndExit("Supplied filepath is to a directory")

	fileExt = pathObj.suffix

	if fileExt != '.csv':
		errorAndExit("Supplied filepath is not a csv")

	return pathObj


def makeDATFilepath (message: str) -> Path:
	outputPath = input(message).strip()

 	# Sometimes the passed in directory is surrounded by quotes
	# This checks for & removes them
	# ex: '/home/velcro' -> /home/velcro
	first_and_last_chars = outputPath[0] + outputPath[-1]
	if first_and_last_chars == "''" or first_and_last_chars == '""':
		outputPath = outputPath[1:-1]

	pathObj = Path(outputPath)

	if pathObj.exists():
		print()
		printWarning("File already exists")
		overwrite = input("Overwrite existing file? [y/n] ")

		if (overwrite != 'y'):
			print("\n\nAborting")
			sys.exit(0)

	return pathObj






# ======================================================
#                 (2) Data Linting
# ======================================================

def checkVarNameList (varNameList: List[str]) -> str:
	'''
		Will check the provided list of variable names to find
			- duplicates
			- blank names

		This function returns an error message string, and if
		there's no error it returns None
	'''
	for varName in varNameList:
		if varName.strip() == "":
			return "Unnamed variable found"

	if len(varNameList) != len(set(varNameList)):
		duplicates = [name for name in varNameList if varNameList.count(name) > 1]
		duplicates = [str(x) for x in list(set(duplicates))]
		return f"Repeated variable names: {' '.join(duplicates)}"

	return None


def checkVarNamesMatch (objVarNames: List[str], constVarNames: List[str]) -> str:
	'''
		Checks that the variable names in the objective file match
		those in the constriant file.

		Note: This does not check for duplicate or unnamed variables

		Returns an error message if one is found, but otherwise a None
	'''
	if set(objVarNames) == set(constVarNames):
		return None

	varsOnlyInConst = set(constVarNames) - set(objVarNames)
	varsOnlyInObj = set(objVarNames) - set(constVarNames)

	if varsOnlyInConst:
		return
		'''
			Found decision variables in the constraint file
			that don't exist in the objective file:
		''' + ", ".join([str(x) for x in varsOnlyInConst])

	if varsOnlyInObj:
		return
		'''
			Found unconstrained variable, i.e. they exist in
			the objective file but not the constraint file:
		''' + ", ".join([str(x) for x in varsOnlyInObj])

	# If the two sets are unequal, one of them should have a member
	# the other doesn't. The code should never reach here.
	assert(False)


#
# Filling in lists

def fillInEmptyNames (nameList: list, nameBase: str) -> Union[List[str], bool]:
	'''
		Goes through the list, filling in empty names in a seperate list.
		Returns the now filled list, as well as true/false as to whether
		any empty entries were found.
	'''
	filledList = [x for x in nameList] # duplicate the list
	anyEmptiesFound = False

	for ind, constName in enumerate(filledList):
		if constName.strip() == "":
			anyEmptiesFound = True
			newConstName = getNextAvailableDummyName(filledList, nameList)
			filledList[ind] = newConstName

	return filledList, anyEmptiesFound


def getNextAvailableDummyName (nameList: List[str], nameBase: str, startInd: int=0) -> Union[str, int]:
	'''
		This searches through a list to find the first unused
		string in the form nameBase + a number.

		For example, given
			- nameBase = 'un'
			- nameList = ['un0', 'un1', 'un3']
		this would return 'un2'
	'''
	num = startInd
	outStr = nameBase + str(num)

	while (outStr in nameList):
		num += 1
		outStr = nameBase + str(num)

	return outStr, num









# ======================================================
#                     (3) File Output
# ======================================================

def writeTopComment (paramFile, objFilepath: str, constFilepath: str) -> None:
	paramFile.write(f'''
# Auto Generated File built from CSVs
#  - Objective File: {str(objFilepath)}
#  - Constraints File: {str(constFilepath)}
#
# NJDEP
	''')


def writeVector (paramFile, vectorName: str, vector: list, indexNames: list) -> None:
	assert(len(vector) == len(indexNames))

	paramFile.write(f'\nparam {vectorName} := \n')
	for ind, objCoef in enumerate(vector):
		paramFile.write(f'\t{indexNames[ind]} {objCoef}\n')
	paramFile.write(f';\n')


def writeMatrix (paramFile, matrixName: str, matrix: list, rowNames: list, varNames: list, ) -> None:
	# The indexing sets need to have the same lengths as the matrix
	assert(len(matrix) == len(rowNames))
	assert(len(matrix) > 0 and len(matrix[0]) == len(varNames))

	# First, we need the line 'param matName: 1 2 ... 6 7 :='
	paramFile.write(f'\nparam {matrixName}: ')
	for indName in varNames:
		paramFile.write(f'{indName} ')
	paramFile.write(':=\n')

	# Now we have the actual matrix
	for ind, valueList in enumerate(matrix):
		paramFile.write(f'\t{rowNames[ind]} ')
		for coef in valueList:
			paramFile.write(f'{coef} ')
		paramFile.write('\n')
	paramFile.write(';\n')








# ======================================================
#              Logging / Small Utilities
# ======================================================

def errorAndExit (errMessage: str):
	print()
	print('\t[[ Error ]]')
	print(f'{errMessage}')
	print()
	print("Aborting.")
	sys.exit(1)


def printWarning (warnMessage: str):
	print(f'\t[[ Warning ]] : {warnMessage}')







if __name__ == '__main__':
	main()
