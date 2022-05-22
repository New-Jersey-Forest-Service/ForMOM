'''
Constraint Processor

This file does the actual processing:
 - generating constraint classes
 - reading files
 - saving to custom format


Michael Gorbunov
NJDEP / NJFS
Started 05/21/2022
'''

import varname_dataclasses as models
from pathlib import Path
from typing import List
import csv
import sys
import re


# TODO: Remove main method, this file is not meant to actually be run
def main():
	# Input
	objCSVPath = getCSVFilepath("Objective file: ")
	varNames = readAllObjVarnames(objCSVPath)
	delimiter = input("Delimiter: ")

	# Linting
	errMsg = lintVarNames(varNames, delimiter)
	if errMsg != None:
		errorAndExit(errMsg)

	# Processing
	numGroups = getNumGroups(varNames[0], delimiter)
	groupIDLists = splitsVarsIntoGroupIDs(varNames, delimiter, numGroups)

	# Input
	groupNames = getGroupNames(groupIDLists)

	# Processing

	




#
# Processing
#

def splitsVarsIntoGroupIDs (varNames: List[str], delim: str, numGroups: int) -> List[List[str]]:
	'''
		Takes a list of variables in the form

		[	167S_2021_NM,
		 	167S_2025_NM,
		 	167N_2025_NM,
		 	167N_2030_SBP	]

		and returns lists of each individual group

		[	[167S, 167N],
			[2021, 2025, 2030],
			[NM, SBP]	]
	'''
	groupIDLists = []
	for i in range(numGroups):
		groupIDLists.append([])
	
	for var in varNames:
		splitUpGroups = splitVarIntoGroups(var, delim)
		for ind, groupID in enumerate(splitUpGroups):
			groupIDLists[ind].append(groupID)

	for ind, groupIDs in enumerate(groupIDLists):
		groupIDLists[ind] = list(set(groupIDs))
		groupIDLists[ind].sort()

	return groupIDLists


def getNumGroups (var: str, delim: str) -> int:
	return len(splitVarIntoGroups(var, delim))


def splitVarIntoGroups (var: str, delim: str) -> List[str]:
	return re.split(delim + "+", var)





#
# Linting
#

def lintVarNames (varNames: List[str], delim: str) -> str:
	'''
	Goes through the list of variable names and checks that they're nice
	 - returns None if there are no erors
	 - returns an error message string if there are errors
	'''
	VALID_DELIMITERS = "_-= "
	# All group names must be exclusively alphanumeric (A-Z, a-z, 0-9)
	GROUP_NAME_REGEX = "^[A-Za-z0-9]+$"


	# [[ Check ]] At least one variable
	if (varNames == None or len(varNames) == 0):
		return "Empty or None list passed in"

	
	# [[ Check ]] Delimiter is valid
	if len(delim) == 0:
		return f'Empty delimiter is not allowed'
	if len(delim) > 1:
		return f'Delimiter must be a single character. If you have variables of the form "167S--2021---SPBQ", usiing delimiter "-" is valid.'
	if not (delim in VALID_DELIMITERS):
		return f'Delimiter "{delim}" is invalid. It must be one of {",".join(VALID_DELIMITERS)}'


	# [[ Check ]] All group names are valid
	for var in varNames:
		for group in splitVarIntoGroups(var, delim):
			if re.search(GROUP_NAME_REGEX, group) == None:
				return f'Found invalid groupname "{group}" for variable "{var}". Groups must contain only letters and numbers'


	# [[ Check ]] All variables have the same number of groups
	firstVar = varNames[0]
	numGroups = getNumGroups(firstVar, delim)

	for var in varNames[1:]:
		testNumGroups = getNumGroups(var, delim)
		if testNumGroups != numGroups:
			return f'Variable "{var}" has a different number of groups ({testNumGroups}) compare to "{firstVar}" ({numGroups})'


def lintGroupName (groupName: str) -> str:
	'''
	Checks that the provided group name is valid, returning None if
	there are no errors or the actual error message if there is one
	'''
	GROUPNAME_MAX_LENGTH = 15
	GROUPNAME_MIN_LENGTH = 3


	# [[ Check ]] Size
	if len(groupName) < GROUPNAME_MIN_LENGTH or len(groupName) > GROUPNAME_MAX_LENGTH:
			return f'Groupname "{groupName}" is incorrect length. ' + \
				   f'It must be between {GROUPNAME_MIN_LENGTH} to {GROUPNAME_MAX_LENGTH} ' + \
				   f'characters long'





#
#  File I/O
#

def readAllObjVarnames (objCSVPath: Path) -> List[str]:
	all_vars = []

	with open(objCSVPath, 'r') as objFile:
		objCSVReader = csv.reader(objFile)
		lineCount = 0

		for row in objCSVReader:
			row = [str(x).strip() for x in row]
			lineCount += 1

			if lineCount == 1:
				continue

			all_vars.append(row[0])
	
	return all_vars








#
# Command line Input
#

GROUPNAME_MAX_LENGTH = 15

def getGroupNames (groupIDLists: List[List[str]]) -> List[str]:
	'''
		Takes the list of different group ids and asks the user
		to name them. For ex:

		input:
		[
			['167N', '167S', '409'  ...], 
			['2021', '2025', '2030' ...], 
			['PLSQ', 'PLWF', 'RBWF' ...]
		]

		output (given by user):
		[
			"species",
			"year",
			"management"
		]
	'''
	groupNames = []

	for groupIDs in groupIDLists:
		sampleMembers = None
		if len(groupIDs) < 3:
			sampleMembers = groupIDs
		else:
			sampleMembers = groupIDs[:3] + ["..."]
		membersStr = ", ".join(sampleMembers)

		name = input(f"\nGroup members: {membersStr}\nName for group? ").strip()

		errMsg = lintGroupName(name)
		if errMsg:
			errorAndExit(errMsg)

		groupNames.append(name)
	
	return groupNames





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
	firstAndLastChars = pathStr[0] + pathStr[-1]
	if firstAndLastChars == "''" or firstAndLastChars == '""':
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


