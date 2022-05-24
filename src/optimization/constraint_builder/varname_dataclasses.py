'''
Variable Names

This file has an attrs class for storing variable names
and groups.

Michael Gorbunov
NJDEP
'''

import attrs
from enum import Enum, unique
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

@frozen
class VarTagsInfo:
	tag_order: List[str]
	all_vars: List[List[str]]
	tag_groups: Dict[str, List[str]]


@frozen
class CompiledConstraint:
	name: str
	var_tags: List[List[str]]
	var_coeffs: List[float]
	compare_type: ComparisonSign
	compare_value: float

@frozen
class StandardConstraintGroup:
	included_tags: Dict[str, List[str]]
	split_by_groups: List[str]
	name: str
