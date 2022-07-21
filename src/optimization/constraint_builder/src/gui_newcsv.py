import tkinter as tk
import tkinter.ttk as ttk
from typing import Dict, List
from devtesting import dummyProjectState
import models
from enum import Enum, auto

import proc_constraints as proc
import linting as lint
import proc_render as render
import io_file
from gui_consts import CSV_FILES, WIDTH_BIG, WIDTH_MED, WIDTH_SML

import gui_projectoverview

class ChangeOptions:
	ADDED = auto()
	REMOVED = auto()
	KEPT = auto()

class DifferenceOptions :
	ADDED = auto()
	REMOVED = auto()



class GUINewCSV:

	# State
	_passedProjectState: models.ProjectState = None
	_passedRoot: tk.Tk = None

	# user input
	_objFileStr: str = None
	_groupnameList: List[str] = None
	_delimiter: str = None

	# useful processing
	_errWithObjFile: str = None
	_errWithNamesList: str = None
	_objSampleVar: str = None

	_varNamesRaw: List[str] = None
	_tagLists: List[List[str]] = None

	_oldVarNames: List[List[str]] = None
	_oldTagOrder: List[str] = None
	_oldTagDict: Dict[str, List[str]] = None

	# preview changes
	_changesGroups: Dict[ChangeOptions, List[str]] = {
		ChangeOptions.ADDED: [],
		ChangeOptions.KEPT: [],
		ChangeOptions.REMOVED: []
	}
	_changesTag: Dict[str, Dict[DifferenceOptions, List[str]]] = {}
	_changesVars: Dict[DifferenceOptions, List[str]] = {
		DifferenceOptions.ADDED: [],
		DifferenceOptions.REMOVED: []
	}
	_previewReady: bool = False

	# GUI items
	_nameEntVarList: List[tk.StringVar] = None




	def __init__(self, root:tk.Tk, projectState: models.ProjectState):
		self._passedProjectState = projectState
		self._passedRoot = root
		self._oldTagDict = projectState.varData.tag_members
		self._oldTagOrder = projectState.varData.tag_order
		self._oldVarNames = projectState.varData.all_vars


		print(projectState)

		self._build_ui(root)
		self._init_draw()
		self._init_draw()
		self._update_init()
		self._redraw_dynamics()


	def _build_ui(self, master=None):
		self.frm_replacetop = ttk.Frame(master)
		self.lbl_title = ttk.Label(self.frm_replacetop)
		self.lbl_title.configure(anchor="center", text="Load New Objective File")
		self.lbl_title.grid(
			column=0, columnspan=2, padx=10, pady=10, row=0, sticky="ew"
		)
		self.lblfrm_import = ttk.Labelframe(self.frm_replacetop)
		self.btn_import_file = ttk.Button(self.lblfrm_import)
		self.btn_import_file.configure(text="Objective .csv")
		self.btn_import_file.grid(column=0, row=0, sticky="e")
		self.btn_import_file.configure(command=self.onbtn_import_obj)
		self.lbl_delim = ttk.Label(self.lblfrm_import)
		self.lbl_delim.configure(anchor="e", text="Seperator:")
		self.lbl_delim.grid(column=0, row=1, sticky="ew")
		self.lbl_import_samplevardesc = ttk.Label(self.lblfrm_import)
		self.lbl_import_samplevardesc.configure(anchor="e", text="Sample Variable:")
		self.lbl_import_samplevardesc.grid(column=0, row=2, sticky="ew")
		self.lbl_import_samplevar = ttk.Label(self.lblfrm_import)
		self.lbl_import_samplevar.configure(text="Select a file")
		self.lbl_import_samplevar.grid(column=1, padx=10, row=2, sticky="ew")
		__values = ["_", "-", "="]
		__tkvar = tk.StringVar()
		self.opt_import_delim = tk.OptionMenu(
			self.lblfrm_import, __tkvar, *__values, command=self.onopt_import_delim
		)
		self.opt_import_delim.grid(column=1, padx=10, row=1, sticky="w")
		self.lbl_import_path = ttk.Label(self.lblfrm_import)
		self.lbl_import_path.configure(anchor="w", text="Select a file")
		self.lbl_import_path.grid(column=1, padx=10, row=0, sticky="ew")
		self.lblfrm_import.configure(height=200, text="File Importing", width=200)
		self.lblfrm_import.grid(column=0, padx=10, row=1, sticky="nsew")
		self.lblfrm_import.grid_anchor("center")
		self.lblfrm_import.rowconfigure(0, pad=10)
		self.lblfrm_import.rowconfigure(1, pad=10)
		self.lblfrm_import.rowconfigure(2, pad=20)
		self.lblfrm_import.columnconfigure(0, pad=10)
		self.lblfrm_import.columnconfigure(1, weight=1)
		self.lblfrm_naming = ttk.Labelframe(self.frm_replacetop)
		self.separator1 = ttk.Separator(self.lblfrm_naming)
		self.separator1.configure(orient="vertical")
		self.separator1.grid(column=1, padx=10, pady=10, row=0, rowspan=2, sticky="ns")
		self.frm_naming_prompts = ttk.Frame(self.lblfrm_naming)
		self.ent_import_tagname1 = ttk.Entry(self.frm_naming_prompts)
		self.ent_import_tagname1.configure(validate="key", width=15)
		self.ent_import_tagname1.grid(column=0, row=0, sticky="ew")
		_validatecmd = (
			self.ent_import_tagname1.register(self.onent_naming_row1),
			"%p_entry_value",
			"%v_validate",
		)
		self.ent_import_tagname1.configure(validatecommand=_validatecmd)
		self.lbl_import_exname1 = ttk.Label(self.frm_naming_prompts)
		self.lbl_import_exname1.configure(padding=5, text="167N, 167S, 999")
		self.lbl_import_exname1.grid(column=1, row=0, sticky="ew")
		self.frm_naming_prompts.configure(width=200)
		self.frm_naming_prompts.grid(column=0, padx=10, pady=10, row=1, sticky="w")
		self.frm_naming_prompts.columnconfigure(1, weight=1)
		self.frm_naming_existing = ttk.Frame(self.lblfrm_naming)
		self.lbl_import_exist1_example = ttk.Label(self.frm_naming_existing)
		self.lbl_import_exist1_example.configure(anchor="w", text="167N, 167S, 409")
		self.lbl_import_exist1_example.grid(column=1, padx=10, row=0, sticky="ew")
		self.lbl_import_exist1_name = ttk.Label(self.frm_naming_existing)
		self.lbl_import_exist1_name.configure(
			anchor="center", relief="ridge", text="for_type"
		)
		self.lbl_import_exist1_name.grid(column=0, ipadx=5, ipady=5, row=0, sticky="e")
		self.frm_naming_existing.configure(height=200, width=200)
		self.frm_naming_existing.grid(column=2, row=1, sticky="w")
		self.frm_naming_existing.grid_anchor("center")
		self.frm_naming_existing.columnconfigure(1, weight=1)
		self.label7 = ttk.Label(self.lblfrm_naming)
		self.label7.configure(anchor="w", text="Existing Tags")
		self.label7.grid(column=2, row=0, sticky="ew")
		self.lbl_naming = ttk.Label(self.lblfrm_naming)
		self.lbl_naming.configure(anchor="w", text="Imported Tag Groups")
		self.lbl_naming.grid(column=0, padx=10, row=0, sticky="ew")
		self.msg_import_err = tk.Message(self.lblfrm_naming)
		self.msg_import_err.configure(
			justify="left",
			text="[[ Error ]]\nSometimes it really be like that :/",
			width=400,
		)
		self.msg_import_err.grid(column=0, columnspan=3, pady=10, row=2)
		self.btn_import_preview = ttk.Button(self.lblfrm_naming)
		self.btn_import_preview.configure(text="Preview Changes")
		self.btn_import_preview.grid(
			column=0, columnspan=3, ipadx=5, ipady=5, pady=10, row=3
		)
		self.btn_import_preview.configure(command=self.onbtn_naming_preview)
		self.lblfrm_naming.configure(height=200, text="Variable Tags", width=200)
		self.lblfrm_naming.grid(column=1, padx=10, pady=0, row=1, sticky="nsew")
		self.lblfrm_naming.rowconfigure(1, weight=1)
		self.lblfrm_naming.columnconfigure(0, weight=1)
		self.lblfrm_naming.columnconfigure(2, weight=1)
		self.lblfrm_summary = ttk.Labelframe(self.frm_replacetop)
		self.lblfrm_change_group = ttk.Labelframe(self.lblfrm_summary)
		self.lbl_changes_group = ttk.Label(self.lblfrm_change_group)
		self.lbl_changes_group.configure(
			anchor="nw", text="New: dev\n\nRemoved: year\n\nChanged: mng, for_type"
		)
		self.lbl_changes_group.grid(column=0, row=0, sticky="nsew")
		self.lblfrm_change_group.configure(height=200, text="Groups", width=200)
		self.lblfrm_change_group.grid(column=0, padx=10, pady=10, row=0, sticky="nsew")
		self.lblfrm_change_group.rowconfigure(0, weight=1)
		self.lblfrm_change_group.columnconfigure(0, minsize=150, pad=10, weight=1)
		self.lblfrm_change_tags = ttk.Labelframe(self.lblfrm_summary)
		self.nb_change_tags = ttk.Notebook(self.lblfrm_change_tags)



		self.frame1 = ttk.Frame(self.nb_change_tags)

		self.label14 = ttk.Label(self.frame1)
		self.label14.configure(anchor="center", text="Added")
		self.label14.grid(column=0, row=0, sticky="ew")

		self.label15 = ttk.Label(self.frame1)
		self.label15.configure(anchor="center", text="Removed")
		self.label15.grid(column=1, row=0, sticky="ew")

		self.listbox1 = tk.Listbox(self.frame1)
		self.listbox1.grid(column=0, row=1)

		self.listbox2 = tk.Listbox(self.frame1)
		self.listbox2.grid(column=1, row=1)

		self.frame1.configure(height=200, padding=10, width=200)
		self.frame1.grid(column=0, row=0, sticky="nsew")
		self.frame1.rowconfigure(1, weight=1)
		self.frame1.columnconfigure(0, weight=1)
		self.frame1.columnconfigure(1, weight=1)

		self.nb_change_tags.add(self.frame1, text="Mng")
		self.nb_change_tags.configure(height=200, width=200)
		self.nb_change_tags.grid(column=0, row=0, sticky="nsew")


		self.lblfrm_change_tags.configure(height=200, text="Changed Tags", width=200)
		self.lblfrm_change_tags.grid(column=1, padx=10, pady=10, row=0, sticky="nsew")
		self.lblfrm_change_vars = ttk.Labelframe(self.lblfrm_summary)
		self.label16 = ttk.Label(self.lblfrm_change_vars)
		self.label16.configure(anchor="center", text="Added")
		self.label16.grid(column=0, row=0, sticky="ew")
		self.label17 = ttk.Label(self.lblfrm_change_vars)
		self.label17.configure(anchor="center", text="Removed")
		self.label17.grid(column=1, row=0, sticky="ew")
		self.lsb_change_vars_added = tk.Listbox(self.lblfrm_change_vars)
		self.lsb_change_vars_added.grid(
			column=0, padx=10, pady=10, row=1, sticky="nsew"
		)
		self.lsb_change_removed = tk.Listbox(self.lblfrm_change_vars)
		self.lsb_change_removed.grid(column=1, padx=10, pady=10, row=1, sticky="nsew")
		self.lblfrm_change_vars.configure(height=200, text="Variables", width=200)
		self.lblfrm_change_vars.grid(
			column=2,
			columnspan=2,
			ipadx=10,
			ipady=10,
			padx=10,
			pady=10,
			row=0,
			sticky="nsew",
		)
		self.lblfrm_change_vars.rowconfigure(1, weight=1)
		self.lblfrm_change_vars.columnconfigure(0, weight=1)
		self.lblfrm_change_vars.columnconfigure(1, weight=1)
		self.lblfrm_summary.configure(height=200, text="Changes Summary", width=200)
		self.lblfrm_summary.grid(
			column=0, columnspan=2, padx=10, pady=10, row=3, sticky="nsew"
		)
		self.lblfrm_summary.rowconfigure(0, weight=1)
		self.lblfrm_summary.rowconfigure(1, weight=1)
		self.lblfrm_summary.columnconfigure(1, weight=1)
		self.lblfrm_summary.columnconfigure(2, weight=1)
		self.frm_botbuttons = ttk.Frame(self.frm_replacetop)
		self.btn_bot_apply = ttk.Button(self.frm_botbuttons)
		self.btn_bot_apply.configure(default="normal", text="Apply Changes")
		self.btn_bot_apply.grid(column=1, ipadx=5, ipady=5, padx=10, row=0, sticky="e")
		self.btn_bot_apply.configure(command=self.onbtn_bot_apply)
		self.btn_bot_cancel = ttk.Button(self.frm_botbuttons)
		self.btn_bot_cancel.configure(text="Cancel")
		self.btn_bot_cancel.grid(column=0, ipadx=5, ipady=5, row=0, sticky="e")
		self.btn_bot_cancel.configure(command=self.onbtn_bot_cancel)
		self.frm_botbuttons.configure(height=200, width=200)
		self.frm_botbuttons.grid(column=0, columnspan=2, row=4, sticky="e")
		self.frm_botbuttons.columnconfigure(0, pad=20)
		self.frm_replacetop.configure(height=200, width=200)
		self.frm_replacetop.grid(column=0, row=0)
		self.frm_replacetop.rowconfigure(4, pad=20)
		self.frm_replacetop.columnconfigure(0, minsize=400, pad=20, weight=1)

		# Main widget
		self.mainwindow = self.frm_replacetop
	


	# Callbacks
	def onbtn_import_obj(self):
		newpath = io_file.getOpenFilepath(CSV_FILES)
		if newpath != None:
			self._objFileStr = newpath
		
		self._update_processfile()
		self._redraw_dynamics()

	def onopt_import_delim(self, option):
		self._delimiter = option
		self._update_processfile()
		self._redraw_dynamics()

	# Needed only during init, nothing binds to it (callback should be removed in pygubu)
	def onent_naming_row1(self, p_entry_value, v_validate):
		pass

	def onent_naming_name(self):
		self._update_groupnaming()
		self._redraw_dynamics()

	def onbtn_naming_preview(self):
		self._update_previewchanges()
		self._redraw_dynamics()

	def onbtn_bot_apply(self):
		print("Applying changes")
		newVarsData: models.VarsData = proc.buildVarDataObject(
			self._varNamesRaw,
			self._delimiter,
			self._groupnameList
		)
		self._passedProjectState = proc.change_varsdata(newVarsData, self._passedProjectState)
		self._transition_to_overview()

	def onbtn_bot_cancel(self):
		print("Cancelling and going back")
		self._transition_to_overview()


	# Transition calls
	def _transition_to_overview(self):
		print("Transitioning to overview")
		for child in self._passedRoot.winfo_children():
			child.destroy()
		
		gui_projectoverview.buildGUI_ProjectOverview(self._passedRoot, self._passedProjectState)


	# Update calls
	def _update_init(self):
		self._update_processfile()
		self._update_groupnaming()


	def _update_previewchanges(self):
		# Group changes
		old_groupnames = set(self._oldTagOrder)
		new_groupnames = set(self._groupnameList)

		self._changesGroups[ChangeOptions.ADDED] = list(new_groupnames - old_groupnames)
		self._changesGroups[ChangeOptions.KEPT] = list(new_groupnames.intersection(old_groupnames))
		self._changesGroups[ChangeOptions.REMOVED] = list(old_groupnames - new_groupnames)

		# Tag member changes
		self._changesTag = {}
		for ind, taggroupname in enumerate(self._groupnameList):
			if not taggroupname in self._changesGroups[ChangeOptions.KEPT]:
				continue

			old_mems = set(self._oldTagDict[taggroupname])
			new_mems = set(self._tagLists[ind])

			self._changesTag[taggroupname] = {
				DifferenceOptions.ADDED: list(new_mems - old_mems),
				DifferenceOptions.REMOVED: list(old_mems - new_mems)
			}

		# Variable changes
		old_varnames_raw = set([
			self._delimiter.join(x) for x in self._oldVarNames
		])
		new_names_set = set(self._varNamesRaw)

		self._changesVars[DifferenceOptions.ADDED] = list(new_names_set - old_varnames_raw)
		self._changesVars[DifferenceOptions.REMOVED] = list(old_varnames_raw - new_names_set)

		# And, update state
		self._previewReady = True


	def _update_processfile(self):
		self._varNamesRaw = None
		self._errWithObjFile = None
		self._tagLists = None

		if  self._objFileStr == None:
			self._errWithObjFile = "No file selected"
			return
		# TODO: What if its a bad file ???
		self._varNamesRaw = io_file.readVarnamesRaw(self._objFileStr)
		self._objSampleVar = self._varNamesRaw[0]

		if self._delimiter == None:
			self._errWithObjFile = "No delimiter selected"
			return
		self._errWithObjFile = lint.lintAllVarNamesRaw(self._varNamesRaw, self._delimiter)

		if self._errWithObjFile:
			return
		self._tagLists = proc.makeTagGroupMembersList(self._varNamesRaw, self._delimiter)

		self._redraw_rebuild_naming_frame()


	def _update_groupnaming(self):
		if self._nameEntVarList == None:
			self._nameEntVarList = []

		self._groupnameList = [x.get() for x in self._nameEntVarList]
		self._errWithNamesList = lint.lintAllTagGroupNames(self._groupnameList)



	# Redraw calls
	def _init_draw(self):
		# Styling options that pygubu doesn't support :/
		self.lbl_title.configure(font=("Arial", 16))

		# The existing vars in the naming section can be drawn
		# at init and do not change

		# First, reset them
		for c in self.frm_naming_existing.winfo_children():
			c.destroy()
		
		# Then populate
		for ind, tag in enumerate(self._oldTagDict.keys()):
			members_str = render.trimEllipsisRight(", ".join(self._oldTagDict[tag]), WIDTH_MED)

			lbl_members = ttk.Label(self.frm_naming_existing)
			lbl_members.configure(anchor="w", text=members_str)
			lbl_members.grid(column=1, padx=10, row=ind, sticky="ew")

			lbl_groupname = ttk.Label(self.frm_naming_existing)
			lbl_groupname.configure(
				anchor="center", relief="ridge", borderwidth=2, text=tag
			)
			lbl_groupname.grid(column=0, ipadx=5, ipady=5, pady=2, row=ind, sticky="e")
		

		# and we call some existing functions
		self._redraw_rebuild_naming_frame()


	def _redraw_dynamics(self):
		# First reset everything

		# - disable buttons
		btns = [
			self.btn_bot_apply,
			self.btn_import_preview
		]
		for b in btns:
			b['state'] = 'disabled'
			b['style'] = ''

		# - resetting naming section
		self.msg_import_err.grid_forget()

		# - resetting summary section
		self.lbl_changes_group.configure(text="No changes to preview yet")
		for c in self.nb_change_tags.winfo_children():
			c.destroy()


		# Now draw things

		# Stage 1 - Importing the file
		if self._objFileStr != None:
			shortstr = render.trimEllipsisLeft(self._objFileStr, WIDTH_BIG)
			self.lbl_import_path.configure(text=shortstr)
		
		if self._objSampleVar != None:
			self.lbl_import_samplevar.configure(text=self._objSampleVar)

		# TODO: This should be in a label in the importing frame
		if self._errWithObjFile != None:
			self.msg_import_err.configure(text=self._errWithObjFile)
			self.msg_import_err.grid(column=0, columnspan=3, pady=10, row=2)
			return
		
		if self._objFileStr == None or self._objSampleVar == None:
			return

		# Stage 2 - Naming Items
		print(f"Error: {self._errWithNamesList}")
		if self._errWithNamesList != None:
			self.msg_import_err.configure(text=self._errWithNamesList)
			self.msg_import_err.grid(column=0, columnspan=3, pady=10, row=2)
			return
		
		self.btn_import_preview['state'] = 'normal'
		self.btn_import_preview['style'] = ''

		# Stage 3 - Changes
		print("Time to change")
		if self._previewReady == False:
			return
		
		# Group Changes
		groupchange_str = \
			f"New:\n" + ", ".join(self._changesGroups[ChangeOptions.ADDED]) + "\n\n" + \
			f"Removed:\n" + ", ".join(self._changesGroups[ChangeOptions.REMOVED]) + "\n\n" + \
			f"Same:\n" + ", ".join(self._changesGroups[ChangeOptions.KEPT])
		self.lbl_changes_group.configure(text=groupchange_str)

		# Tag Member Changes
		changedgroups = self._changesTag.keys()
		print(changedgroups)
		for group in changedgroups:
			addedvar = tk.StringVar()
			addedvar.set(value=self._changesTag[group][DifferenceOptions.ADDED])
			removedvar = tk.StringVar()
			removedvar.set(value=self._changesTag[group][DifferenceOptions.REMOVED])

			nb_tab = ttk.Frame(self.nb_change_tags, padding=10, width=200)
			nb_tab.grid(column=0, row=0, sticky="nsew")
			nb_tab.rowconfigure(1, weight=1)
			nb_tab.columnconfigure([0, 1], weight=1)

			add_lbl = ttk.Label(nb_tab, anchor="center", text="Added")
			add_lbl.grid(column=0, row=0, sticky="ew")
			rm_lbl = ttk.Label(nb_tab, anchor="center", text="Removed")
			rm_lbl.grid(column=1, row=0, sticky="ew")

			add_lsb = tk.Listbox(nb_tab, listvariable=addedvar)
			add_lsb['selectmode'] = 'extended'
			add_lsb.grid(column=0, row=1)
			rm_lsb = tk.Listbox(nb_tab, listvariable=removedvar)
			rm_lsb['selectmode'] = 'extended'
			rm_lsb.grid(column=1, row=1)

			self.nb_change_tags.add(nb_tab, text=group)
		
		# Variable Changes
		var_addvar = tk.StringVar(value=self._changesVars[DifferenceOptions.ADDED])
		var_remvar = tk.StringVar(value=self._changesVars[DifferenceOptions.REMOVED])

		self.lsb_change_vars_added.configure(listvariable=var_addvar)
		self.lsb_change_removed.configure(listvariable=var_remvar)

		self.btn_bot_apply['state'] = 'normal'
		self.btn_bot_apply['style'] = ''


	def _redraw_rebuild_naming_frame(self):
		# destroy the naming frame
		for c in self.frm_naming_prompts.winfo_children():
			c.destroy()
		self.msg_import_err.grid_forget()
		self.lbl_import_samplevar.configure(text="Select a File")
		self.lbl_import_path.configure(text="Select a File")

		if self._objFileStr == None or self._objSampleVar == None:
			return

		# populate the naming frame
		if len(self._nameEntVarList) > len(self._tagLists):
			self._nameEntVarList = self._nameEntVarList[:len(self._tagLists)]
		self._nameEntVarList = self._nameEntVarList + \
			[None] * (len(self._tagLists) - len(self._nameEntVarList))

		for ind, taglist in enumerate(self._tagLists):
			strvar_groupname = self._nameEntVarList[ind]
			if strvar_groupname == None:
				strvar_groupname = tk.StringVar()
				strvar_groupname.trace("w", lambda name, index, mode,
					sv=strvar_groupname: self.onent_naming_name())
				self._nameEntVarList[ind] = strvar_groupname

			ent_memname = tk.Entry(self.frm_naming_prompts, width=WIDTH_MED, textvariable=strvar_groupname)
			ent_memname.grid(row=ind, column=0, sticky="ew")

			mems_str = render.trimEllipsisRight(", ".join(taglist), WIDTH_MED)
			lbl_examplmems = ttk.Label(self.frm_naming_prompts, text=mems_str, anchor="w")
			lbl_examplmems.grid(row=ind, column=1, padx=10, sticky="ew")


		



if __name__ == "__main__":
	projState = dummyProjectState()

	root = tk.Tk()
	app = GUINewCSV(root, projState)
	root.mainloop()
