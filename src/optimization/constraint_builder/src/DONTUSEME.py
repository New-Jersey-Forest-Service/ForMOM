

def updateExportToCSV(overwrite = False):
	global _constrGroup, _varTagsInfo

	allConstrs = proc.compileStandardConstraintGroup(_varTagsInfo, _constrGroup)

	allVarNamesSorted = copy.deepcopy(_varTagsInfo.all_vars)
	allVarNamesSorted.sort(key=lambda tags: "_".join(tags))
	allVarnamesRaw = ["_".join(x) for x in allVarNamesSorted]

	outputFile = '/home/velcro/Documents/Professional/NJDEP/TechWork/ForMOM/src/optimization/constraint_builder/sample_data/constrs.csv'

	# TODO: Move this into the processing file (or maybe some kind of input output file)
	# TODO: Bro this is so ugly I cannot do deep work if I'm not in silence wow
	# TODO: Maybe use dictionary structure instead of parallel lists ??
	writingMode = 'w' if overwrite else 'a'

	with open(outputFile, mode=writingMode) as constrCsv:
		writer = csv.writer(constrCsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		if overwrite:
			firstRow = ['const_name'] + allVarnamesRaw + ['operator', 'rtSide']
			writer.writerow(firstRow)
		
		_updateWriteConstrs(writer, allVarNamesSorted, allConstrs)


# TODO: Move this to some file i/o module
def _updateWriteConstrs(writer: csv.writer, allVarNamesSorted: List[List[str]], allConstrs: List[models.CompiledConstraint]):
	COMPSIGN_TO_STR = {
		models.ComparisonSign.GE: 'ge',
		models.ComparisonSign.LE: 'le',
		models.ComparisonSign.EQ: 'eq'
	}
	
	rowLen = len(allVarNamesSorted) + 3

	for constr in allConstrs:
		nextRow = [''] * rowLen
		nextRow[0] = constr.name
		nextRow[-1] = constr.compare_value
		nextRow[-2] = COMPSIGN_TO_STR[constr.compare_type]
		
		for ind, var in enumerate(allVarNamesSorted):
			coef = 0
			if var in constr.var_tags:
				varInd = constr.var_tags.index(var)
				coef = constr.var_coeffs[varInd]
			nextRow[ind + 1] = coef
		
		writer.writerow(nextRow)