
## Overall Goal
What needs to happen rn


Main -> Create
    |       |
   \/      \/
Project Overview <\-> Constraint Builder


Other
 - [ ] Get the outputs from all the fvs runs
 - [ ] Consider making it pretty


Feedback:
 - It's not clear at all what to do on the objective import
 - Delimiter doesn't make sense
 - Allow for fullscreening ?
 - Standard Constraint, fix arrow moving to a side
 - It's not clear why to use arrows
 - Continuity constraints are gonna be painful
 - Allow for variables on both sides
 - Look at windows export
 - Look into changing right sides
 - Have more options for fine-tuning with variable selection

BUGS:
 - [x] Eq, Le, Ge signs not being rendered correctly	

So
 - [x] Build Main Screen
 - [x] Figure out file exporting & saving (json conversion of projectState)
   * [ ] Think about still putting everything into a zip
 - [x] Create Transitions
   * [x] Start with Overview -> Constraint Builder
 - [x] CSV File Output
 - [~] Better standard cosntraint
   * [!] ~~Add difference between name of constraint and constraint prefix~~
   * [x] Add option for default coefficient in constraints
   * [~] Lint constraint names (no spaces probably) 
	=> Still doesn't check for duplicates overall
   * [x] Don't allow exiting with invalid constraint state
	=> It does allow exiting when no constraints exist which may be an issue :/

 - [ ] Refactoring 1.0
 	* [ ] Write test suite?
	* [x] Pull styling constants out (width, csv files, etc)
	* [x] GUI files with more standard names & functions
	* [x] Get inequality checks from the inequality class (instead of switch statement with strs EW)
	* [x] File IO File
	* [x] Hella renaming
 - [~] Test
 	* [x] See how courtney uses it
	* [ ] Auto detecting bad save files
	* [ ] Ground truths for string conversions & testing
 - [ ] Better Looks
    * [ ] ttk ?

 - [ ] Future Functions
    * [ ] Export straight to .dat
    * [ ] Export individually to .csvs
    * [ ] Include csv\_to_dat in this program
    * [ ] Automatic running
	* [ ] Better exporting options
	* [ ] To Dat conversion
    * [ ] Handle change of objective file
    * [ ] Renamable tags





## [ ] Renamed Dataclasses

```python
# What's needed to parse an objective file
#  - Objective File
#  - Delimiter
#  - Tag Names



# User Input Process. It must necessarily be in this order
objFile = getObjFile()

exampleVar = readExampleVar(objFile)
delim = getDelim(exampleVar)

exampleTagMembers = readExampleTags(objFile, delim)
tagNames = getTagNames(exampleTagMembers)


# Actual Processing
varInfo = buildVarInfo(objFile, delim, tagNames)

> def buildVarInfo (objFile, delim, tagNames):
> 	varNamesRaw = getVarNames(objFile, delim)
>	varNamesRaw.sort()
>   varNamesSplit = [x.split(delim) for x in varNamesRaw]
>	tagOrder = tagNames
>
>	tagMembers = dict()
```









## [~] Better Folder Structure

- [x] Create better folders:
launchcmd.py
launchgui.py

screens/
 > mainmenu
 > newproject
 > projectoverview
 > standardconstraint

ioutils/
 > fileio
 > cmdinput

processor/
 > dataclasses
 > linting
 > constraintprocessor

- [ ] Actually populate files








## [x] Obj Import Screen
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





## [x] Standard Constraint Builder Screen
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





## [x] Project Overview Screen
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










