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
from typing import Any, List, Dict, Type
from copy import deepcopy





# TODO: Redo a _lot_ of this



#
# Program State Dataclasses

@unique
class ComparisonSign(Enum):
	GE = '>='
	LE = '<='
	EQ = '=='

	def toSymbols (self):
		return self._value_

	@staticmethod
	def fromSybols (symbols: str):
		stripped = symbols.strip()

		if not stripped in _compSignMap.keys():
			return None
		return _compSignMap[stripped]

_compSignMap = {}
for cs in ComparisonSign:
	_compSignMap[cs._value_] = cs


@attrs.frozen
class VarTagsInfo:
	delim: str
	tag_order: List[str]
	all_vars: List[List[str]]
	tag_members: Dict[str, List[str]]


@attrs.define
class CompiledConstraint:
	name: str
	var_tags: List[List[str]]
	var_coeffs: List[float]
	compare_type: ComparisonSign
	compare_value: float





# TODO: Purge this little yuckling
@attrs.define
class StandardConstraintGroup:
	selected_tags: Dict[str, List[str]]
	split_by_groups: List[str]
	constr_prefix: str
	default_compare: ComparisonSign = ComparisonSign.EQ
	default_rightside: float = 0
	defualt_coef: float = 1

	@staticmethod
	def createEmptyConstraint(varInfo: VarTagsInfo):
		selected_dict = {}
		for tag in varInfo.tag_order:
			selected_dict[tag] = []
		
		return StandardConstraintGroup(
			selected_dict, [], "empty_group"
		)















@attrs.define
class ConstraintEquation:
	namePrefix: str
	nameSuffix: str
	constant: float

	leftVars: List[List[str]]
	leftCoefs: List[float]
	rightVars: List[List[str]]
	rightCoefs: List[float]

	def getName(self):
		return self.namePrefix + self.nameSuffix


@attrs.define
class ConstraintGroup:
	groupName: str
	equations: List[ConstraintEquation]

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
	def createEmptyConstraint(varInfo: VarTagsInfo):
		selectedTags = {}
		for tag in varInfo.tag_order:
			selectedTags[tag] = []
		
		return SetupConstraintGroup(
			namePrefix="unnamed",
			splitBy=[],
			defComp=ComparisonSign.EQ,
			defLeftCoef=1,
			defRightCoef=1,
			defConstant=0,
			selLeftTags=selectedTags,
			selRightTags=deepcopy(selectedTags)
		)


@attrs.define
class ProjectState:
	# TODO: Re-evaluate how the data is being split up. It feels a little weird
	#       for the delimiter to be here. Maybe put it into VarTagsInfo? Maybe into compilation class?
	varTags: VarTagsInfo
	constrGroupList: List[StandardConstraintGroup]

	@staticmethod
	def createEmptyprojectState():
		return ProjectState(
			None, None
		)



def toOutputStr (obj: Any, type: Type) -> str:
	if not isinstance(obj, type):
		objType = type(obj)
		raise TypeError(f"Expected {type} got {objType} ")
	
	return json.dumps(cattrs.unstructure(obj))


# TODO: How do I type annotate this ??
# TODO: Add versioning to file saves ??
def fromOutputStr (strObj: str, type: Type):
	try:
		return cattrs.structure_attrs_fromdict(json.loads(strObj), type)
	except Exception as e:
		print("[[ XX ERROR ]] Unable to read file. It may be corrupt or comes from an older version of the program")
		print()
		raise e







