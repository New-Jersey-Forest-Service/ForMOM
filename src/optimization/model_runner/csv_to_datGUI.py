'''
.csv to .dat converter

This script will convert two csvs, one for the
objective function and one for the constraints,
and then spit out a single .dat file.

Michael Gorbunov
William Zipse
NJDEP
'''

from tkinter import filedialog
import tkinter as tk
from tkinter import ttk

from model_data_classes import *
import csv_to_dat as converter

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
datSel = False

lblObj = None
lblConstr = None
lblDat = None
btnProc = None
txtOutput = None

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

    if isInvalidFile(objFileStr):
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

    if isInvalidFile(constrFileStr):
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
    global outputDatFileStr, lblDat, datSel

    outputDatFileStr = filedialog.asksaveasfilename(
        filetypes=DAT_FILES,
        defaultextension=DAT_FILES
        )

    if isInvalidFile(outputDatFileStr):
        datSel = False
        lblDat.config(text="No file selected")
    else:
        datSel = True
        lblDat.config(text=shrinkPathString(outputDatFileStr))

    updateProcessButtonStatus()


def isInvalidFile(dialogOutput) -> bool:
    # For whatever reason, filedialog.askname() can return multiple different things ???
    return dialogOutput == None or len(dialogOutput) == 0 or dialogOutput.strip() == ""


def updateProcessButtonStatus() -> None:
    global btnProc

    if objSel and constrSel and datSel:
        btnProc['state'] = 'normal'
    else:
        btnProc['state'] = 'disabled'


def shrinkPathString(pathstr: str) -> str:
    pathstr = str(pathstr)
    if len(pathstr) <= PATH_DISPLAY_LEN:
        return pathstr
    else:
        return '...' + pathstr[3 - PATH_DISPLAY_LEN:]






# ======================================================
#             Processing / Actual Conversion
# ======================================================

def doProcessing() -> None:
    '''
    Actually does the file processing. Based heavily on the main
    call of csv_to_dat.

    Will output all errors & warnings to the textbook.
    '''
    global txtOutput


    try:
        # Read Data
        objData = converter.openAndReadObjectiveCSV(objFileStr)
        constrData = converter.openAndReadConstraintCSV(constrFileStr)

        # Lint Data
        objData, constrData, messages = converter.lintInputData(objData, constrData)

        txtOutput.delete("1.0", tk.END)
        txtOutput.insert(tk.END, "\n\n".join(messages))

        if objData == None:
            txtOutput.insert("1.0", "[[ Errors Occured - Unable to Convert ]] \n\n")
            return

        # Output to File
        finalModel = converter.convertInputToFinalModel(objData, constrData)
        converter.writeOutputDat(finalModel, outputDatFileStr, objFileStr, constrFileStr)

        txtOutput.insert("1.0", "[[ Conversion Successful ]]\n\n")

    except Exception:
        txtOutput.delete("1.0", tk.END)
        txtOutput.insert(tk.END, "[[ Unkown Errors Occured :( - Unable to Convert ]]")

















#new main; instantiate mainWindow
def main():
    global lblObj, lblConstr, lblDat, btnProc, txtOutput

    #create a main window
    root = tk.Tk()
    root.option_add("*tearOff", False)
    root.title('NJFS ForMOM - CSV to Dat')
    root.geometry('450x600')
    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)

    #Import Theme
    style = ttk.Style(root)
    root.tk.call("source", "./theme/forest-light.tcl")
    style.theme_use("forest-light")


    #Title + Instruction Label
    frmTitle = ttk.Frame(root)

    lblTitle = ttk.Label(frmTitle, text="NJFS .csv to .dat Converter", font=("Arial", 20), anchor="center")
    lblInstruction = ttk.Label(frmTitle, text="Select Input CSV's and then Process", anchor="center")
    lblTitle.grid(row=0, column=0)
    lblInstruction.grid(row=1, column=0)

    #File Selectors
    frmFileSelectors = ttk.Frame(root)
    frmFileSelectors.rowconfigure([0, 1, 2], minsize=50, weight=1)
    frmFileSelectors.columnconfigure([0, 1], weight=1)
    frmFileSelectors.columnconfigure(0, minsize=125)

    btnObjFile = ttk.Button(frmFileSelectors,text='Objective CSV',command=setObjFile)
    lblObj     = ttk.Label(frmFileSelectors, text="No file selected", width=PATH_DISPLAY_LEN, anchor="w")
    btnObjFile.grid(row=0, column=0, sticky="nse", pady=5)
    lblObj.grid(row=0, column=1, sticky="nsw", padx=5)

    btnConstrFile = ttk.Button(frmFileSelectors,text='Constraint CSV',command=setConstrFile)
    lblConstr     = ttk.Label(frmFileSelectors, text="No file selected", width=PATH_DISPLAY_LEN, anchor="w")
    btnConstrFile.grid(row=1, column=0, sticky="nse", pady=5)
    lblConstr.grid(row=1, column=1, sticky="nsw", padx=5)

    btnDatFile = ttk.Button(frmFileSelectors,text='Output DAT',command=setOutFile)
    lblDat     = ttk.Label(frmFileSelectors, text="No file selected", width=PATH_DISPLAY_LEN, anchor="w")
    btnDatFile.grid(row=2, column=0, sticky="nse", pady=5)
    lblDat.grid(row=2, column=1, sticky="nsw", padx=5)

    #Processing
    frmProcess = ttk.Frame(root)
    frmProcess.rowconfigure(1, weight=1)
    frmProcess.columnconfigure(0, weight=1)

    btnProc = ttk.Button(frmProcess,text='Process',command=doProcessing)
    txtOutput = tk.Text(frmProcess, height=20)

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
