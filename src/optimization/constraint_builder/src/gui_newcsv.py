import tkinter as tk
import tkinter.ttk as ttk


class ObjreplaceApp:
	def __init__(self, master=None):
		self._build_ui(master)

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
		self.label5 = ttk.Label(self.lblfrm_import)
		self.label5.configure(text="Select a file")
		self.label5.grid(column=1, padx=10, row=2, sticky="ew")
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
		self.frm_naming_prompts.configure(height=200, width=200)
		self.frm_naming_prompts.grid(column=0, padx=10, pady=10, row=1, sticky="w")
		self.frm_naming_prompts.columnconfigure(1, weight=1)
		self.frm_naming_existing = ttk.Frame(self.lblfrm_naming)
		self.lbl_import_exist1_example = ttk.Label(self.frm_naming_existing)
		self.lbl_import_exist1_example.configure(anchor="w", text="167N, 167S, 409")
		self.lbl_import_exist1_example.grid(column=2, padx=10, row=0, sticky="ew")
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
		self.lbl_change_err = tk.Label(self.lblfrm_summary)
		self.lbl_change_err.configure(
			padx=10, pady=10, text="No changes to preview yet"
		)
		self.lbl_change_err.grid(column=0, columnspan=3, row=1, sticky="nsew")
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

	def run(self):
		self.mainwindow.mainloop()

	def onbtn_import_obj(self):
		pass

	def onopt_import_delim(self, option):
		pass

	def onent_naming_row1(self, p_entry_value, v_validate):
		pass

	def onbtn_naming_preview(self):
		pass

	def onbtn_bot_apply(self):
		pass

	def onbtn_bot_cancel(self):
		pass


if __name__ == "__main__":
	root = tk.Tk()
	app = ObjreplaceApp(root)
	app.run()
