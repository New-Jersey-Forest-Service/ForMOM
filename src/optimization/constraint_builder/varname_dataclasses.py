'''
Variable Names

This file has an attrs class for storing variable names
and groups.

Michael Gorbunov
NJDEP
'''

import attrs
from typing import List, Dict
from attrs import define, frozen


@frozen
class VarTagsInfo:
	tag_order: List[str]
	all_vars: List[List[str]]
	tag_groups: Dict[str, List[str]]


@frozen
class ConstraintGroup:
	included_tags: Dict[str, List[str]]
	split_by_groups: List[str]
	name: str
