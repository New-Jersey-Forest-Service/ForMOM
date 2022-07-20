#!/usr/bin/python3
import time
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import attrs
import pathlib
import os
import tempfile

import csv_to_dat as converter
import model_data_classes as model
import pyomo_runner
import pyomo.environ as pyo
import pyomo.opt as opt

PATH_DISPLAY_LEN = 35
CSV_FILES = [('CSV Files','*.csv'), ('All Files','*.*')]



@attrs.define
class GUIState:
	objFileStr: str = ""
	constFileStr: str = ""

	loadedModel: model.FinalModel = None
	runInstance: pyo.ConcreteModel = None
	runResult: opt.SolverResults = None






class GuibuildingApp:
	def __init__(self, master=None):
		# state variable
		self.state = GUIState()

		# build ui
		self.im_a_top = master if master is not None else tk.Tk()
		self.frm_title = ttk.Frame(self.im_a_top)
		self.lbl_title = ttk.Label(self.frm_title)
		self.lbl_title.configure(text="ForMOM Linear Model Runner")
		self.lbl_title.pack(anchor="center", expand="true", side="top")
		self.lbl_subtitle = ttk.Label(self.frm_title)
		self.lbl_subtitle.configure(text="Solves linear optimization problems.")
		self.lbl_subtitle.pack(side="top")
		self.frm_title.configure(height=200, width=200)
		self.frm_title.grid(
			column=0, columnspan=3, padx=10, pady=20, row=0, sticky="ew"
		)
		self.frm_actualrunning = ttk.Frame(self.im_a_top)
		self.lblfrm_import = ttk.Labelframe(self.frm_actualrunning)
		self.btn_objcsv = ttk.Button(self.lblfrm_import)
		self.btn_objcsv.configure(text="Objective .csv")
		self.btn_objcsv.grid(column=0, ipadx=2, ipady=2, padx=5, row=0, sticky="ew")
		self.btn_objcsv.configure(command=self.onbtn_import_obj)
		self.btn_constcsv = ttk.Button(self.lblfrm_import)
		self.btn_constcsv.configure(text="Constraint .csv")
		self.btn_constcsv.grid(column=0, ipadx=2, ipady=2, padx=5, row=1, sticky="ew")
		self.btn_constcsv.configure(command=self.onbtn_import_const)
		self.btn_loadmodel = ttk.Button(self.lblfrm_import)
		self.btn_loadmodel.configure(text="Load Model")
		self.btn_loadmodel.grid(
			column=0, columnspan=2, ipadx=10, ipady=5, padx=10, pady=10, row=2
		)
		self.btn_loadmodel.configure(command=self.onbtn_import_load)
		self.lbl_constpath = ttk.Label(self.lblfrm_import)
		self.lbl_constpath.configure(anchor="w", text="No File Selected")
		self.lbl_constpath.grid(column=1, row=1, sticky="ew")
		self.lbl_objpath = ttk.Label(self.lblfrm_import)
		self.lbl_objpath.configure(anchor="w", text="No File Selected")
		self.lbl_objpath.grid(column=1, row=0, sticky="ew")
		self.lblfrm_import.configure(height=200, text="Import", width=200)
		self.lblfrm_import.grid(
			column=0, ipady=0, padx=0, pady=10, row=0, sticky="nsew"
		)
		self.lblfrm_import.rowconfigure(0, pad=10)
		self.lblfrm_import.rowconfigure(1, pad=10)
		self.lblfrm_import.columnconfigure(0, pad=5)
		self.lblfrm_import.columnconfigure(1, pad=5, weight=1)
		self.lblfrm_run = ttk.Labelframe(self.frm_actualrunning)
		self.btn_run = ttk.Button(self.lblfrm_run)
		self.btn_run.configure(text="Run Model")
		self.btn_run.grid(
			column=0, columnspan=1, ipadx=10, ipady=5, padx=10, pady=10, row=1
		)
		self.btn_run.configure(command=self.onbtn_run_run)
		self.lbl_run_modelstats = ttk.Label(self.lblfrm_run)
		self.lbl_run_modelstats.configure(text="No Model Loaded")
		self.lbl_run_modelstats.grid(column=0, padx=10, pady=10, row=0, sticky="nsew")
		self.lblfrm_run.configure(height=200, text="Run", width=200)
		self.lblfrm_run.grid(column=0, pady=10, row=1, sticky="nsew")
		self.lblfrm_run.columnconfigure(0, weight=1)
		self.lblfrm_output = ttk.Labelframe(self.frm_actualrunning)
		self.btn_output = ttk.Button(self.lblfrm_output)
		self.btn_output.configure(text="Save Output")
		self.btn_output.grid(
			column=0, columnspan=1, ipadx=10, ipady=5, padx=10, pady=10, row=1
		)
		self.btn_output.configure(command=self.onbtn_output_save)
		self.lblfrm_output.configure(height=200, text="Output", width=200)
		self.lblfrm_output.grid(column=0, pady=10, row=2, sticky="nsew")
		self.lblfrm_output.columnconfigure(0, weight=1)
		self.frm_actualrunning.configure(height=200, width=300)
		self.frm_actualrunning.grid(column=0, padx=0, pady=0, row=1, sticky="nsew")
		self.frm_actualrunning.rowconfigure(1, pad=10)
		self.frm_actualrunning.rowconfigure(2, pad=10)
		self.frm_actualrunning.columnconfigure(0, minsize=300)
		self.lblfrm_status = ttk.Labelframe(self.im_a_top)
		self.txt_status = tk.Text(self.lblfrm_status)
		self.txt_status.configure(undo="true", width=50)
		_text_ = '	 \n\n\n			888\'Y88	\n			888 ,\'Y  e88 88e  888,8,\n			888C8   d888 888b 888 " \n			888 "   Y888 888P 888   \n			888	  "88 88"  888   \n \n		 e   e	   e88 88e	   e   e\n		d8b d8b	 d888 888b	 d8b d8b\n	   e Y8b Y8b   C8888 8888D   e Y8b Y8b\n	  d8b Y8b Y8b   Y888 888P   d8b Y8b Y8b\n	 d888b Y8b Y8b   "88 88"   d888b Y8b Y8b\n\n  \n'
		self.txt_status.insert("0.0", _text_)
		self.txt_status.grid(column=0, padx=10, pady=10, row=0, sticky="nsew")
		self.lblfrm_status.configure(height=200, text="Status", width=200)
		self.lblfrm_status.grid(column=1, padx=20, pady=10, row=1, sticky="nsew")
		self.im_a_top.configure(height=200, padx=10, pady=10, width=200)
		self.im_a_top.columnconfigure(0, weight=1)
		self.im_a_top.columnconfigure(1, pad=10)
		self.im_a_top.columnconfigure(2, weight=1)

		# Main widget
		self.mainwindow = self.im_a_top

		self._init_styling()
		self._redraw_dynamics()

	def run(self):
		self.mainwindow.mainloop()


	def onbtn_import_obj(self):
		'''
			Select objective csv with a chooser
		'''
		objFileStr = filedialog.askopenfilename(
			filetypes=CSV_FILES,
			defaultextension=CSV_FILES
			)

		# TODO: Improve behaviour by checking if previous selection
		# is valid, so that selecting nothing doesn't clear everything
		if isInvalidFile(objFileStr):
			self.lbl_objpath.config(text="No file selected")
			self.state.objFileStr = ""
		else:
			self.lbl_objpath.config(text=shrinkPathString(objFileStr))
			self.state.objFileStr = objFileStr
		
		self._redraw_dynamics()


	def onbtn_import_const(self):
		constrFileStr = filedialog.askopenfilename(
			filetypes=CSV_FILES,
			defaultextension=CSV_FILES
			)

		# TODO: Improve behaviour by checking if previous selection
		# is valid, so that selecting nothing doesn't clear everything
		if isInvalidFile(constrFileStr):
			self.lbl_constpath.config(text="No file selected")
			self.state.constFileStr = ""
		else:
			self.lbl_constpath.config(text=shrinkPathString(constrFileStr))
			self.state.constFileStr = constrFileStr
		
		self._redraw_dynamics()


	def onbtn_import_load(self):
		'''
		This reads the objective and constraint file, linting them
		'''
		print("Loading model")
		objData, constrData, messages = converter.lintInputDataFromFilepaths(
			objFilePath=self.state.objFileStr,
			constrFilePath=self.state.constFileStr
		)

		status_str = ""

		if objData == None:
			# Error
			status_str = "XXXXXX\n[[ Errors Occured - Unable to Convert ]]\n"
			status_str += "\n\n[[ Error ]]\n".join([''] + messages)
			self.state.loadedModel = None

		else:
			# Success
			status_str = "[[ Conversion Success ]]\n"
			if len(messages) >= 1:
				status_str += "\n\n[[ Warning ]]\n".join([''] + messages)
			self.state.loadedModel = converter.convertInputToFinalModel(
				objData=objData, 
				constData=constrData
			)

		self._write_new_status(status_str)
		self._redraw_dynamics()


	def onbtn_run_run(self):
		print("Now do the run")

		datloc = tempfile.NamedTemporaryFile()
		temppath = pathlib.Path(datloc.name).absolute()

		converter.writeOutputDat(
			self.state.loadedModel, 
			temppath,
			self.state.objFileStr,
			self.state.constFileStr
			)
		
		instance = pyomo_runner.loadPyomoModelFromDat(temppath)
		instance, res = pyomo_runner.solveConcreteModel(instance)
		resStr = pyomo_runner.getOutputStr(instance, res)

		self.state.runInstance = instance
		self.state.runResult = res

		datloc.close()

		self._write_new_status(resStr)
		self._redraw_dynamics()


	def onbtn_output_save(self):
		pass

	
	def _write_new_status(self, msg_str: str):
		'''
		Writes to the status box, clearing out whatever was there
		before and timestamping it.
		'''
		self.txt_status.delete("1.0", tk.END)

		# Insert Time Stamp
		cur_time = time.localtime(time.time())
		time_str = "{Year}-{Month}-{Day}-{Hour}-{Min}-{Sec}".format(
			Year=cur_time.tm_year, 
			Month=str(cur_time.tm_mon).zfill(2),  # zfill pads the string with zeros
			Day=str(cur_time.tm_mday).zfill(2),   # i.e. "3" -> "03"
			Hour=str(cur_time.tm_hour).zfill(2),
			Min=str(cur_time.tm_min).zfill(2),
			Sec=str(cur_time.tm_sec).zfill(2)
		)
		self.txt_status.insert(tk.END, time_str + "\n\n")

		# Insert message
		self.txt_status.insert(tk.END, msg_str)


	def _init_styling(self):
		'''
		There's some style work that I don't know how to input into
		pyguru designer so instead it's done here
		'''
		# Buttons that are always green
		btns = [
			self.btn_constcsv,
			self.btn_objcsv
		]

		for b in btns:
			b['state'] = 'normal'
			b['style'] = 'Accent.TButton'
		
		# Text sizes
		self.lbl_title.configure(font=("Arial", 18))

		# Make the status box monospace
		self.txt_status.configure(font='TkFixedFont')




	def _redraw_dynamics(self):
		# Reset all dyanmics
		# buttons
		btns = [
			self.btn_output, 
			self.btn_loadmodel, 
			self.btn_run
		]

		for b in btns:
			b['state'] = 'disabled'
			b['style'] = ''

		# label
		self.lbl_run_modelstats.configure(text="No Model Loaded")


		# Stage 1: Files Selected for import
		if self.state.constFileStr != '' and self.state.objFileStr != '':
			self.btn_loadmodel['state'] = 'normal'
			self.btn_loadmodel['style'] = 'Accent.TButton'
		
		else:
			return


		# Stage 2: Model loaded
		lm = self.state.loadedModel

		if lm != None:
			self.btn_run['state'] = 'normal'
			self.btn_run['style'] = 'Accent.TButton'

			num_vars = len(lm.var_names)
			num_consts = len(lm.eq_vec) + len(lm.ge_vec) + len(lm.le_vec)
			model_str = \
				f"Model Loaded\n" + \
				f"{num_vars} variables, {num_consts} constraints\n" + \
				f"EQ: {len(lm.eq_vec)} | GE: {len(lm.ge_vec)} | LE: {len(lm.le_vec)}"
			self.lbl_run_modelstats.configure(text=model_str)
		
		else:
			return
		

		# Stage 3: Model was run
		res = self.state.runResult

		if res == None:
			return

		term_cond = res.solver.termination_condition

		if term_cond == pyo.TerminationCondition.optimal:
			self.btn_output['state'] = 'normal'
			self.btn_output['style'] = 'Accent.TButton'

		else:
			return











def isInvalidFile(dialogOutput) -> bool:
	# For whatever reason, filedialog.askname() can return multiple different things ???
	return dialogOutput == None or len(dialogOutput) == 0 or dialogOutput.strip() == ""

def shrinkPathString(pathstr: str) -> str:
	pathstr = str(pathstr)
	if len(pathstr) <= PATH_DISPLAY_LEN:
		return pathstr
	else:
		return '...' + pathstr[3 - PATH_DISPLAY_LEN:]



if __name__ == "__main__":
	# Setup root
	root = tk.Tk()
	root.option_add("*tearOff", False)
	root.title("ForMOM - Linear Model Runner")

	# Load theme
	style = ttk.Style(root)

	os.chdir(pathlib.Path(__file__).parent)
	root.tk.call("source", "./theme/forest-light.tcl")
	style.theme_use("forest-light")

	# Build the app and run
	app = GuibuildingApp(root)
	app.run()
