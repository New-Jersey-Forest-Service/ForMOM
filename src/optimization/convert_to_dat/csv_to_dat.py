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


def main():
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

	objFilepath   = getCSVFilepath("Objective File:   ")
	constFilepath = getCSVFilepath("Constraints File: ")
	paramFilepath = makeDATFilepath("Output .dat File: ")

	print()
	print("Now parsing & converting...")

	# Read the objective file
	dat_objVarNames, dat_objCoeffs = openAndReadObjectiveCSV(objFilepath)

	# Read the constraints file
	dat_constVarNames, \
	dat_eqConstNames, dat_eqMatrix, dat_eqVector, \
	dat_leConstNames, dat_leMatrix, dat_leVector = openAndReadConstraintCSV(constFilepath)




	# Before writing to file, do some linting on the csv data

	# Check 1 - Making sure variable names are the same in objective file &
	#			constraint file
	listIsOK, errMsg = varNameListIsOK(dat_objVarNames)
	if (not listIsOK):
		errorAndExit(errMsg)

	listIsOK, errMsg = varNameListIsOK(dat_constVarNames)
	if (not listIsOK):
		errorAndExit(errMsg)

	# Check 2 - The variables in the objective function are the same as those in
	#			the constraints file
	if set(dat_objVarNames) != set(dat_constVarNames):
		varsOnlyInConsts = set(dat_constVarNames) - set(dat_objVarNames)
		varsOnlyInObj = set(dat_objVarNames) - set(dat_constVarNames)

		# All variables in the constraints must be in the objective
		# function, so this is an error
		if varsOnlyInConsts:
			errorAndExit(
				"Found variables in constraint file that are not in the objective file: " +
				" ".join([str(x) for x in varsOnlyInConsts])
				)

		# It might be ok if there are unused variables, hence why this is only a warning
		if varsOnlyInObj:
			printWarning(
				"Found variables on in the objective file, i.e. they're unused in constraints: " +
				" ".join([str(x) for x in varsOnlyInObj])
				)

	# Check 3 - Name all unnamed constraints
	dat_eqConstNames = fillInEmptyNames(dat_eqConstNames, "unnamedEQ")
	dat_leConstNames = fillInEmptyNames(dat_leConstNames, "unnamedLE")

	# Check 4 - Existence of at least one LE & EQ constraint
	# 			In the event that one constraint type is missing,
	#			dummy variables are made
	if len(dat_eqVector) == 0 and len(dat_leVector) == 0:
		errorAndExit("No constraints at all found")

	elif len(dat_eqVector) == 0 or len(dat_leVector) == 0:
		dumVar1 = getNextAvailableDummyName(dat_objVarNames, 'dummy')
		dat_objVarNames.append(dumVar1)
		dat_constVarNames.append(dumVar1)

		dumVar2 = getNextAvailableDummyName(dat_objVarNames, 'dummy')
		dat_objVarNames.append(dumVar2)
		dat_constVarNames.append(dumVar2)

		# Adding the two variables means resizing all previous constraints

		# Resizing all previous constraints to have 0 coeffs for the new variables
		for ind, _ in enumerate(dat_eqMatrix):
			dat_eqMatrix[ind] += [0, 0]
		for ind, _ in enumerate(dat_leMatrix):
			dat_leMatrix[ind] += [0, 0]

		# Since we're maximizing the function, making these negative
		# will mean dummyVar1 & 2 always equal 0 and keep the actual objective
		# values unaffected (potentially wrong, this is my idea)
		dat_objCoeffs.append(-1)
		dat_objCoeffs.append(-1)

		constraint_coeffs = [0] * len(dat_objVarNames)
		constraint_coeffs[-2:] = [1, 1]

		if len(dat_eqVector) == 0:
			dumConstName = getNextAvailableDummyName(dat_eqConstNames, 'dummyEQ')

			# Add restriction dummy1 + dummy2 = 0
			dat_eqConstNames.append(dumConstName)
			dat_eqMatrix.append(constraint_coeffs)
			dat_eqVector.append(0)

			printWarning(f'No equals constraint found, adding variables' +
				f' "{dumVar1}", "{dumVar2}" and constraint "{dumConstName}"'
				)
		else:
			dumConstName = getNextAvailableDummyName(dat_leConstNames, 'dummyLE')

			# Add restriction dumm1 + dummy2 <= 10 (any number >= 0 works)
			dat_leConstNames.append(dumConstName)
			dat_leMatrix.append(constraint_coeffs)
			dat_leVector.append(10)

			printWarning(f'No le constraint found, adding variables' +
				f' "{dumVar1}", "{dumVar2}" and constraint "{dumConstName}"'
				)


	# Now write the entire model into the .dat file
	with open(paramFilepath, 'w') as paramFile:
		writeTopComment(paramFile, objFilepath, constFilepath)

		# indexing sets
		index_vars_str = " ".join([str(x) for x in dat_objVarNames])
		index_eq_consts_str = " ".join([str(x) for x in dat_eqConstNames])
		index_le_consts_str = " ".join([str(x) for x in dat_leConstNames])

		paramFile.write(f'\nset index_vars := {index_vars_str};\n')
		paramFile.write(f'\nset index_eq_consts := {index_eq_consts_str};\n')
		paramFile.write(f'\nset index_le_consts := {index_le_consts_str};\n')

		# objective
		writeVector(paramFile, 'vec_objective', dat_objCoeffs, dat_objVarNames)

		# constraints
		writeVector(paramFile, 'vec_eq', dat_eqVector, dat_eqConstNames)
		writeMatrix(paramFile, 'mat_eq', dat_eqMatrix, dat_eqConstNames, dat_constVarNames)

		writeVector(paramFile, 'vec_le', dat_leVector, dat_leConstNames)
		writeMatrix(paramFile, 'mat_le', dat_leMatrix, dat_leConstNames, dat_constVarNames)

	print()
	print(f'All done')
	print(f'View output in {paramFilepath}')












