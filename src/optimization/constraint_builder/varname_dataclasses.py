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
class VarGroupIDs:
	delim: str
	all_vars: List[List[str]]
	var_groups: Dict[str, List[str]]
