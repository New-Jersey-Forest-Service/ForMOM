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


def renderCompiledConstraint(constr: models.CompiledConstraint, delim: str, charwidth:int=-1) -> str:
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


def renderMultipleCompiledConstraints(constrList: List[models.CompiledConstraint], delim: str, charWidth: int, numConstrs=5) -> str:
	'''
	Converts a list of compiled constraints
	'''
	clist = constrList
	if numConstrs != -1:
		clist = clist[:numConstrs]
	
	finalStr = ''
	for constr in clist:
		finalStr += renderCompiledConstraint(constr, delim, charWidth)
		finalStr += '\n'
	
	return finalStr








if __name__ == '__main__':
	print(trimEllipsisRight("1234567890", maxLen=7))
	print(trimEllipsisLeft("1234567890", maxLen=7))