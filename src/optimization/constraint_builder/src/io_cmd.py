
import sys
from pathlib import Path
from typing import List

import linting as lint


def getTagGroupNames (tagMems: List[List[str]]) -> List[str]:
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

	for tagGroup in tagMems:
		sampleMembers = None
		if len(tagGroup) < 3:
			sampleMembers = tagGroup
		else:
			sampleMembers = tagGroup[:3] + ["..."]
		sampleStr = ", ".join(sampleMembers)

		name = input(f"\nGroup members: {sampleStr}\nName for group? ").strip()

		errMsg = lint.lintTagGroupName(name)
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

	if len(pathStr) < 2:
		errorAndExit("Supplied filepath is too short")

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
	print('\t[[ XX Error ]]')
	print(f'{errMessage}')
	print()
	print("Aborting.")
	sys.exit(1)


def printWarning (warnMessage: str):
	print(f'\t[[ !! Warning ]] : {warnMessage}')


def printInfo (infoMessage: str):
	print(f'\t[[ ~~ Info ]] : {infoMessage}')



