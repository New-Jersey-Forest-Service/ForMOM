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
from typing import List, Dict
import itertools
import csv
import sys
import re


# TODO:
# [ ] Remove main method, this file is not meant to actually be run
# [ ] Come up with better names (groups, vars, varGroupList, etc is _really_ confusing)
# [ ] Be more strict with delimiting
#    - Only allow for one character in the delimiting ?
# [ ] Have dataclass for constraint classes
#    - There should be a sense of an abstract constraint class (group members)
#      and a concrete constraint class (which can be exactly compiled into constraints)
# [ ] Use Set instead of List for tag_groups in class models.VarTagsInfo

def main():
	# Input
	objCSVPath = getCSVFilepath("Objective file: ")
	varNamesRaw = readAllObjVarnames(objCSVPath)
	delimiter = input("Delimiter: ")

	# Linting
	errMsg = lintVarNames(varNamesRaw, delimiter)
	if errMsg != None:
		errorAndExit(errMsg)

	# Processing
	varnameTags = splitVarsToTags(varNamesRaw, delimiter)
	tagGroupMembersList = makeTagGroupMembersList(varnameTags)

	# Input
	tagGroupNames = getTagGroupNames(tagGroupMembersList)

	# Processing
	tagGroupsDict = {}
	for ind, name in enumerate(tagGroupNames):
		tagGroupsDict[name] = tagGroupMembersList[ind]

	groupsData = models.VarTagsInfo(
		tag_order = tagGroupNames,
		all_vars = varnameTags,
		tag_groups = tagGroupsDict
	)

	print(groupsData.tag_groups)
	generateConstraint(groupsData, {"species": ['167N'], "year":['2021', '2025', '2030'], "mng": ["WFNM", "PLSQ"]})

	




#
# Processing
#

def generateConstraint (allVarsInfo: models.VarTagsInfo, includedTagsDict: Dict[str, List[str]]) -> List[str]:
	'''
		Given the necessary definitions for a constraint class, this will return all variables
		matching the includeGroupIDs
	'''
	matchingNames = []
	allKeys = list(includedTagsDict.keys())
	individualGroupIds = [includedTagsDict[k] for k in allKeys]

	for varGroups in itertools.product(*individualGroupIds):
		varTags = list(varGroups)
		varName = "_".join(varTags)
		if varTags in allVarsInfo.all_vars:
			matchingNames.append(varName)
		else:
			print(f"[[ Found unused var ]]: {varName}")

	print()
	print("\n > ".join(matchingNames))
	return matchingNames


def makeTagGroupMembersList (allVarTags: List[List[str]]) -> List[List[str]]:
	'''
		Takes a list of variables in the form

		[	[167S, 2021, NM],
		 	[167S, 2025, NM],
		 	[167N, 2025, NM],
		 	[167N, 2030, SBP]	]

		and returns lists of each individual tag group,
		in the order they appear within the variables.

		[	[167S, 167N],
			[2021, 2025, 2030],
			[NM, SBP]	] 
	'''
	tagGroupMembers = []
	for i in range(len(allVarTags[0])):
		tagGroupMembers.append(set())
	
	for varTags in allVarTags:
		for ind, groupID in enumerate(varTags):
			tagGroupMembers[ind].add(groupID)

	for ind, tags in enumerate(tagGroupMembers):
		tagGroupMembers[ind] = list(tags)
		tagGroupMembers[ind].sort()

	return tagGroupMembers


def splitVarsToTags (rawVarnames: List[str], delim: str) -> List[List[str]]:
	'''
	Splits variables up by their delimiter
	input:  [ "167S_2021_NM",          "167N_2030_SBP" ] 
	output: [ ["167S", "2021", "NM"], ["167N", "2030", "SBP"] ]
	'''
	return [splitRawVarIntoTags(x, delim) for x in rawVarnames]


def getNumTagsInRawVar (varnameRaw: str, delim: str) -> int:
	return len(splitRawVarIntoTags(varnameRaw, delim))


def splitRawVarIntoTags (varnameRaw, delim: str) -> List[str]:
	return re.split(delim + "+", varnameRaw)





#
# Linting
#

