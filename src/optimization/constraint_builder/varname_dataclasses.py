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


@unique
class SelectionType(Enum):
	EXLUDE_SELECTED = auto()
	INCLUDE_SELECTED = auto()


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


@frozen
class StandardConstraintGroup:
	selected_tags: Dict[str, List[str]]
	selection_type: SelectionType
	split_by_groups: List[str]
	name: str
