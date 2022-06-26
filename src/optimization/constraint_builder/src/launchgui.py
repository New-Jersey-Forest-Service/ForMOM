'''
gui_main.py

This file launches the program
'''

import tkinter as tk
# from screens import *
import screens.mainmenu
from enum import Enum, unique, auto
from typing import List, Dict
import processor.models as models



def main():
	print("Hi")
	# Very important to instantiate the object so it can be passed arround
	projectState = models.ProjectState.createEmptyprojectState()

	root = tk.Tk()
	root.minsize(width=400, height=400)

	screens.mainmenu.buildOpeningScreen(root, projectState)

	root.mainloop()



if __name__ == '__main__':
	main()
else:
	print("[[ ERROR ]] This file is not meant to be imported")
	num = 1 / 0
