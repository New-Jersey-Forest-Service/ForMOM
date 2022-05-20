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
objFileStr = ''
constrFileStr = ''
outputDatFileStr = ''

objSel = False
constrSel = False
outputSel = False

lblObj = None
lblConstr = None
lblDat = None
btnProc = None

#global constants
PATH_DISPLAY_LEN = 35
CSV_FILES = [('CSV Files','*.csv'), ('All Files','*.*')]
DAT_FILES = [('DAT Files','*.dat'), ('All Files','*.*')]




# ======================================================
#                 File Selection
# ======================================================

def setObjFile() -> None:
    '''
        Select objective csv with a chooser
    '''
    global objFileStr, lblObj, objSel

    objFileStr = filedialog.askopenfilename(
        filetypes=CSV_FILES,
        defaultextension=CSV_FILES
        )

    print(objFileStr)

    if objFileStr.strip() == "":
        objSel = False
        lblObj.config(text="No file selected")
    else:
        objSel = True
        lblObj.config(text=shrinkPathString(objFileStr))
    
    updateProcessButtonStatus()
    

def setConstrFile() -> None:
    '''
        Select constraint csv with a chooser
    '''
    global constrFileStr, lblConstr, constrSel

    constrFileStr = filedialog.askopenfilename(
        filetypes=CSV_FILES,
        defaultextension=CSV_FILES
        )

    if constrFileStr.strip() == "":
        constrSel = False
        lblConstr.config(text="No file selected")
    else: 
        constrSel = True
        lblConstr.config(text=shrinkPathString(constrFileStr))

    updateProcessButtonStatus()


def setOutFile() -> None:
    '''
        Select output dat with a chooser 
    '''
    global outputDatFileStr, lblDat, constrSel

    outputDatFileStr = filedialog.asksaveasfilename(
        filetypes=DAT_FILES,
        defaultextension=DAT_FILES
        )

    if outputDatFileStr.strip() == "":
        outputSel = False
        lblDat.config(text="No file selected")
    else:
        outputSel = True
        lblDat.config(text=shrinkPathString(outputDatFileStr))

    updateProcessButtonStatus()


def updateProcessButtonStatus() -> None:
    global btnProc

    if objSel and constrSel and outputSel:
        btnProc['state'] = 'normal'
    else:
        btnProc['state'] = 'disabled'


def shrinkPathString(pathstr: str) -> str:
    pathstr = str(pathstr)
    if len(pathstr) <= PATH_DISPLAY_LEN:
        return pathstr
    else:
        return '...' + pathstr[-PATH_DISPLAY_LEN + 3:]






# ======================================================
#             Processing / Actual Conversion
# ======================================================

#file processing; old main function
def processCSVs() -> None:
    return_messages = []
	# Step 1: Get + Read Input
    return_messages.append("Now parsing & converting...")

    # TODO: This
    objData = openAndReadObjectiveCSV(objFilepath)
    constData = openAndReadConstraintCSV(constFilepath)

    # Step 2: Validate the data & produce a FinalModel object
    objData, constData = lintInputData(objData, constData)
    finalModel = convertInputToFinalModel(objData, constData)

    # Step 3: Write the finalModel
    writeParamFile(finalModel, paramFilepath, objFilepath, constFilepath)
    
    return_messages.append(f'All done')
    return_messages.append(f'View output in {paramFilepath}')
    return return_messages

















#new main; instantiate mainWindow
def main():
    global lblObj, lblConstr, lblDat, btnProc

    #create a main window
    root = Tk()
    root.title('NJFS ForMOM - CSV to Dat')
    root.geometry('450x600')
    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)

    #Title + Instruction Label
    frmTitle = Frame(root)

    lblTitle = Label(frmTitle, text="NJFS .csv to .dat Converter", font=("Arial", 20), anchor="center")
    lblInstruction = Label(frmTitle, text="Select Input CSV's and then Process", anchor="center")
    lblTitle.grid(row=0, column=0)
    lblInstruction.grid(row=1, column=0)

    #File Selectors
    frmFileSelectors = Frame(root)
    frmFileSelectors.rowconfigure([0, 1, 2], minsize=50, weight=1)
    frmFileSelectors.columnconfigure([0, 1], weight=1)
    frmFileSelectors.columnconfigure(0, minsize=125)

    btnObjFile = Button(frmFileSelectors,text='Objective CSV',command=setObjFile)
    lblObj     = Label(frmFileSelectors, text="No file selected", width=PATH_DISPLAY_LEN, anchor="w")
    btnObjFile.grid(row=0, column=0, sticky="nse", pady=5)
    lblObj.grid(row=0, column=1, sticky="nsw", padx=5)

    btnConstrFile = Button(frmFileSelectors,text='Constraint CSV',command=setConstrFile)
    lblConstr     = Label(frmFileSelectors, text="No file selected", width=PATH_DISPLAY_LEN, anchor="w")
    btnConstrFile.grid(row=1, column=0, sticky="nse", pady=5)
    lblConstr.grid(row=1, column=1, sticky="nsw", padx=5)

    btnDatFile = Button(frmFileSelectors,text='Output DAT',command=setOutFile)
    lblDat     = Label(frmFileSelectors, text="No file selected", width=PATH_DISPLAY_LEN, anchor="w")
    btnDatFile.grid(row=2, column=0, sticky="nse", pady=5)
    lblDat.grid(row=2, column=1, sticky="nsw", padx=5)

    #Processing
    frmProcess = Frame(root)
    frmProcess.rowconfigure(1, weight=1)
    frmProcess.columnconfigure(0, weight=1)

    btnProc = Button(frmProcess,text='Process',command=processCSVs)
    txtOutput = Text(frmProcess, height=20)

    btnProc.grid(row=0, column=0, pady=5, sticky="ns")
    txtOutput.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    #Gridding the main frames
    frmTitle.grid(row=0, column=0)
    frmFileSelectors.grid(row=1, column=0, padx=10, pady=(10, 0))
    frmProcess.grid(row=2, column=0, sticky="ns")

    updateProcessButtonStatus()

    root.mainloop()
#end main()






if __name__ == '__main__':
	main()
