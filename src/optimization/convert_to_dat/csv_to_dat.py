'''
.csv to .dat converter

This script will convert two csvs, one for the
objective function and one for the constraints,
and then spit out a single .dat file.

Michael Gorbunov
William Zipse
NJDEP
'''

import sys
import csv
from typing import Union, List
from pathlib import Path

import model_data_classes as models





# ======================================================
#                 Reading Input Files
# ======================================================

def openAndReadObjectiveCSV (objFilepath: Path) -> models.InputObjectiveData:
	'''
		Opens and reads the objective file csv, returning
		a InputObjectiveData object.
	'''
	var_name_list = []
	obj_coeff_list = []

	with open(objFilepath, 'r') as objFile:
		objCSVReader = csv.reader(objFile)
		lineCount = 0

		# Read in the objective function
		for row in objCSVReader:
			lineCount += 1

			if (lineCount > 1):
				var_name_list.append(row[0])
				obj_coeff_list.append(float(row[1]))

	return models.InputObjectiveData(
		var_names=var_name_list, 
		obj_coeffs=obj_coeff_list
	)


def openAndReadConstraintCSV (constFilepath: Path) -> models.InputConstraintData:
	'''
		Opens and reads the constraint csv, returning a InputConstraintData class
	'''
	var_names = []
	vec_operators = []
	mat_constraint_coeffs = []
	vec_const_bounds = []
	const_names = []

	with open(constFilepath, 'r') as constFile:
		constCSVReader = csv.reader(constFile)
		lineCount = 0

		for row in constCSVReader:
			row = [str(x).strip() for x in row]
			lineCount += 1

			if (lineCount == 1):
				var_names = row[1:-2]
			else:
				operator = row[-2]
				coeffs = row[1:-2]
				constraint_bound = row[-1]
				constraint_name = row[0]

				vec_operators.append(operator)
				mat_constraint_coeffs.append(coeffs)
				vec_const_bounds.append(constraint_bound)
				const_names.append(constraint_name)

	return models.InputConstraintData(
		var_names=var_names,
		const_names=const_names,
		vec_const_bounds=vec_const_bounds,
		vec_operators=vec_operators,
		mat_constraint_coeffs=mat_constraint_coeffs
	)


def convertInputToFinalModel (objData: models.InputObjectiveData, constData: models.InputConstraintData) -> models.FinalModel:
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
	var_names = constData.var_names
	obj_coeffs = [0.0] * len(objData.obj_coeffs)
	for ind, name in enumerate(objData.var_names):
		coef_ind = var_names.index(name)
		obj_coeffs[coef_ind] = objData.obj_coeffs[ind]

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

	return models.FinalModel(
		var_names=var_names, obj_coeffs=obj_coeffs,
		le_const_names=le_const_names, le_vec=le_vec, le_mat=le_mat,
		ge_const_names=ge_const_names, ge_vec=ge_vec, ge_mat=ge_mat,
		eq_const_names=eq_const_names, eq_vec=eq_vec, eq_mat=eq_mat
		)










# ======================================================
#                Input Linting & Validation
# ======================================================

