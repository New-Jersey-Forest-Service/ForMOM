'''
gui_main.py

This file launches the program
'''

import tkinter as tk
import constraint_builder_project_overview
import constraint_builder_obj_import
import constraint_builder_opening_screen
from enum import Enum, unique, auto
from typing import List, Dict
from attrs import define, frozen
import varname_dataclasses as models
import constraint_processer as proc



def main():
	# Very important to instantiate the object so it can be passed arround
	projectState = models.ProjectState.createEmptyprojectState()

	root = tk.Tk()
	root.minsize(width=400, height=400)

	constraint_builder_opening_screen.buildOpeningScreen(root, projectState)

	root.mainloop()



if __name__ == '__main__':
	main()
else:
	print("[[ ERROR ]] This file is not meant to be imported")
	num = 1 / 0
