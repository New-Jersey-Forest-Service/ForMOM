The idea:

State:
 - VarTagsInfo (given)
 - StandardConstraint (built via input)

Updates (bindings):
 - Name, Operator, Value => UpdateConstraint + Update Preview
 - Buttons for listboxes => UpdateConstraint + Redraw LSBs + Update Preview
 - SplitBy => UpdateConstraint + Update Preview

Funcs to make:
 - [x] Redraw Preview
 - [x] Redraw LSBs
 - Updating constraint from LSBs:
   - [x] Update inc / exc groups in constraint
   - TODO [ ] Have select all button

Exposed Components:
 - [x] ConstrName, OpType, DefaultValue
 - [x] Include & Exclude StingVars per tag group
 - [x] Checkbox per Tag Group
 - [x] Text Entry for sample constraint

include lsbs:
{
	'species': tk.LSB,
	'year': tk.LSB,
	'management': tk.LSB
}

exclude lsbs:
{
	'species': tk.LSB,
	'year': tk.LSB,
	'management': tk.LSB
}

