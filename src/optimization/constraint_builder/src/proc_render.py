'''
Processor for (string) Rendering

This file contains methods for string manipulation and converting data to strings.
'''

import models
from typing import List




def trimEllipsisLeft (baseStr: str, maxLen: int) -> str:
	'''
	Converts "Fsdfsadff1111" => "... sadff1111"
	'''
	if len(baseStr) <= maxLen:
		return baseStr
	
	ELLIPSIS = "... "
	return ELLIPSIS + baseStr[len(ELLIPSIS)-maxLen:]


def trimEllipsisRight (baseStr: str, maxLen: int) -> str:
	'''
	Converts "Fsdfsadff1111" => "Fsdfsad ..."
	'''
	if len(baseStr) <= maxLen:
		return baseStr
	
	ELLIPSIS = " ..."
	return baseStr[:maxLen - len(ELLIPSIS)] + ELLIPSIS


def renderSingleEq (eq: models.Equation, delim: str, charwidth:int=-1) -> str:
	leftVarsStr = _renderVarsString(eq.leftVars, eq.leftCoefs, delim)
	rightVarStr = _renderVarsString(eq.rightVars, eq.rightCoefs, delim)

	finalStr = eq.namePrefix
	if eq.nameSuffix != "":
		finalStr += delim + eq.nameSuffix
	finalStr += "\n"
	finalStr += leftVarsStr + " " + eq.comparison.toSymbols() + " " + rightVarStr
	finalStr += " + " + str(eq.constant)
	finalStr += "\n"

	return finalStr



def _renderVarsString (varTags: List[List[str]], varCoefs: List[float], delim: str) -> str:
	varStrs: List[str] = [delim.join(tags) for tags in varTags]
	coefVarStrs: List[str] = []

	for ind, varStr in enumerate(varStrs):
		coef = varCoefs[ind]

		coefStr = ''
		if coef == 1:
			pass
		elif coef == int(coef):
			coefStr = str(int(coef)) + "*"
		else:
			coefStr = str(coef) + "*"
		
		coefVarStrs.append(coefStr + varStr)
	
	return " + ".join(coefVarStrs)
		
		
def renderConstraintGroup (group: models.ConstraintGroup, delim: str, charwidth:int=-1) -> str:
	NUM_EQS = 5
	eqs = group.equations[:NUM_EQS]

	# print(f"In render method. # Eqs: {len(eqs)}, Eqs: {eqs}")
	print(f"In render method. # Eqs: {len(eqs)}")

	if len(eqs) == 0:
		return "No Constraints Exist"

	finalStr = ""
	for eq in eqs:
		finalStr += renderSingleEq(eq, delim, charwidth)
		finalStr += "\n"
	
	return finalStr


def renderCompiledConstraintOLD(constr: models.CompiledConstraint, delim: str, charwidth:int=-1) -> str:
	'''
	Converts a compile constriant into a string for previewing
	'''
	varsStr = ""

	for ind, varTags in enumerate(constr.var_tags):
		coeff = constr.var_coeffs[ind]
		coeffStr = ''

		if coeff == 1:
			pass
		elif coeff == int(coeff):
			coeffStr = str(int(coeff)) + "*"
		else:
			coeffStr = str(coeff) + "*"

		varsStr += coeffStr + delim.join(varTags)
		varsStr += " + "

	varsStr = varsStr[:-len(" + ")]
	rightHandStr = str(constr.compare_type.toSymbols()) + " " + str(constr.compare_value)
	if charwidth != -1:
		varsStr = trimEllipsisRight(varsStr, charwidth - len(rightHandStr) - 1)

	return constr.name + ":\n" + varsStr + " " + rightHandStr + "\n"


def renderMultipleCompiledConstraintsOLD(constrList: List[models.CompiledConstraint], delim: str, charWidth: int, numConstrs=5) -> str:
	'''
	Converts a list of compiled constraints
	'''
	clist = constrList
	if numConstrs != -1:
		clist = clist[:numConstrs]
	
	finalStr = ''
	for constr in clist:
		finalStr += renderCompiledConstraintOLD(constr, delim, charWidth)
		finalStr += '\n'
	
	return finalStr








if __name__ == '__main__':
	print(trimEllipsisRight("1234567890", maxLen=7))
	print(trimEllipsisLeft("1234567890", maxLen=7))