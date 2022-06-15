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





