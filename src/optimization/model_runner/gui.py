#!/usr/bin/python3
from enum import Enum
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import attrs
from enum import Enum, auto


PATH_DISPLAY_LEN = 35
CSV_FILES = [('CSV Files','*.csv'), ('All Files','*.*')]


class GUIPhase(Enum):
	IMPORT = auto()
	RUN = auto()
	OUTPUT = auto()


@attrs.define
class GUIState:
	phase: GUIPhase = GUIPhase.IMPORT

	objFileStr: str = ""
	constFileStr: str = ""
	loadErr: str = ""
	runErr: str = ""


class GuibuildingApp:
	def __init__(self, master=None):
		# state variable
		self.state = GUIState()

		# build ui
		self.im_a_top = tk.Tk() if master is None else master
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
		self.btn_objcsv.configure(text="Objective .csv", style="Accent.TButton")
		self.btn_objcsv.grid(column=0, ipadx=2, ipady=2, padx=5, row=0, sticky="ew")
		self.btn_objcsv.configure(command=self.onbtn_import_obj)
		self.btn_constcsv = ttk.Button(self.lblfrm_import)
		self.btn_constcsv.configure(text="Constraint .csv", style="Accent.TButton")
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
		self.lblfrm_run.configure(height=200, text="Run", width=200)
		self.lblfrm_run.grid(column=0, pady=10, row=1, sticky="nsew")
		self.lblfrm_run.columnconfigure(0, weight=1)
		self.lblfrm_output = ttk.Labelframe(self.frm_actualrunning)
		self.button6 = ttk.Button(self.lblfrm_output)
		self.button6.configure(text="Save Output")
		self.button6.grid(
			column=0, columnspan=1, ipadx=10, ipady=5, padx=10, pady=10, row=1
		)
		self.button6.configure(command=self.onbtn_output_save)
		self.lblfrm_output.configure(height=200, text="Output", width=200)
		self.lblfrm_output.grid(column=0, pady=10, row=2, sticky="nsew")
		self.lblfrm_output.columnconfigure(0, weight=1)
		self.frm_actualrunning.configure(height=200, width=300)
		self.frm_actualrunning.grid(column=0, padx=0, pady=10, row=1, sticky="nsew")
		self.frm_actualrunning.rowconfigure(1, pad=10)
		self.frm_actualrunning.rowconfigure(2, pad=10)
		self.frm_actualrunning.columnconfigure(0, minsize=300)
		self.separator = ttk.Separator(self.im_a_top)
		self.separator.configure(orient="vertical")
		self.separator.grid(column=1, padx=10, pady=5, row=1, sticky="ns")
		self.frm_status = ttk.Frame(self.im_a_top)
		self.label1 = ttk.Label(self.frm_status)
		self.label1.configure(anchor="w", justify="left", text="Status")
		self.label1.grid(column=0, row=0, sticky="w")
		self.txt_statusbox = tk.Text(self.frm_status)
		self.txt_statusbox.configure(width=50, wrap="word")
		_text_ = "adsafds\nf asdfkasdjfkl jsadklfj sdklajfkl sdjalf jkl\nsadfjklsad \njksad f\nkj jskdfjlsadjfkl sjadklfj klsaj klf\nObjective .csv"
		self.txt_statusbox.insert("0.0", _text_)
		self.txt_statusbox.grid(column=0, row=1, sticky="nsew")
		self.frm_status.configure(height=200, width=200)
		self.frm_status.grid(column=2, row=1, sticky="nsew")
		self.frm_status.rowconfigure(0, pad=10)
		self.frm_status.columnconfigure(0, pad=10)
		self.im_a_top.configure(height=200, padx=10, pady=10, width=200)
		self.im_a_top.columnconfigure(0, weight=1)
		self.im_a_top.columnconfigure(1, pad=10)
		self.im_a_top.columnconfigure(2, weight=1)

		# Main widget
		self.mainwindow = self.im_a_top

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
		
		self.update_and_redraw()

	def onbtn_import_const(self):
		pass

	def onbtn_import_load(self):
		pass

	def onbtn_run_run(self):
		pass

	def onbtn_output_save(self):
		pass

	
	def update_and_redraw(self):
		pass



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
	root.tk.call("source", "./theme/forest-light.tcl")
	style.theme_use("forest-light")

	# Build the app and run
	app = GuibuildingApp(root)
	app.run()
