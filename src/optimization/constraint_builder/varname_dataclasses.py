'''
Variable Names

This file has an attrs class for storing variable names
and groups.

Michael Gorbunov
NJDEP
'''

import attrs
from enum import Enum, unique, auto
from typing import List, Dict
from attrs import define, frozen





#
# Program State Dataclasses
class ComparisonSign(Enum):
	GREATER_THAN = 0
	GE = 0
	LESS_THAN = 1
	LE = 1
	EQUAL = 2
	EQ = 2

	def __str__(self):
		if self.value == 0:
			return ">="
		if self.value == 1:
			return "<="
		if self.value == 2:
			return "= "
		else:
			return "??"
	



# @unique
# class SelectionType(Enum):
# 	EXLUDE_SELECTED = auto()
# 	INCLUDE_SELECTED = auto()


@frozen
class VarTagsInfo:
	tag_order: List[str]
	all_vars: List[List[str]]
	tag_groups: Dict[str, List[str]]


@define
class CompiledConstraint:
	name: str
	var_tags: List[List[str]]
	var_coeffs: List[float]
	compare_type: ComparisonSign
	compare_value: float


@define
class StandardConstraintGroup:
	selected_tags: Dict[str, List[str]]
	split_by_groups: List[str]
	name: str
	default_compare: ComparisonSign = ComparisonSign.EQ
	default_value: float = 0

	@staticmethod
	def createEmptyConstraint(varInfo: VarTagsInfo):
		selected_dict = {}
		for tagGroup in varInfo.tag_order:
			selected_dict[tagGroup] = []

		return StandardConstraintGroup(
			selected_tags=selected_dict,
			split_by_groups=[],
			name="unnamed constraint group",
			default_compare=ComparisonSign.EQUAL,
			default_value=0.0
		)


@define
class GlobalState():
	varTags: VarTagsInfo
	constrGroupList: List[StandardConstraintGroup]



