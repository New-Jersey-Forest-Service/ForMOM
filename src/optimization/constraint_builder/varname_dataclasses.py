'''
Variable Names

This file has an attrs class for storing variable names
and groups.

Michael Gorbunov
NJDEP
'''

import json
import attrs
from enum import Enum, unique, auto
from typing import Any, List, Dict, Type

import cattrs





#
# Program State Dataclasses

@unique
class ComparisonSign(Enum):
	GE = 'ge'
	LE = 'le'
	EQ = 'eq'

	# def __str__(self):
	# 	if self.value == 0:
	# 		return ">="
	# 	if self.value == 1:
	# 		return "<="
	# 	if self.value == 2:
	# 		return "= "
	# 	else:
	# 		return "??"
	



# @unique
# class SelectionType(Enum):
# 	EXLUDE_SELECTED = auto()
# 	INCLUDE_SELECTED = auto()


@attrs.frozen
class VarTagsInfo:
	tag_order: List[str]
	all_vars: List[List[str]]
	tag_groups: Dict[str, List[str]]


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
	delim: str
	varTags: VarTagsInfo
	constrGroupList: List[StandardConstraintGroup]

	@staticmethod
	def createEmptyprojectState():
		return ProjectState(
			None, None, None
		)



def toOutputStr (obj: Any, type: Type) -> str:
	if not isinstance(obj, type):
		objType = type(obj)
		raise TypeError(f"L + ratio. Expected {type} got {objType} ")
	
	return json.dumps(cattrs.unstructure(obj))


# TODO: How do I type annotate this ??
def fromOutputStr (strObj: str, type: Type):
	return cattrs.structure_attrs_fromdict(json.loads(strObj), type)