# ======================================================
#                 (1) Data Input
# ======================================================

def openAndReadObjectiveCSV (objFilepath: Path):
	'''
		Opens and reads the objective file csv, returning two lists
		 - varNames: Names of the variables
		 - objCoeffs: Coefficients of the objective function
	'''
	varNames = []
	objCoeffs = []

	with open(objFilepath, 'r') as objFile:
		objCSVReader = csv.reader(objFile)
		lineCount = 0

		# Read in the objective function
		for row in objCSVReader:
			lineCount += 1

			if (lineCount > 1):
				varNames.append(row[0])
				objCoeffs.append(float(row[1]))

	return varNames, objCoeffs


def openAndReadConstraintCSV (constFilepath: Path):
	'''
		Opens and reads the constraint csv, returning 7 lists
		 - varNames: Names of constraint variables, potentially
			in a different order than the varNames from openAndReadObjectiveCSV()
		 - leConstNames, leMatrix, leVector: Coefs for the <= constraints
		 - geConstNames, geMatrix, geVector: Coefs for the >= constraints
		 - eqConstNames, eqMatrix, eqVector: Coefs for the equality constraints. The vector
		 	represents the actual amounts that the matrix product should equals

		They are returned in the following order:
			varNames, eqConstNames, eqMatrix, eqVector, leConstNames, leMatrix, leVector
	'''
	varNames = []

	leConstNames = []
	leVector = []
	leMatrix = []

	geConstNames = []
	geVector = []
	geMatrix = []

	eqConstNames = []
	eqVector = []
	eqMatrix = []

	with open(constFilepath, 'r') as constFile:
		constCSVReader = csv.reader(constFile)
		lineCount = 0

		for row in constCSVReader:
			row = [str(x).strip() for x in row]
			lineCount += 1

			if (lineCount == 1):
				varNames = row[1:-2]
			else:
				operator = row[-2]
				if (operator == 'le'):
					leVector.append(row[-1])
					leMatrix.append(row[1:-2])
					leConstNames.append(row[0])
				elif (operator == 'eq'):
					eqVector.append(row[-1])
					eqMatrix.append(row[1: -2])
					eqConstNames.append(row[0])
				else:
					printWarning(f'Unreognized constraint type: {operator}')

	return varNames, \
		eqConstNames, eqMatrix, eqVector, \
		leConstNames, leMatrix, leVector



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

def varNameListIsOK (varNameList: list) -> Union[bool, str]:
	'''
		Will check the provided list of variable names to find
			- duplicates
			- blank names

		In the event of detection, this function returns True
		and an error message, otherwise returning False and None
	'''
	for varName in varNameList:
		if varName.strip() == "":
			return False, "Unnamed variable found"

	if len(varNameList) != len(set(varNameList)):
		duplicates = [name for name in varNameList if varNameList.count(name) > 1]
		duplicates = [str(x) for x in list(set(duplicates))]
		return False, f"Repeated variable names: {' '.join(duplicates)}"

	return True, None


def getNextAvailableDummyName (nameList: list, nameBase: str, start: int=0) -> str:
	'''
		Given
			- nameBase = 'unnamed'
			- nameList = ['unnamed0', 'unnamed1', 'unnamed3']
		this would return 'unnamed2'
	'''
	num = start
	outStr = nameBase + str(num)

	while (outStr in nameList):
		num += 1
		outStr = nameBase + str(num)

	return outStr


def fillInEmptyNames (nameList: list, nameBase: str) -> list:
	'''
		Goes through the nameList, fills in any empty
		names, and returns the now filled in list.
	'''
	filledList = [x for x in nameList] # duplicate the list

	for ind, constName in enumerate(filledList):
		if constName.strip() == "":
			newConstName = getNextAvailableDummyName(filledList, nameList)
			filledList[ind] = newConstName
			printWarning(f"Found unnamed constraint, renaming it to '{newConstName}'")

	return filledList










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
