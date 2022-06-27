'''
dev.py

This file holds constants and functions meant for
development.
'''

from typing import List
import proc_constraints as proc
import io_file
import models


def dummyProjectState() -> models.ProjectState:

	varnamesRaw = io_file.readVarnamesRaw(
		# './sample_data/minimodel_obj.csv', 
		'/home/velcro/Documents/Professional/NJDEP/TechWork/ForMOM/src/optimization/constraint_builder/sample_data/minimodel_obj.csv',
		)

	varTagsInfo = proc.buildVarTagsInfoObject(
		varnamesRaw,
		'_', 
		['for_type', 'year', 'mng']
		)

	# TODO: To remove future polymorphism, add a general constriantinfo class ?
	constrGroupList: List[models.StandardConstraintGroup] = [
		models.StandardConstraintGroup(
			selected_tags={'for_type': ['167N', '167S', '409'], 'year': ["2021", "2025", "2030", "2050"], 'mng': ['RBWF', 'PLSQ', 'TB']},
			split_by_groups=['for_type'],
			constr_prefix="MaxAcresBySpecies",
			default_compare=models.ComparisonSign.EQ,
			default_rightside=0
		),
		models.StandardConstraintGroup.createEmptyConstraint(varTagsInfo)
	]

	return models.ProjectState(
		varTags=varTagsInfo,
		constrGroupList=constrGroupList
	)



