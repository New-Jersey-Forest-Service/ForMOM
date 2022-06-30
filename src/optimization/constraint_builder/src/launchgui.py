'''
gui_main.py

This file launches the program
'''

import tkinter as tk

import gui_mainmenu
import models


def main():
	print("Hi")
	# Very important to instantiate the object so it can be passed arround
	projectState = models.ProjectState.createEmptyProjectState()

	root = tk.Tk()
	root.minsize(width=400, height=400)

	gui_mainmenu.buildGUI_OpeningScreen(root, projectState)

	root.mainloop()



if __name__ == '__main__':
	main()
else:
	print("[[ ERROR ]] This file is not meant to be imported")
	num = 1 / 0
