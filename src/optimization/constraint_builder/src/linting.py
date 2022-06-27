
from typing import List, Dict
import re



def lintAllVarNamesRaw (varNamesRaw: List[str], delim: str) -> str:
	'''
	Goes through the list of variable names and checks that they're nice
	 - returns None if there are no erors
	 - returns an error message string if there are errors
	'''
	VALID_DELIMITERS = "_-= "
	# All tag members must be exclusively alphanumeric (A-Z, a-z, 0-9)
	TAG_MEMBER_REGEX = "^[A-Za-z0-9]+$"


	# [[ Check ]] At least one variable
	if (varNamesRaw == None or len(varNamesRaw) == 0):
		return "Empty or None list passed in"

	firstVar = varNamesRaw[0]

	
	# [[ Check ]] Delimiter is valid
	if len(delim) == 0:
		return f'Empty delimiter is not allowed'
	if len(delim) > 1:
		return f'Delimiter must be a single character.'
	if not (delim in VALID_DELIMITERS):
		return f'Delimiter "{delim}" is invalid. It must be one of {",".join(VALID_DELIMITERS)}'


	# [[ Check ]] Delimiter is inside of variable
	if not delim in firstVar:
		return f'Delimiter "{delim}" not found inside variable {firstVar}'


	# [[ Check ]] All group names are valid
	for var in varNamesRaw:
		for tag in var.split(delim):
			if re.search(TAG_MEMBER_REGEX, tag) == None:
				return f'Found invalid groupname "{tag}" for variable "{var}". Groups must contain only letters and numbers'


	# [[ Check ]] All variables have the same number of groups
	numGroups = len(firstVar.split(delim))

	for var in varNamesRaw[1:]:
		testNumGroups = len(var.split(delim))
		if testNumGroups != numGroups:
			return f'Variable "{var}" has a different number of groups ({testNumGroups}) compare to "{firstVar}" ({numGroups})'


def lintTagGroupName (tagName: str) -> str:
	'''
	Checks that the provided group name is valid, returning None if
	there are no errors or the actual error message if there is one
	'''
	TAGNAME_MAX_LENGTH = 15
	TAGNAME_MIN_LENGTH = 3
	TAGNAME_REGEX = "^[A-Za-z0-9_-]+$"

	# [[ Check ]] Size
	if len(tagName) < TAGNAME_MIN_LENGTH:
		return f'Groupname "{tagName}" too short. Must be at least {TAGNAME_MIN_LENGTH} characters'
	elif len(tagName) > TAGNAME_MAX_LENGTH:
		return f'Groupname "{tagName}" is too long. Name is {len(tagName)} characters long, but max is {TAGNAME_MAX_LENGTH}'
	
	# [[ Check ]] Only alphanumeric names allowed
	if re.search(TAGNAME_REGEX, tagName) == None:
		# Lol this is so inefficient but its kinda funny
		for c in tagName:
			if re.search(TAGNAME_REGEX, str(c)) == None:
				return f'Invalid groupname "{tagName}". Illegal character "{c}"'


def lintAllTagGroupNames (listTagNames: List[str]) -> str:
	'''
	Checks a list of tag names instead of a single one (like lintTagGroupName)
	'''
	# [[ Check ]] All variable named
	for ind, name in enumerate(listTagNames):
		if name == None or name == '':
			return f'Not all groups are named'
	
	# [[ Check ]] Individually fine
	for name in listTagNames:
		err = lintTagGroupName(name)
		if err:
			return err

	# [[ Check ]] Duplicate names
	if len(set(listTagNames)) != len(listTagNames):
		return f'Found duplicate names'


# TODO: Have a general constraintgroup linting? Make sure coefficients != 0, etc
def lintConstrGroupName (groupName: str) -> str:
	'''
	Checks that the provided group name is valid, returning None if
	there are no errors or the actual error message if there is one
	'''
	GROUPNAME_MAX_LENGTH = 30
	GROUPNAME_MIN_LENGTH = 3
	GROUPNAME_REGEX = "^[A-Za-z0-9_-]+$"

	# [[ Check ]] Size
	if len(groupName) < GROUPNAME_MIN_LENGTH:
		return f'Groupname "{groupName}" too short. Must be at least {GROUPNAME_MIN_LENGTH} characters'
	elif len(groupName) > GROUPNAME_MAX_LENGTH:
		return f'Groupname "{groupName}" is {len(groupName) - GROUPNAME_MAX_LENGTH} characters too long.'
	
	# [[ Check ]] Only alphanumeric names allowed
	if re.search(GROUPNAME_REGEX, groupName) == None:
		for c in groupName:
			if re.search(GROUPNAME_REGEX, str(c)) == None:
				return f'Invalid groupname "{groupName}". Illegal character "{c}"'


def lintAllConstrGroupNames (listGroupNames: List[str]) -> str:
	# [[ Check ]] All groups named
	for ind, name in enumerate(listGroupNames):
		if name == None or name == '':
			return f'Not all groups are named'
	
	# [[ Check ]] Individually fine
	for name in listGroupNames:
		err = lintConstrGroupName(name)
		if err:
			return err

	# [[ Check ]] Duplicate names
	if len(set(listGroupNames)) != len(listGroupNames):
		duplicates = set([x for x in listGroupNames if listGroupNames.count(x) > 1])
		return f'Found duplicate group names {duplicates}'