def lintVarNames (varNamesRaw, delim: str) -> str:
	'''
	Goes through the list of variable names and checks that they're nice
	 - returns None if there are no erors
	 - returns an error message string if there are errors
	'''
	VALID_DELIMITERS = "_-= "
	# All group names must be exclusively alphanumeric (A-Z, a-z, 0-9)
	GROUP_NAME_REGEX = "^[A-Za-z0-9]+$"


	# [[ Check ]] At least one variable
	if (varNamesRaw == None or len(varNamesRaw) == 0):
		return "Empty or None list passed in"

	
	# [[ Check ]] Delimiter is valid
	if len(delim) == 0:
		return f'Empty delimiter is not allowed'
	if len(delim) > 1:
		return f'Delimiter must be a single character. If you have variables of the form "167S--2021---SPBQ", usiing delimiter "-" is valid.'
	if not (delim in VALID_DELIMITERS):
		return f'Delimiter "{delim}" is invalid. It must be one of {",".join(VALID_DELIMITERS)}'


	# [[ Check ]] All group names are valid
	for var in varNamesRaw:
		for group in splitRawVarIntoTags(var, delim):
			if re.search(GROUP_NAME_REGEX, group) == None:
				return f'Found invalid groupname "{group}" for variable "{var}". Groups must contain only letters and numbers'


	# [[ Check ]] All variables have the same number of groups
	firstVar = varNamesRaw[0]
	numGroups = getNumTagsInRawVar(firstVar, delim)

	for var in varNamesRaw[1:]:
		testNumGroups = getNumTagsInRawVar(var, delim)
		if testNumGroups != numGroups:
			return f'Variable "{var}" has a different number of groups ({testNumGroups}) compare to "{firstVar}" ({numGroups})'


def lintTagGroupName (tagGroupName) -> str:
	'''
	Checks that the provided group name is valid, returning None if
	there are no errors or the actual error message if there is one
	'''
	GROUPNAME_MAX_LENGTH = 15
	GROUPNAME_MIN_LENGTH = 3

	# [[ Check ]] Size
	if len(tagGroupName) < GROUPNAME_MIN_LENGTH or len(tagGroupName) > GROUPNAME_MAX_LENGTH:
			return f'Groupname "{tagGroupName}" is incorrect length. ' + \
				   f'It must be between {GROUPNAME_MIN_LENGTH} to {GROUPNAME_MAX_LENGTH} ' + \
				   f'characters long'





#
#  File I/O
#

def readAllObjVarnames (objCSVPath: Path) -> List[str]:
	allVarnames = []

	with open(objCSVPath, 'r') as objFile:
		objCSVReader = csv.reader(objFile)
		lineCount = 0

		for row in objCSVReader:
			row = [str(x).strip() for x in row]
			lineCount += 1

			if lineCount == 1:
				continue

			allVarnames.append(row[0])
	
	return allVarnames








#
# Command line Input
#

GROUPNAME_MAX_LENGTH = 15

def getTagGroupNames (tagGroupsList: List[List[str]]) -> List[str]:
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
	tagGroupNames = []

	for tagGroup in tagGroupsList:
		sampleMembers = None
		if len(tagGroup) < 3:
			sampleMembers = tagGroup
		else:
			sampleMembers = tagGroup[:3] + ["..."]
		sampleStr = ", ".join(sampleMembers)

		name = input(f"\nGroup members: {sampleStr}\nName for group? ").strip()

		errMsg = lintTagGroupName(name)
		if errMsg:
			errorAndExit(errMsg)

		tagGroupNames.append(name)
	
	return tagGroupNames





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




'''
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣤⣤⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⠟⠉⠉⠉⠉⠉⠉⠉⠙⠻⢶⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣷⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡟⠀⣠⣶⠛⠛⠛⠛⠛⠛⠳⣦⡀⠀⠘⣿⡄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⠁⠀⢹⣿⣦⣀⣀⣀⣀⣀⣠⣼⡇⠀⠀⠸⣷⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡏⠀⠀⠀⠉⠛⠿⠿⠿⠿⠛⠋⠁⠀⠀⠀⠀⣿⡄⣠
⠀⠀⢀⣀⣀⣀⠀⠀⢠⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡇⠀
⠿⠿⠟⠛⠛⠉⠀⠀⣸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⠀
⠀⠀⠀⠀⠀⠀⠀⢸⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⠀
⠀⠀⠀⠀⠀⠀⠀⣾⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀
⠀⠀⠀⠀⠀⠀⠀⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀
⠀⠀⠀⠀⠀⠀⢰⣿⠀⠀⠀⠀⣠⡶⠶⠿⠿⠿⠿⢷⣦⠀⠀⠀⠀⠀⠀⠀⣿⠀
⠀⠀⣀⣀⣀⠀⣸⡇⠀⠀⠀⠀⣿⡀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⣿⠀
⣠⡿⠛⠛⠛⠛⠻⠀⠀⠀⠀⠀⢸⣇⠀⠀⠀⠀⠀⠀⣿⠇⠀⠀⠀⠀⠀⠀⣿⠀
⢻⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⡟⠀⠀⢀⣤⣤⣴⣿⠀⠀⠀⠀⠀⠀⠀⣿⠀
⠈⠙⢷⣶⣦⣤⣤⣤⣴⣶⣾⠿⠛⠁⢀⣶⡟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡟⠀
⢷⣶⣤⣀⠉⠉⠉⠉⠉⠄⠀⠀⠀⠀⠈⣿⣆⡀⠀⠀⠀⠀⠀⠀⢀⣠⣴⡾⠃⠀
⠀⠈⠉⠛⠿⣶⣦⣄⣀⠀⠀⠀⠀⠀⠀⠈⠛⠻⢿⣿⣾⣿⡿⠿⠟⠋⠁⠀⠀⠀


			 Why so Sus ?

'''
