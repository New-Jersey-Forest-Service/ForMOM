'''
Variable Names

This file has an attrs class for storing variable names
and groups.

Michael Gorbunov
NJDEP
'''

import json
import attrs
import cattrs
from enum import Enum, unique, auto
from typing import Any, List, Dict, Type, Union
from copy import deepcopy







#
# Program State Dataclasses

@unique
class ComparisonSign(Enum):
	GE = '>='
	LE = '<='
	EQ = '=='

	def toSymbols (self) -> str:
		return self._value_
	
	def exportName (self) -> str:
		return _toExportName[self]

	@staticmethod
	def fromSybols (symbols: str):
		stripped = symbols.strip()

		if not stripped in _compSignMap.keys():
			return None
		return _compSignMap[stripped]

_toExportName = {
	ComparisonSign.GE: 'ge',
	ComparisonSign.LE: 'le',
	ComparisonSign.EQ: 'eq'
}

_compSignMap = {}
for cs in ComparisonSign:
	_compSignMap[cs._value_] = cs




@attrs.frozen
class VarsData:
	delim: str
	tag_order: List[str]
	all_vars: List[List[str]]
	tag_members: Dict[str, List[str]]
















@attrs.define
class Equation:
	namePrefix: str
	nameSuffix: str
	constant: float
	comparison: ComparisonSign

	leftVars: List[List[str]]
	leftCoefs: List[float]
	rightVars: List[List[str]]
	rightCoefs: List[float]

	# def getName(self):
	# 	return self.namePrefix + self.nameSuffix


@attrs.define
class ConstraintGroup:
	groupName: str
	equations: List[Equation]

	# TODO: These may be unneeded ??
	# These are meant to go unchanged once the group
	SPLIT_BY: List[str]
	DEFAULT_COMPARE: ComparisonSign
	DEFAULT_LEFT_COEF: float
	DEFAULT_RIGHT_COEF: float


@attrs.define
class SetupConstraintGroup:
	namePrefix: str
	splitBy: List[str]
	defComp: ComparisonSign
	defLeftCoef: float
	defRightCoef: float
	defConstant: float

	selLeftTags: Dict[str, List[str]]
	selRightTags: Dict[str, List[str]]

	@staticmethod
	def createEmptySetup(varData: VarsData):
		selectedTags = {}
		for tag in varData.tag_order:
			selectedTags[tag] = []
		
		return SetupConstraintGroup(
			namePrefix="unnamed",
			splitBy=[],
			defComp=ComparisonSign.EQ,
			defLeftCoef=1.0,
			defRightCoef=1.0,
			defConstant=0,
			selLeftTags=selectedTags,
			selRightTags=deepcopy(selectedTags)
		)












@attrs.define
class ProjectState:
	varData: VarsData
	# constraintList: List[ConstraintGroup]
	setupList: List[SetupConstraintGroup]

	# The actual value of the version doesn't matter
	# what matters is each new version has a different
	# variable name
	VERSION01: str = None

	@staticmethod
	def createEmptyProjectState ():
		return ProjectState(
			None, None
		)


@attrs.define
class ProjectState_V0_0:
	varData: VarsData
	setupList: List[SetupConstraintGroup]

	# This state is before versioning was added, hence no version number
	
	def convertUp(self) -> ProjectState:
		'''
			Converts this object into a more recent project state
		'''
		new_self = deepcopy(self)

		return ProjectState(
			varData=new_self.varData,
			setupList=new_self.setupList
		)




_model_versions = [
	ProjectState,
	ProjectState_V0_0
]

def readProjectStateFile (filepath: str) -> Union[ProjectState, str]:
	'''
	Attempts to read the project file at the filepath.

	If reading an older project file, will convert up
	to a more recent version.

	Returns None and an error message if unsuccesful.
	'''
	fileData = None
	try:
		with open(filepath, 'r') as file:
			fileData = file.read()
	except:
		pass

	if fileData == None:
		return None, "Unable to read file"
	
	# See if the data is in fact a model file
	model = None
	for m in _model_versions:
		try:
			model = fromOutputStr(fileData, m)
		except:
			continue
	
	if model == None:
		return None, "Not a valid project file, unable to parse"
	
	# Cast the model up
	while not isinstance(model, ProjectState):
		_prevModel = model
		model = model.convertUp()

		if _prevModel == model:
			return None, "Conversion code is messed up"
	
	return model, None
	
	




def toOutputStr (obj: Any, type: Type) -> str:
	if not isinstance(obj, type):
		objType = type(obj)
		raise TypeError(f"Expected {type} got {objType} ")
	
	return json.dumps(cattrs.unstructure(obj))


# TODO: How do I type annotate this ??
def fromOutputStr (strObj: str, type: Type):
	try:
		return cattrs.structure_attrs_fromdict(json.loads(strObj), type)
	except Exception as e:
		# print("[[ XX ERROR ]] Unable to read file. It may be corrupt or comes from an older version of the program")
		# print()
		raise e







