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

from copy import copy, deepcopy
import sys

print("=====")
print("\n\n".join(sys.path))
print("=====")

import models
from pathlib import Path
from typing import List, Dict
import itertools
import csv

import io_cmd
import linting as lint


# TODO:
# [ ] Remove main method, this file is not meant to actually be run
# [~] Come up with better names (groups, vars, varGroupList, etc is _really_ confusing)
# [ ] Be more strict with delimiting
#    - Only allow for one character in the delimiting ?
# [~] Have dataclass for constraint classes
#    - There should be a sense of an abstract constraint class (group members)
#      and a concrete constraint class (which can be exactly compiled into constraints)
# [ ] Use Set instead of List for tag_groups in class models.VarTagsInfo
# [ ] Adjust architecture so all method for compiling constraints groups -> constraints
#      live inside varname_dataclasses.py
# [ ] Instead of returning lists of copmiled constraints, return an iterator or generator function
# [ ] Have a way to be Exclusive or Inclusive with categories ??
#    - We may want a constriant that for example applies to all but 2 tree species, and this would allow
#      for generalizing the scripts for other obj inputs (other states ?)
# [ ] Add type checks for important processing functions


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


def makeTagGroupMembersList (varnamesRaw: List[str], delim: str) -> List[List[str]]:
	'''
		Takes a list of variables in the form

		[	"167S_2021_NM",
		 	"167S_2025_NM",
		 	"167N_2025_NM",
		 	"167N_2030_SBP"	]

		and returns lists of tags in individual groups
		in the order they appear within the variables.

		[	[167S, 167N],      
			[2021, 2025, 2030],
			[NM, SBP]	] 
	'''
	tagGroupMembers = []
	for _ in range(len(varnamesRaw[0].split(delim))):
		tagGroupMembers.append(set())
	
	for varName in varnamesRaw:
		varTags = varName.split(delim)
		for ind, groupID in enumerate(varTags):
			tagGroupMembers[ind].add(groupID)

	for ind, tags in enumerate(tagGroupMembers):
		tagGroupMembers[ind] = list(tags)
		tagGroupMembers[ind].sort()

	return tagGroupMembers


def buildVarTagsInfoObject (varnamesRaw: List[str], delim: str, tagGroupNames: List[str]) -> models.VarTagsInfo:
	'''
		DOES NOT LINT. Make sure to call the linting functions before passing into this.
		With poor data, this will throw an error (or worse, fail silently)
	'''
	sortedVarsRaw = deepcopy(varnamesRaw)
	sortedVarsRaw.sort()
	tagGroupMembersList = makeTagGroupMembersList(varnamesRaw, delim)

	tagGroupsDict = {}
	for ind, name in enumerate(tagGroupNames):
		tagGroupsDict[name] = tagGroupMembersList[ind]

	return models.VarTagsInfo(
		delim = delim,
		tag_order = tagGroupNames,
		all_vars = [x.split(delim) for x in sortedVarsRaw],
		tag_members = tagGroupsDict
	)


def buildConstraintsFromStandardConstraintGroup (varInfo: models.VarTagsInfo, stdConGroup: models.StandardConstraintGroup) -> List[models.CompiledConstraint]:
	conDict = {}
	delim = varInfo.delim

	#	
	# Generate names of all constraints
	conNames = []
	conNameTags = []

	# Iterating through varInfo.tag_order guarantees the order is correct
	for tagGroup in varInfo.tag_order:
		if tagGroup in stdConGroup.split_by_groups:
			conNameTags.append(stdConGroup.selected_tags[tagGroup])
	
	for conTags in itertools.product(*conNameTags):
		conNames.append(delim.join([stdConGroup.constr_prefix] + list(conTags)))
	if len(conNames) == 0:
		conNames = [stdConGroup.constr_prefix]
	
	# The names are used as keys in the constraint dictionary, so we
	# populate the dictionary with empty lists
	for name in conNames:
		conDict[name] = []
	
	# print(conDict)
	

	#
	# Generate the indicies that get split by
	tagListsByGroup = [] # this is a 2D array
	for tagGroup in varInfo.tag_order:
		tagListsByGroup.append(stdConGroup.selected_tags[tagGroup])
	
	# TODO: Refactor to avoid needing indToSplitBy
	indToSplitBy = []
	for splitByGroup in stdConGroup.split_by_groups:
		ind = varInfo.tag_order.index(splitByGroup)
		indToSplitBy.append(ind)
	indToSplitBy.sort()


	#
	# Generate all potential variables and split into multiple constraints
	for varTags in itertools.product(*tagListsByGroup):
		varTags = list(varTags)
		if not (varTags in varInfo.all_vars):
			continue

		tagsToSplitBy = []
		for ind in indToSplitBy:
			tagsToSplitBy.append(varTags[ind])
		conName = delim.join([stdConGroup.constr_prefix] + tagsToSplitBy)

		conDict[conName].append(varTags)

	# Check for potential empty constraints & convert to list
	allKeys = list(conDict.keys())
	compiledConList = []

	for key in allKeys:
		numVars = len(conDict[key])

		if numVars == 0:
			io_cmd.printInfo(f"Found empty constraint {key}")
		else:
			compiledConList.append(
				models.CompiledConstraint(
					name = key,
					var_tags = conDict[key],
					var_coeffs = [stdConGroup.default_coef] * numVars,
					compare_type = stdConGroup.default_compare,
					compare_value = stdConGroup.default_rightside
				)
			)
	
	return compiledConList












if __name__ == '__main__':
	# Input
	objCSVPath = io_cmd.getCSVFilepath("Objective File: ")

	varnamesRaw = readVarnamesRaw(objCSVPath)
	delim = input(f"Sample Var '{varnamesRaw[0]}' | Delimiter: ")
	errMsg = lint.lintAllVarNamesRaw(varnamesRaw, delim)
	if errMsg:
		io_cmd.errorAndExit(errMsg)

	tagMems = makeTagGroupMembersList(varnamesRaw, delim)
	tagNames = io_cmd.getTagGroupNames(tagMems)
	errMsg = lint.lintAllTagGroupNames(tagNames)
	if errMsg:
		io_cmd.errorAndExit(errMsg)

	# Processing
	varInfo = buildVarTagsInfoObject(varnamesRaw, delim, tagNames)
	print(varInfo)



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
