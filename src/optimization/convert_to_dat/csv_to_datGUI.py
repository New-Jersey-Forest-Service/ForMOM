'''
.csv to .dat converter

This script will convert two csvs, one for the
objective function and one for the constraints,
and then spit out a single .dat file.

Michael Gorbunov
William Zipse
NJDEP
'''

import os
import sys
import csv
from typing import Union
from pathlib import Path
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

from model_data_classes import *

#constants for file names
#***Change filenames/paths here (for now)
'''
OBJFILE = 'testObjNoSBP.csv'
CONSTRFILE = 'testConstraintsPL2.csv'
OUTPUTDAT = 'testMini99.dat'
'''
#global variables
objFile = ''
constrFile = ''
outputDat = ''
allSel = False
objSel = False
constrSel = False
outputSel = False
objLabel = ''
constrLabel = ''
outputLabel = ''


# ======================================================
#                 (0) Main Calls
# ======================================================

#--------------------------------------------------------
#GUI setup
#--------------------------------------------------------
#select objective CSV with a chooser
def setObjFile():
    global objFile
    global outputSel
    global objSel
    global constrSel
    global allSel
    global objLabel
    files = [('CSV Files','*.csv'),
                ('All Files','*.*')]
    objFile = filedialog.askopenfile(
    filetypes = files,defaultextension=files)
    objLabel.config(text='Objective CSV: '+str(objFile))
    objSel = True
    if outputSel and constrSel:
        allSel = True
    if allSel:
        procBtn['state']='normal'

#select constraint CSV with a chooser
def setConstrFile():
    global constrFile
    global outputSel
    global objSel
    global constrSel
    global allSel
    global constrLabel
    files = [('CSV Files','*.csv'),
                ('All Files','*.*')]
    constrFile = filedialog.askopenfile(
        filetypes = files,defaultextension=files)
    constrLabel.config(text='Objective CSV: '+str(constrFile))
    constrSel = True
    if outputSel and objSel:
        allSel = True
    if allSel:
        procBtn['state']='normal'

#select output dat with a chooser
def setOutFile():
    global outputDat
    global outputSel
    global objSel
    global constrSel
    global allSel
    global outputLabel
    files = [('DAT Files','*.dat'),
                ('All Files','*.*')]
    outputDat = filedialog.asksaveasfilename(
        filetypes = files,defaultextension=files)
    outputLabel.config(text='Output DAT1: '+str(outputDat))
    outputSel = True
    if objSel and constrSel:
        allSel = True
    if allSel:
        procBtn['state']='normal'

#new main; instantiate mainWindow
def main():
    global objLabel
    global constrLabel
    global datLabel
    global outputLabel
    global procBtn
    #create a main window
    root = Tk()
    root.title('NJ Forest Service ForMOM')
    root.geometry('400x300')

    #create a title label
    titleLabel = Label(root, text="Select Input CSV's & Output dat")

    #create labels for selection statuses
    objLabel = Label(root, text="Obj CSV: ")
    constrLabel = Label(root, text="Constraint CSV: ")
    outputLabel = Label(root, text="Output DAT: ")
    procLabel = Label(root, text = '')
    #define buttons
    objFileBtn = Button(root,text='Objective CSV',command=setObjFile)
    constrFileBtn = Button(root,text='Constraint CSV',command=setConstrFile)
    outputFileBtn = Button(root,text='Output DAT',command=setOutFile)
    procBtn = Button(root,text='Process',command=proc)
    #disable process button
    procBtn['state']='disabled'
    if allSel:
        procBtn['state']='normal'

    #display buttons and labels
    titleLabel.pack()
    objFileBtn.pack(padx=10,pady=10)
    objLabel.pack()
    constrFileBtn.pack(padx=10,pady=10)
    constrLabel.pack()
    outputFileBtn.pack(padx=10,pady=10)
    outputLabel.pack()
    procBtn.pack(padx=10,pady=10)
    procLabel.pack()

    root.mainloop()
#end main()

#file processing; old main function
def proc():
	# Step 1: Get + Read Input
	objFilepath, constFilepath, paramFilepath = getFilepathsFromInput()
	print()
	print("Now parsing & converting...")

	objData = openAndReadObjectiveCSV(objFilepath)
	constData = openAndReadConstraintCSV(constFilepath)

	# Step 2: Validate the data & produce a FinalModel object
	objData, constData = lintInputData(objData, constData)
	finalModel = convertInputToFinalModel(objData, constData)

	# Step 3: Write the finalModel
	writeParamFile(finalModel, paramFilepath, objFilepath, constFilepath)

	print()
	print(f'All done')
	print(f'View output in {paramFilepath}')


def getFilepathsFromInput () -> Union[str, str, str]:
	# First get the filepaths
	# Try it with choosers

	# print("Let's choose some CSV's for making a Pyomo .dat file!")
	# input("Press any key to choose decision variable CSV.")
	# Tk().withdraw() #hide tk window since this is not a full GUI program
	# objFilepath   = askopenfilename()
	# input("Press any key to choose a constraint CSV.")
	# constFilepath = askopenfilename()
	# print("Next choose a Pyomo .dat file.")
	# print("Note: You will have to right click in the file window")
	# print("to create a new file and then select the file.")
	# input("Press any key to choose a Pyomo .dat filename")
	# paramFilepath = askopenfilename()

	# objFilepath   = getCSVFilepath("Objective File:   ")
	# constFilepath = getCSVFilepath("Constraints File: ")
	# paramFilepath = makeDATFilepath("Output .dat File: ")
	objFilepath = OBJFILE
	constFilepath = CONSTRFILE
	paramFilepath = OUTPUTDAT

	return objFilepath, constFilepath, paramFilepath

















if __name__ == '__main__':
	main()