def lintInputData (objData: models.InputObjectiveData, constData: models.InputConstraintData) -> Union[models.InputObjectiveData, models.InputConstraintData, str]:
	'''
		Goes through the data in the CSVs and runs some checks. It will return either:
			1. (None, None, ["Error Message"]) in the case of an error
			2. (InputObjData, InputConstData, ["Warning Messages"]) in the case of succesfull linting
		The final entry will always be an array of strings. Whether they are warnings or errors depends on whether
		the data objects are None. If there are no warnings, the list will be empty.
	'''
	objVars = objData.var_names
	constVars = constData.var_names
	warningList = []

	# TODO: Check that all values are floats, strings, etc
	# TODO: Check that the lists have correct lengths


	# [ Check ]: No duplicate or unnamed variables
	errMsg = checkVarNameList(objVars)
	if (errMsg):
		return None, None, ["Error in objective file variable names: " + errMsg]

	errMsg = checkVarNameList(constVars)
	if (errMsg):
		return None, None, ["Error in constraint file variable name: " + errMsg]


	# [ Check ]: Variables in the objective file match those in the
	# 			 constraint file
	errMsg = checkVarNamesMatch(objVarNames=objVars, constVarNames=constVars)
	if (errMsg):
		return None, None, [errMsg]


	# [ Check + Fix ]: All constraint are named
	filledList, emptyNamesExisted = fillInEmptyNames(constData.const_names, "unnamedConst")
	constData.const_names = filledList
	if (emptyNamesExisted):
		warningList.append("Found unnamed constraints, giving them the name 'unnamedConst'")


	# [ Check ]: There exists at least one constraint
	if len(constData.const_names) == 0:
		return None, None, ["No constraints found!"]


	# [ Check ]: Remove unrecognized operators
	allOps = constData.vec_operators
	# TODO: This is really ugly for adding new constraint types
	opClasses = ['le', 'eq', 'ge']
	indsToRemove = []

	for ind, op in enumerate(allOps):
		if not op in opClasses:
			indsToRemove.append(ind)

			warningList.append(f"Found unrecognized constraint operator {op}" + \
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
		warningList.append(f"No constraints found for types: {' '.join(missingOps)}." + 
						   f" Adding dummy constraints & variables for them")


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

		warningList.append(f'No {op.upper()} constraint found, adding variables' +
						   f' "{dumVar1}", "{dumVar2}" and constraint "{dumConstName}"')

	return objData, constData, warningList


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
#                  Writing to .dat
# ======================================================

def writeOutputDat (modelData: models.FinalModel, outputFilepath: str, objFilepath: str, constFilepath: str):
	md = modelData

	# Now write the entire model into the .dat file
	with open(outputFilepath, 'w') as outFile:
		writeTopComment(outFile, objFilepath, constFilepath)

		# indexing sets
		str_index_vars = " ".join([str(x) for x in md.var_names])
		str_index_le_consts = " ".join([str(x) for x in md.le_const_names])
		str_index_ge_consts = " ".join([str(x) for x in md.ge_const_names])
		str_index_eq_consts = " ".join([str(x) for x in md.eq_const_names])

		outFile.write(f'\nset index_vars := {str_index_vars};\n')
		outFile.write(f'\nset index_le_consts := {str_index_le_consts};\n')
		outFile.write(f'\nset index_ge_consts := {str_index_ge_consts};\n')
		outFile.write(f'\nset index_eq_consts := {str_index_eq_consts};\n')

		# objective function
		writeVector(outFile, 'vec_objective', md.obj_coeffs, md.var_names)

		# constraints
		writeVector(outFile, 'vec_le', md.le_vec, md.le_const_names)
		writeMatrix(outFile, 'mat_le', md.le_mat, md.le_const_names, md.var_names)

		writeVector(outFile, 'vec_ge', md.ge_vec, md.ge_const_names)
		writeMatrix(outFile, 'mat_ge', md.ge_mat, md.ge_const_names, md.var_names)

		writeVector(outFile, 'vec_eq', md.eq_vec, md.eq_const_names)
		writeMatrix(outFile, 'mat_eq', md.eq_mat, md.eq_const_names, md.var_names)


def writeTopComment (outFile, objFilepath: str, constFilepath: str) -> None:
	outFile.write(f'''
# Auto Generated File built from CSVs
#  - Objective File: {str(objFilepath)}
#  - Constraints File: {str(constFilepath)}
#
# NJDEP
	''')


def writeVector (outFile, vectorName: str, vector: list, indexNames: list) -> None:
	assert(len(vector) == len(indexNames))

	outFile.write(f'\nparam {vectorName} := \n')
	for ind, objCoef in enumerate(vector):
		outFile.write(f'\t{indexNames[ind]} {objCoef}\n')
	outFile.write(f';\n')


def writeMatrix (outFile, matrixName: str, matrix: list, rowNames: list, varNames: list, ) -> None:
	# The indexing sets need to have the same lengths as the matrix
	assert(len(matrix) == len(rowNames))
	assert(len(matrix) > 0 and len(matrix[0]) == len(varNames))

	# First, we need the line 'param matName: 1 2 ... 6 7 :='
	outFile.write(f'\nparam {matrixName}: ')
	for indName in varNames:
		outFile.write(f'{indName} ')
	outFile.write(':=\n')

	# Now we have the actual matrix
	for ind, valueList in enumerate(matrix):
		outFile.write(f'\t{rowNames[ind]} ')
		for coef in valueList:
			outFile.write(f'{coef} ')
		outFile.write('\n')
	outFile.write(';\n')









# ======================================================
#               Input via Command Line
# ======================================================

def getFilepathsFromInput () -> Union[str, str, str]:
	objFilepath   = getCSVFilepath("Objective File:   ")
	constFilepath = getCSVFilepath("Constraints File: ")
	outputFilepath = makeDATFilepath("Output .dat File: ")

	return objFilepath, constFilepath, outputFilepath


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


#
# Utilities for logging to command line

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
	# Step 1: Get + Read Input
	objFilepath, constFilepath, outputFilepath = getFilepathsFromInput()
	print()
	print("Now parsing & converting...")

	objData = openAndReadObjectiveCSV(objFilepath)
	constData = openAndReadConstraintCSV(constFilepath)

	# Step 2: Validate the data & produce a FinalModel object
	objData, constData, messages = lintInputData(objData, constData)
	if (objData == None):
		errorAndExit(messages[0])
	else:
		for msg in messages:
			printWarning(msg)	

	# Step 3: Write the finalModel
	finalModel = convertInputToFinalModel(objData, constData)
	writeOutputDat(finalModel, outputFilepath, objFilepath, constFilepath)

	print()
	print(f'All done')
	print(f'View output in {outputFilepath}')
