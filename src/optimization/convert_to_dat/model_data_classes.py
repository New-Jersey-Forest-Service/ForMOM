'''
Model Data Classes

These classes are used to store the model data in objects
instead of as a bunch of parallel Lists. The idea is the
input classes should store the input data and then be
sanitized. Afterwards, a FinalModel object is initialized
and read into the .dat file.

Everything is an attrs class, which are effectively structs
with extra sanitation optoins.
https://www.attrs.org/en/stable/
'''

import sys
from typing import List
from attrs import define, frozen


@define
class InputObjectiveData:
	var_names: List[str] = []
	obj_coeffs: List[float] = []


@define
class InputConstraintData:
	var_names: List[str] = []
	const_names: List[str] = []

	# These are all parallel Lists
	vec_const_bounds: List[float] = []
	vec_operators: List[str] = []
	mat_constraint_coeffs: List[List[float]] = []


@frozen
class FinalModel:
	'''
	This class represents all the final constraints & names
	When created it should already be valid. The idea is do
	error checking & linting first, then instantiate this class,
	then write it to the dat file.
	'''

	# Because this class is immutable, there are no
	# defaults. All values placed should be final
	var_names: List[str]
	obj_coeffs: List[float]

	le_const_names: List[str]
	ge_const_names: List[str]
	eq_const_names: List[str]

	le_vec: List[float]
	ge_vec: List[float]
	eq_vec: List[float]

	le_mat: List[List[float]]
	ge_mat: List[List[float]]
	eq_mat: List[List[float]]



if __name__ == '__main__':
	print("This file is not meant to be run")
	sys.exit(1)
