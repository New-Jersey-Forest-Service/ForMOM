
## Overall Goal
What needs to happen rn


Main -> Create
    |       |
   \/      \/
Project Overview <\-> Constraint Builder


So
 - [ ] Build Main Screen
 - [ ] Figure out file exporting & saving (look at pickle)
 - [ ] Create Transitions
   * [ ] Start with Overview -> Constraint Builder




## Obj Import Screen
The idea:
 - Select an objective file
	 - Lint that it's actually a file
	 - Select a delimiter
 - Name the species
	 - Verify group names
	 - Continue button

State (no tkinter variables):
 - objective file (input)
 - delimiter (input) # TODO: Scan for this in the varname
 - Groupname list

Updates (bindings):
 - CSV Button => CSV Label, SampleVar + Update groupname list
 - Delimiter => Update groupname list
 - Verify group names => Continue button

Funcs to make:
 - [x] Redraw filepathlabel
 - [x] Redraw samplevarlabel
 - [x] Redraw groupname input list
 - [x] Redraw continue button

 - [x] File import all variables
	 - [x] File import one variables
 - [ ] File lint (column structure + name + is a file)

Exposed components:
 - [x] Labels: Filepath, Samplevar
 - [x] Groupnames frame (to redraw)
 - [x] Groupnames: List of StringVars





## Standard Constraint Builder Screen
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





## Project Overview Screen
The idea:

State:
 - constrGroupList (given from prev screens)


Updates (bindings):
 - Delete => UpdateDeleteConstr
 - Edit => UpdateEdit
 - New Constraint Group => UpdateNew + UpdateEdit
 - Save Project => 


Exposed GUI:
 - constr group list frame
 - 










