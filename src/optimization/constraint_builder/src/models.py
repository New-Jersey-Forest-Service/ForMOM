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


# TODO: Look into attrs linting to guarantee state is sensible (ex: no spaces in constraint name)
@attrs.define
class StandardConstraintGroup:
	selected_tags: Dict[str, List[str]]
	split_by_groups: List[str]
	constr_prefix: str
	default_compare: ComparisonSign = ComparisonSign.EQ
	default_rightside: float = 0
	default_coef: float = 1

	@staticmethod
	def createEmptyConstraint(varInfo: VarTagsInfo):
		selected_dict = {}
		for tagGroup in varInfo.tag_order:
			selected_dict[tagGroup] = []

		return StandardConstraintGroup(
			selected_tags=selected_dict,
			split_by_groups=[],
			constr_prefix="empty_group",
			default_compare=ComparisonSign.EQ,
			default_rightside=0.0,
			default_coef=1.0
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







