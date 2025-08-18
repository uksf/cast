testCommandLine = ["--json","local"]
version = "v0.0.4"
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import font
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import re
import requests
import json
import os
import sys
import pandas as pd
import threading
import queue
import pyperclip
from collections import Counter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
import matplotlib.patches as patches
from Functions import ArtilleryFunctions as AF

jsonType = 0
"""The mode that the program operates in

if 0 then the mode is local and uses local json files

if 1 then the mode is online and shared by using the uksf server json files"""

if len(sys.argv) > 1:
    for index,arg in enumerate(sys.argv):
        if str(arg) == "--json":
            if str(sys.argv[index+1]).lower() == "local":
                jsonType = 0
            elif str(sys.argv[index+1]).lower() == "server":
                jsonType = 1
elif testCommandLine != []:
    for index,arg in enumerate(testCommandLine):
        if str(arg) == "--json":
            if str(testCommandLine[index+1]).lower() == "local":
                jsonType = 0
            elif str(testCommandLine[index+1]).lower() == "server":
                jsonType = 1

def get_base_dir():
    """Get the base directory, works for both development and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        return Path(sys.executable).parent
    else:
        # Running as normal Python script
        return Path(__file__).resolve().parent

baseDir = get_base_dir()
currentFile = Path(__file__).resolve()
exeDir = currentFile.parent
appdata_local = Path(os.getenv('LOCALAPPDATA'))
os.makedirs(appdata_local/"UKSF"/"CAST",exist_ok=True)
user = "Unknown User"
update_queue = queue.Queue()
authToken = {}

def Json_Load(source : int,localOverride = False) -> dict | str:
    """
    Loads and returns the Json data from the specified source. Takes the "json" arguement and uses the appropriate json source
    
    source = 

    0 : Common variables (temperature, windspeed/direction etc.)
    1 : IDFP positons
    2 : Friendly positions
    3 : Target positions and their specified missions
    4 : Calculated fire missions
    5 : Message Log (returns string)
    6 : Artillery Configurations (Always local override)
    """
    if jsonType == 0 or localOverride == True or source == 6:
        try:
            if source == 0:
                with open(appdata_local/"UKSF"/"CAST"/"common.json","r") as file:
                    return json.load(file)
            elif source == 1:
                with open(appdata_local/"UKSF"/"CAST"/"IDFP.json","r") as file:
                    return json.load(file)
            elif source == 2:
                with open(appdata_local/"UKSF"/"CAST"/"Friendly.json","r") as file:
                    return json.load(file)
            elif source == 3:
                with open(appdata_local/"UKSF"/"CAST"/"Targets.json","r") as file:
                    return json.load(file)
            elif source == 4:
                with open(appdata_local/"UKSF"/"CAST"/"FireMissions.json","r") as file:
                    return json.load(file)
            elif source == 5:
                with open(appdata_local/"UKSF"/"CAST"/"Message_Log.json","r") as file:
                    return str(json.load(file)["message"])
            elif source == 6:
                with open(exeDir/"Functions"/"ArtilleryConfigs.json",mode="r") as file:
                    return json.load(file)
        except Exception as e:
            if source == 0: source = "Common parameters"
            elif source == 1: source = "IDFP position data"
            elif source == 2: source = "Friendly position data"
            elif source == 3: source = "Target position data"
            elif source == 4: source = "Fire mission data"
            elif source == 5:
                StatusMessageErrorDump(e, errorMessage="Failed to load Message log, returning nothing")
                return {}
            else: source = "Artillery Configurations"
            StatusMessageErrorDump(e, errorMessage=f"Failed to load {source}, returning nothing")
            return ""
                
                
                
    elif jsonType ==1:
        global authToken
        try:
            if source == 0:
                return json.loads(requests.get(url="https://api.uk-sf.co.uk/artillery/common",headers={"Authorization":"Bearer " + authToken["token"]}).json()["data"].replace("'",'"'))
            elif source == 1:
                return json.loads(requests.get(url="https://api.uk-sf.co.uk/artillery/idfp",headers={"Authorization":"Bearer " + authToken["token"]}).json()["data"].replace("'",'"'))
            elif source == 2:
                return json.loads(requests.get(url="https://api.uk-sf.co.uk/artillery/friendly",headers={"Authorization":"Bearer " + authToken["token"]}).json()["data"].replace("'",'"'))
            elif source == 3:
                return json.loads(requests.get(url="https://api.uk-sf.co.uk/artillery/target",headers={"Authorization":"Bearer " + authToken["token"]}).json()["data"].replace("'",'"'))
            elif source == 4:
                return json.loads(requests.get(url="https://api.uk-sf.co.uk/artillery/fireMissions",headers={"Authorization":"Bearer " + authToken["token"]}).json()["data"].replace("'",'"'))
            elif source == 5:
                return str(json.loads(requests.get(url="https://api.uk-sf.co.uk/artillery/message_log",headers={"Authorization":"Bearer " + authToken["token"]}).json()["data"].replace("'",'"'))["message"])
        except Exception as e:
            if source == 0: source = "Common parameters"
            elif source == 1: source = "IDFP position data"
            elif source == 2: source = "Friendly position data"
            elif source == 3: source = "Target position data"
            elif source == 4: source = "Fire mission data"
            elif source == 5:
                StatusMessageErrorDump(e, errorMessage="Failed load Message log, returning nothing")
                return {}
            else: source = "Artillery Configurations"
            StatusMessageErrorDump(e, errorMessage=f"Failed load {source}, returning nothing")
            return ""

def Json_Save(source : int,newEntry : dict | str, append = True,localOverride = False) -> bool:
    """
    Loads the Json data from the specified source then saves new data if append = True, otherwise it overwrite the json. Takes the "json" arguement and uses the appropriate json source
    
    source = 

    0 : Common variables (temperature, windspeed/direction etc.)
    1 : IDFP positons
    2 : Friendly positions
    3 : Target positions and their specified missions
    4 : Calculated fire missions
    5 : Message Log (string not dictionary)

    This does not merge nested jsons, it just replaces all keys within. Only the surface layer is overwritten
    """
    data = {}
    if append:
        if source !=5:
            data = (Json_Load(source,localOverride) | newEntry)
        else:
            message = Json_Load(5,localOverride) + str(newEntry)
            data["message"] = message
    else:
        if source == 5: data["message"] = str(newEntry)
        else: data = newEntry
    if jsonType == 0 or localOverride==True:
        try:
            if source == 0:
                with open(appdata_local/"UKSF"/"CAST"/"common.json","w") as file:
                    json.dump(data,file,indent=4)
            elif source == 1:
                with open(appdata_local/"UKSF"/"CAST"/"IDFP.json","w") as file:
                    json.dump(data,file,indent=4)
            elif source == 2:
                with open(appdata_local/"UKSF"/"CAST"/"Friendly.json","w") as file:
                    json.dump(data,file,indent=4)
            elif source == 3:
                with open(appdata_local/"UKSF"/"CAST"/"Targets.json","w") as file:
                    json.dump(data,file,indent=4)
            elif source == 4:
                with open(appdata_local/"UKSF"/"CAST"/"FireMissions.json","w") as file:
                    json.dump(data,file,indent=4)
            elif source == 5:
                with open(appdata_local/"UKSF"/"CAST"/"Message_Log.json","w") as file:
                    json.dump(data,file,indent=4)
            return True
        except Exception as e:
            if source == 0: source = "Common parameters"
            elif source == 1: source = "IDFP position data"
            elif source == 2: source = "Friendly position data"
            elif source == 3: source = "Target position data"
            elif source == 4: source = "Fire mission data"
            elif source == 5: source = "Message log"
            else: source = "Artillery Configurations"
            StatusMessageErrorDump(e, errorMessage=f"Failed to save {source}, returning False")
            return False
    elif jsonType ==1:
        try:
            if source == 0:
                return requests.put(url="https://api.uk-sf.co.uk/artillery/common",headers={"Authorization":"Bearer " + authToken["token"],"Content-Type": "application/json"},json={"data": str(data)})
            if source == 1:
                return requests.put(url="https://api.uk-sf.co.uk/artillery/idfp",headers={"Authorization":"Bearer " + authToken["token"],"Content-Type": "application/json"},json={"data": str(data)})
            if source == 2:
                return requests.put(url="https://api.uk-sf.co.uk/artillery/friendly",headers={"Authorization":"Bearer " + authToken["token"],"Content-Type": "application/json"},json={"data": str(data)})
            if source == 3:
                return requests.put(url="https://api.uk-sf.co.uk/artillery/target",headers={"Authorization":"Bearer " + authToken["token"],"Content-Type": "application/json"},json={"data": str(data)})
            if source == 4:
                return requests.put(url="https://api.uk-sf.co.uk/artillery/fireMissions",headers={"Authorization":"Bearer " + authToken["token"],"Content-Type": "application/json"},json={"data": str(data)})
            if source == 5:
                return requests.put(url="https://api.uk-sf.co.uk/artillery/message_log",headers={"Authorization":"Bearer " + authToken["token"],"Content-Type": "application/json"},json={"data": str(data)})
        except Exception as e:
            if source == 0: source = "Common parameters"
            elif source == 1: source = "IDFP position data"
            elif source == 2: source = "Friendly position data"
            elif source == 3: source = "Target position data"
            elif source == 4: source = "Fire mission data"
            elif source == 5: source = "Message log"
            else: source = "Artillery Configurations"
            StatusMessageErrorDump(e, errorMessage=f"Failed to save {source}, returning False")
            return False
        
def Json_Delete(source : int,deleteKey = None,localOverride = False) -> bool:
    """
    deleteKey specifies the list or string of the key that needs to be deleted from the source
    source = 

    0 : Common variables (temperature, windspeed/direction etc.)
    1 : IDFP positons
    2 : Friendly positions
    3 : Target positions and their specified missions
    4 : Calculated fire missions
    5 : Message Log
    """
    try:
        data = {}
        if deleteKey != None:
            data = Json_Load(source,localOverride)
            if type(deleteKey) == str: deleteKey = [deleteKey]
            for key in deleteKey:
                data.pop(str(key),None)
        Json_Save(source,data,False,localOverride)
    except Exception as e:
            if source == 0: source = "Common parameters"
            elif source == 1: source = "IDFP position data"
            elif source == 2: source = "Friendly position data"
            elif source == 3: source = "Target position data"
            elif source == 4: source = "Fire mission data"
            elif source == 5: source = "Message log"
            else: source = "Artillery Configurations"
            StatusMessageErrorDump(e, errorMessage=f"Failed to delete {source}, returning False")
            return False




xbm_data = """
#define tempstipple_width 32
#define tempstipple_height 32
static unsigned char tempstipple_bits[] = {
   0x01, 0x00, 0xfe, 0xff, 0x00, 0x00, 0xff, 0xff, 0x00, 0x80, 0xff, 0x7f,
   0x00, 0xc0, 0xff, 0x3f, 0x00, 0xe0, 0xff, 0x1f, 0x00, 0xf0, 0xff, 0x0f,
   0x00, 0xf8, 0xff, 0x07, 0x00, 0xfc, 0xff, 0x03, 0x00, 0xfe, 0xff, 0x01,
   0x00, 0xff, 0xff, 0x00, 0x80, 0xff, 0x7f, 0x00, 0xc0, 0xff, 0x3f, 0x00,
   0xe0, 0xff, 0x1f, 0x00, 0xf0, 0xff, 0x0f, 0x00, 0xf8, 0xff, 0x07, 0x00,
   0xfc, 0xff, 0x03, 0x00, 0xfe, 0xff, 0x00, 0x00, 0xff, 0x7f, 0x00, 0x80,
   0xff, 0x3f, 0x00, 0xc0, 0xff, 0x1f, 0x00, 0xe0, 0xff, 0x0f, 0x00, 0xf0,
   0xff, 0x07, 0x00, 0xf8, 0xff, 0x03, 0x00, 0xfc, 0xff, 0x01, 0x00, 0xfe,
   0xff, 0x00, 0x00, 0xff, 0x7f, 0x00, 0x80, 0xff, 0x3f, 0x00, 0xc0, 0xff,
   0x1f, 0x00, 0xe0, 0xff, 0x0f, 0x00, 0xf0, 0xff, 0x07, 0x00, 0xf8, 0xff,
   0x03, 0x00, 0xfc, 0xff, 0x01, 0x00, 0xfe, 0xff, 0x00, 0x00, 0x00, 0x00 };
   """
with open((baseDir/"tempstipple.xbm"),"w") as f:
    f.write(xbm_data)

root = Tk()
root.iconbitmap(bitmap=str(exeDir/"Functions"/"uksf.ico"))
#Name Ideas :
#AMISS - Artillery Mission Integration & Support System
#NOMAD – Networked Ordnance Management and Deployment
#LANCE – Long-range Artillery Networked Coordination Engine
#ARTOS – Artillery Targeting operations System
#TIFOR - Operation Targeting and Indirect fire Operation relay
#CAST - Coordinated Artillery Support Tool
root.title("Coordinated Artillery Support Tool")
root.state("zoomed")
#ttk.Style().theme_use('classic')

email = StringVar()
password = StringVar()



system = StringVar()
"""IDF system M6, L16, L119, Sholef"""
terrain = StringVar()
"""String Name of terrain"""
terrainTrace = ""
"""variable to track the terrian trace"""

messageLogOpen = 0
messageLogText = Text()
idfpName = StringVar()
"""Combobox entry for IDFP"""
idfpPosX = StringVar()
"""IDFP Position x ordinate"""
idfpPosY = StringVar()
"""IDFP Position y ordinate"""
idfpHeight = StringVar()
"""IDFP Position Height"""
idfpList = []
"""Listed strings of IDFPs in table"""

oldIdfpListSelection = ()
"""Reference for finding the last selected IDFP for table"""

idfpList = StringVar()
idfpLastSelection = -1
idfpUseCharge = StringVar()
"""The request to use specified charge at IDFP"""
idfpCharge = StringVar()
"""The selected charge from the IDFP"""
idfpTraj = StringVar()
"""The selected trajectory type from the IDFP"""

airTemperature = StringVar()
"""Air temperature in degrees celcius as displated by Kestrel"""
airHumidity = StringVar()
"""Air humidity as a percentage as displayed by Kestrel"""
airPressure = StringVar()
"""Air pressure in hPa as displated by Kestrel"""
windDirection = StringVar()
"""Wind Direction (Into headwind) as a bearing in degrees as displayed by Kestrel and ACE"""
windMagnitude = StringVar()
"""Wind Magnitude in m/s as displated by Kestrel"""
windDynamic = StringVar()
"""Shows solutions for with and without wind"""
friendlyName = StringVar()
"""Friendly Position name"""
friendlyPosX = StringVar()
"""Friendly Position x ordinate"""
friendlyPosY = StringVar()
"""Friendly Position y ordinate"""
friendlyHeight = StringVar()
"""Friendly Position Height"""
friendlyDispersion = StringVar()
"""Friendly Position troop dispersion"""

xylrfpf = StringVar()
"""Add new target XY/LR/FPF target prefix selection"""
targetReference = StringVar()
"""Target reference Series and Index ##"""
targetPosX = StringVar()
"""Target position X given as a 4/5 ordinate figures"""
targetPosY = StringVar()
"""Target position Y given as a 4/5 ordinate figures"""
targetHeight = StringVar()
"""Target position Height in metres"""

fireMissionEffect = StringVar()
"""Selected effect on radio selection"""
previousMissionEffect = "Destroy"
"""Previous Effect selected referenced when shifting from FPF to another FM"""
fireMissionWidth = StringVar()
"""Selected width for FM in metres"""
fireMissionDepth = StringVar()
"""Selected length for FM in metres"""
fireMissionLength = StringVar()
"""Selected length of mission, either a number given in second or minutes with prefix Fig/fig"""
fireMissionCondition = StringVar()
"""Condition needed to begin FM"""
fireMissionHour = StringVar()
"""The selected hour if 'Time' is selected for FM"""
fireMissionMinute = StringVar()
"""The selected minute if 'Time' is selected for FM"""
fireMissionSecond = StringVar()
"""The selected second if 'Time' is selected for FM"""
fireMissionPairedEffect = StringVar()
"""Selected mission if multiple FMs are selected for edit"""

clockOffset = StringVar()
"""Clock Offset used for fire mission splashes"""
clockSize = StringVar()
clockRimWidth = StringVar()
clockFontSize = StringVar()
clockHandSize = StringVar()
clockSecHandSize = StringVar()

terrainHeightMap = pd.DataFrame()
"""Terrain height map that contains heights of the map in metres for every metre square in a very large array"""
#"IDFP-1" : (GridX,GridY,Height,ForceCharge,Charge,Trajectory)

# Positions "00" :(GridX,GridY,Height,Effect,Dispersion,Length,condition,Time : {Hour, Minute, Second})
# Solutions "IDFP-Positon" :  "XY-00" : System, Range, Charge, RangeDeviation,
    # Bearing, AzimuthDeviation,Azimuth,AzimuthLeft,AzimuthRight,Elevation,ElevationDeviation,
    # ElevationLow,ElevationHigh,TOF,Vertex : {VGridX,VGridY,VHeight},Effect,Length,Condition,Notes,Trajectory,Orientation

targetList = {
    "LR" : {},
    "XY" : {},
    "FPF" : {},
    "Combo" : {}
    }
"""
Example Fire mission

    '00' : {'GridX' : 05123
    'GridY' : 94213
    'Height' : 234
    'Effect' : Destroy
    'Dispersion' : 150
    'Length' : Fig 1
    'Condition' : FWR
    'Time' : {'Hour': 12,
        'Minute': 52,
        'Second':23}
        }
"""
seriesDict = {
    "LR" : {},
    "XY" : {},
    "FPF" : {},
    "Combo" : {}
    }
"""Used to keep track of series of fire missions"""
listCheckBox_vars = {
    "LR" : {},
    "XY" : {},
    "FPF" : {},
    "Combo" : {}
    }
"""Used to keep track of the Checkboxes in the UI of the firemissions"""

FireMissions = {}
# FireMissions = {
#     "IDFP-1" : {
#         "FPF-10" : {
#             "System" : "L16",
#             "Range" : 5320,
#             "Charge" : 3,
#             "RangeDeviation" : 0,
#             "Bearing" : 1252,
#             "AzimuthDeviation" : 0,
#              "Azimuth" : 1255,
#              "AzimuthLeft" : 1236,
#              "AzimuthRight" : 1274,
#              "Elevation" : 921,
#              "ElevationDeviation" : 0,
#              "ElevationLow": 901,
#              "ElevationHigh": 933,
#              "TOF":30.34,
#              "Vertex" : 36,
#              "Effect": "FPF",
#              "Length": "Fig 3",
#              "Condition" : "FWR",
#              "Notes" : "",
#              "Trajectory" : "High"
#         },
#         "XY-00" : {
#             "System" : "L16",
#             "Range" : 5320,
#             "Charge" : 3,
#             "RangeDeviation" : 100,
#             "Bearing" : 1252,
#             "AzimuthDeviation" : 19,
#              "Azimuth" : 1255,
#             "AzimuthLeft" : 1236,
#              "AzimuthRight" : 1274,
#              "Elevation" : 921,
#              "ElevationDeviation" : 10,
#              "ElevationLow": 901,
#              "ElevationHigh": 933,
#              "TOF":30.34,
#              "Vertex" : 36,
#              "Effect": "Destroy",
#              "PairedEffect" : "Line",
#              "Length": "Fig 3",
#              "Condition" : "FWR",
#              "Notes" : "F",
#              "Trajectory" : "High"
#         }
#     },
#     "IDFP-2" : {
#         "XY-01" : {
#             "System" : "L16",
#             "Range" : 5320,
#             "Charge" : 3,
#             "RangeDeviation" : 100,
#             "Bearing" : 1252,
#             "AzimuthDeviation" : 19,
#              "Azimuth" : 1255,
#              "AzimuthLeft" : 1236,
#              "AzimuthRight" : 1274,
#              "Elevation" : 221,
#              "ElevationDeviation" : 5,
#              "ElevationLow": 216,
#              "ElevationHigh": 226,
#              "TOF":30.34,
#              "Vertex" : 36,
#              "Effect": "Destroy",
#              "Length": "Fig 3",
#              "Condition" : "FWR",
#              "Notes" : "F",
#              "Trajectory" : "Direct"
#         },
#         "XY-10" : {
#             "System" : "L16",
#             "Range" : 5320,
#             "Charge" : 3,
#             "RangeDeviation" : 0,
#             "Bearing" : 1252,
#             "AzimuthDeviation" : 0,
#              "Azimuth" : 1255,
#              "AzimuthLeft" : 1236,
#              "AzimuthRight" : 1274,
#              "Elevation" : 921,
#              "ElevationDeviation" : 0,
#              "ElevationLow": 901,
#              "ElevationHigh": 933,
#              "TOF":30.34,
#              "Vertex" : 36,
#              "Effect": "Destroy",
#              "Length": "Fig 3",
#              "Condition" : "FWR",
#              "Notes" : "",
#              "Trajectory" : "High"
#         },
#         "XY-01,XY-10" : {
#             "System" : "L16",
#             "Charge" : 3,
#             "RoundCount" : 60,
#             "Distance" : 450,
#             "Dispersion" : 50,
#             "Width" : 250,
#             "Azimuth" : 1255,
#             "AzimuthLeft" : 1216,
#             "AzimuthRight" : 1294,
#             "AzimuthDeviation" : 6,
#             "AzimuthRounds" : 6,
#             "Elevation" : 916,
#             "ElevationLow" : 880,
#             "ElevationHigh" : 953,
#             "ElevationDeviation" : 10,
#             "ElevationRounds": 10,
#             "TOF" : 30.12,
#             "Vertex" : 38,
#             "Effect" : "Destroy",
#             "PairedEffect" : "Creeping Barrage",
#             "Condition" : "FWR",
#             "Notes" : "Creeping test",
#             "Trajectory" : "High",
#         },
#         "LR-00" : {
#             "System" : "L16",
#             "Range" : 5320,
#             "Charge" : 3,
#             "RangeDeviation" : 100,
#             "Bearing" : 1252,
#             "AzimuthDeviation" : 19,
#              "Azimuth" : 1255,
#              "AzimuthLeft" : 1236,
#              "AzimuthRight" : 1274,
#              "Elevation" : 221,
#              "ElevationDeviation" : 5,
#              "ElevationLow": 216,
#              "ElevationHigh": 226,
#              "TOF":30.34,
#              "Vertex" : 36,
#              "Effect": "Destroy",
#              "Length": "Fig 3",
#              "Condition" : "FWR",
#              "Notes" : "F",
#              "Trajectory" : "Direct"
#         },
#     }
# }#Json format
# """
# Fire mission solutions given as a JSON. New fire missions are added to this dictionary and it's saved in JSON format.
# Multiple versions of the fire mission should be accessed here and given by the artillery functions.
# """
FPFEditSelected = False
"""Allows the user to select the edit buttons against fire missions"""
idfpNotebookFrameDict = {}
"""Notebook frames for each IDFP, the fire missions dictionary is read and the IDFPs are displayed"""
def ListTerrainFolders():
    """
    Function to get the terrains and folders from /Terrains/
    """
    folders = []
    terrains = []
    for dirpath,dirs,files in os.walk(baseDir/"Terrains"):
        for dirName in dirs:
            try:
                for dirpath2,dirs2,files2 in os.walk(baseDir/"Terrains"/dirName):
                    if str(dirName+".gzcsv") in files2:
                        terrains.append(dirName)
                        folders.append(os.path.join(dirpath,dirName))
                    else: StatusMessageLog(message=f"Folder does not have a valid height map file: {dirName}")
            except Exception as e: StatusMessageErrorDump(e,errorMessage=f"Folder issue in map: {dirName}")
    return(terrains,folders)

terrainsFolders = []

def StatusMessageLog(message = "",privateMessage = None):
    """
    Displays message in the status bar and log. Private message is given only to the user in the status bar, if message is "", it's not included in the log.
    """
    global messageLogText
    global user
    if privateMessage == None:
        statusMessageLabel.config(text=message)
    elif privateMessage == "Empty": None
    else:
        statusMessageLabel.config(text=privateMessage)
    if message != "":
        oldMessageLog = Json_Load(source=5)
        Json_Save(source=5,newEntry=(str(datetime.now(timezone.utc))[:-11] + "\t" + "|" + "\t" + user + "\t" + "|" + "\t" + message+"\n"),append=True)
        if messageLogOpen == 1:
            messageLogText["state"] = "normal"
            messageLogText.delete("1.0","end")
            messageLogText.insert("end",ReadMessageLog()) 
            messageLogText["state"] = "disabled"
            messageLogText.yview_moveto(1)

def StatusMessageErrorDump(e: Exception, errorMessage = ""):
    if errorMessage != "":
        StatusMessageLog(message=errorMessage)
    try:
        excType, excValue, excTraceback = sys.exc_info()
        if excTraceback:
            StatusMessageLog(message=f"Error details:\n\tType: {str(excType)}\n\tError: {str(excValue)}\n\tdetails:\n\t\tfile: {excTraceback.tb_frame.f_code.co_filename.split('\\')[-1]}\n\t\tfunction: {excTraceback.tb_frame.f_code.co_name}\n\t\tline: {excTraceback.tb_lineno}",privateMessage="Empty")
        else: StatusMessageLog(message=f"Failed error message")
    except: StatusMessageLog(message=f"Failed error message")

def LoginWindow(startup=False):
    """Opens the login window"""
    def Login():
        if email.get().strip() !="":
            if password.get() !="":
                global user
                global authToken
                loginMessage.grid()
                loginMessage["text"] = "Logging in"
                loginDetails = {"email" : email.get().strip(), "password" : password.get()}
                password.set("")
                localStorageToken = requests.post(url="https://api.uk-sf.co.uk/auth/login",json=loginDetails)
                loginDetails = None
                try:
                    authToken["token"] = localStorageToken.json()["token"]
                    loginAcount = requests.get(url="https://api.uk-sf.co.uk/accounts",headers={"Authorization":"Bearer " + localStorageToken.json()["token"]}) 
                    loginAcount.json()["displayName"]
                except:
                    try:
                        loginMessage["text"] = localStorageToken.json()["error"]
                    except Exception as e:
                        StatusMessageErrorDump(e,errorMessage="Failed to produce login error")
                else:
                    StatusMessageLog("Logged in as " + loginAcount.json()["displayName"])
                    user = loginAcount.json()["displayName"]
                    loginMessage["text"] = "Logged in as " + loginAcount.json()["displayName"]
                    with open(file=appdata_local/"UKSF"/"CAST"/"auth.json",mode="w") as file:
                        json.dump(localStorageToken.json(),file,indent=4)
                    if startup == True:
                        StartUp(login=True)
                    login_menu.entryconfigure("Login",state=DISABLED)
                    login_menu.entryconfigure("Logout",state=NORMAL)
                    loginTopLevel.grab_release()
                    loginTopLevel.destroy()
                    return True
            else:
                loginMessage.grid()
                loginMessage["text"] = "Enter Password"
                loginPasswordEntry.focus_set()
        else:
            loginMessage.grid()
            loginMessage["text"] = "Enter email address"
            loginUsernameEntry.focus_set()
    def LoginClosed():
        loginTopLevel.grab_release()
        root.destroy()
    loginTopLevel = Toplevel(root)
    loginTopLevel.grab_set()
    loginTopLevel.attributes("-topmost",True)
    loginTopLevel.title("UKSF Login")
    loginTopLevel.geometry("350x200")
    loginTopLevel.iconbitmap(exeDir/"Functions"/"uksf.ico")
    loginWindow = loginTopLevel.winfo_toplevel()
    loginWindow.anchor("nw")
    loginWindow.grid_columnconfigure(0,weight=1)
    loginWindow.grid_rowconfigure(0,weight=1)
    loginFrame = ttk.Frame(loginWindow,padding=20)
    loginFrame.grid_columnconfigure(0,weight=1)
    loginFrame.grid_rowconfigure(0,minsize=50,weight=2)
    loginFrame.grid_rowconfigure((1,2),weight=1)
    loginLabelframe = ttk.LabelFrame(loginFrame,text="uk-sf.co.uk",padding=5)
    loginLabelframe.grid_columnconfigure(0,minsize=60)
    loginLabelframe.grid_columnconfigure(1,weight=1)
    loginLabelframe.grid_rowconfigure((0,1),minsize=20,weight=1)
    loginUsernameLabel = ttk.Label(loginLabelframe,text="Email:",justify="right")
    loginPasswordLabel = ttk.Label(loginLabelframe,text="Password:",justify="right")
    loginUsernameEntry = ttk.Entry(loginLabelframe,justify="center",textvariable=email)
    loginPasswordEntry = ttk.Entry(loginLabelframe,justify="center",textvariable=password,show="*")
    loginMessage = ttk.Label(loginFrame,text="",justify="right")
    loginButton = ttk.Button(loginFrame,text="Login",command=Login)
    loginFrame.grid(row=0,column=0,sticky="NESW")
    loginLabelframe.grid(row=0,column=0,sticky="NESW")
    loginUsernameLabel.grid(row=0,column=0,sticky="E")
    loginPasswordLabel.grid(row=1,column=0,sticky="E")
    loginUsernameEntry.grid(row=0,column=1,sticky="EW")
    loginPasswordEntry.grid(row=1,column=1,sticky="EW")
    loginMessage.grid(row=1,column=0,sticky="NS")
    loginMessage.grid_remove()
    loginButton.grid(row=2,column=0,sticky="EW")
    loginTopLevel.protocol("WM_DELETE_WINDOW",LoginClosed)
    

def LoginRefresh():
    """Collects a fresh auth token and writes to file"""
    global user
    global authToken
    try:
        with open(file=appdata_local/"UKSF"/"CAST"/"auth.json",mode="r") as file:
            file = file.read()
        authToken["token"] = json.loads(file)["token"]
        loginAcount = requests.get(url="https://api.uk-sf.co.uk/accounts",headers={"Authorization":"Bearer " + authToken["token"]})
        StatusMessageLog("Logged back in as " + loginAcount.json()["displayName"])
    except:
        if LoginWindow(startup=True)==True:
            return True
    else:
        user = loginAcount.json()["displayName"]
        with open(file=appdata_local/"UKSF"/"CAST"/"auth.json",mode="w") as file:
            json.dump(requests.get(url="https://api.uk-sf.co.uk/auth/refresh",headers={"Authorization":"Bearer " + authToken["token"]}).json(),file,indent=4)
        login_menu.entryconfigure("Logout",state=NORMAL)
        login_menu.entryconfigure("Login",state=DISABLED)
        return True

def Logout():
    """Logs out and deletes auth token, then closes the window to not cause authentication issues with the server"""
    login_menu.entryconfigure("Logout",state=DISABLED)
    login_menu.entryconfigure("Login",state=NORMAL)
    global user
    with open(file=appdata_local/"UKSF"/"CAST"/"auth.json",mode="w") as file:
        file.write("")
        StatusMessageLog("Logged out")
        user = "Logged Out User"
    root.destroy()
    
def IDFCalculatorClosed():
    """Things to do when the IDF calculator is closed"""
    StatusMessageLog("Closed IDF Calculator")
    Path(baseDir/"tempstipple.xbm").unlink(missing_ok=True)
    root.destroy()
root.protocol("WM_DELETE_WINDOW",IDFCalculatorClosed)

def UpdateStringVar(StrVar: StringVar, value,trace=None,entryLabel=None):
    try:
        if trace!=None:
            StrVar.trace_remove(mode="write",cbname=trace)
        StrVar.set(value)
    except Exception as e: StatusMessageErrorDump(e,errorMessage=f"Failed to set string variable {StrVar} to {value}")

def NewHeightMapFile(filePath: str,terrainName: str,compression = True):
    """Add a new Height map file using https://github.com/Keithenneu/Beowulf.ArmaTerrainExport Information on how to install in the instructions doc"""
    targetListCalculate["state"] = "disabled"
    statusProgressBar["value"],statusProgressBar["mode"] = 0,"determinate"
    #terrainName
    start = ""
    end = ""
    with open(file=filePath) as file:
        for line in file:
            start = line
            break
    with open(file=filePath,mode="rb") as file:
        try:
            file.seek(-2,os.SEEK_END)
            while file.read(1)!=b'\n':
                file.seek(-2,os.SEEK_CUR)
        except OSError:
            file.seek(0)
        except Exception as e:
            StatusMessageErrorDump(e,errorMessage="Failed to seek in file")
        end = file.readline().decode()
    start = start.replace("\n","").replace("\r","").split(sep=" ")
    end = end.replace("\n","").replace("\r","").split(sep=" ")
    statusProgressBar["maximum"] = int(end[0])-int(start[0])
    xrow = None
    rowList = []
    heights = ""
    os.makedirs(baseDir/"Terrains"/terrainName,exist_ok=True)
    StatusMessageLog("Beginning "+ terrainName.replace("_"," ")+ " height map format")
    with open(file=filePath) as file:
        with open(file=baseDir/"Terrains"/terrainName/(terrainName+".gzcsv"),mode="w") as outputfile:
            outputfile.write("")
        for line in file:
            line = line.replace("\n","").replace("\r","").split(sep=" ") # CHECK TO SEE IF THE LAST HEIGHTS ARE ADDED
            if xrow != int(line[0]) and line != start:
                heights += str(rowList).replace("[","").replace("]","") + "\n"
                if len(heights) > 175000000 and line[0]!= end[0]:
                    with open(file=baseDir/"Terrains"/terrainName/str(terrainName+".gzcsv"),mode="a") as outputfile:
                        outputfile.write(str(heights))
                    heights = ""
                rowList = []
                #statusProgressBar.step(1)
                statusProgressBar["value"] = int(line[0])-int(start[0])
                #statusProgressBar.step(0)
                statusProgressBar.update()
            xrow = int(line[0])
            if float(line[2])<0:
                rowList.append(0)
            else:
                rowList.append(round(float(line[2]),ndigits=1))
    StatusMessageLog("Completed "+ terrainName.replace("_"," ")+ " height map format")
    statusMessageLabel.update()
    if compression:
        StatusMessageLog("Beginning compression of "+ terrainName.replace("_"," ")+ " height map. Please wait several minutes")
        statusMessageLabel.update()
        data = pd.read_csv(baseDir/"Terrains"/terrainName/str(terrainName+".gzcsv"),header=None)
        data.to_csv(baseDir/"Terrains"/terrainName/str(terrainName+".gzcsv"),compression="gzip")
        StatusMessageLog("Completed compression of "+ terrainName.replace("_"," ")+ " height map")
    targetListCalculate["state"] = "normal"
    statusProgressBar["value"] = 0
    statusProgressBar.update()
    statusProgressBar.stop()
    global terrainTrace
    terrain.trace_remove("write",cbname=terrainTrace)
    terrain_menu.add_radiobutton(label=terrainName,variable=terrain,value=terrainName)
    root.bell()
    TerrainFolderCheck()


def HeightMapFileDialog():
    """Used to select the terrain to convert for a heightmap"""
    def HeightMapTolLevelClosed():
        HeightMapTopLevel.grab_release()
        HeightMapTopLevel.destroy()
    def HeightMapAccept(*args):
        if mapName.get().count(",") > 0:
            mapName.set("")
        else:
            HeightMapTopLevel.grab_release()
            HeightMapTopLevel.destroy()
            if mapName.get() != "":
                filePath = filedialog.askopenfilename(initialdir="C:/arma3/terrain",title=f"Select corresponding {mapName.get()} terrain height map",filetypes=(("Text files","*txt"),("All files","*.*")))
                if filePath:
                    NewHeightMapFile(filePath,terrainName=mapName.get().replace(" ","_"))
    HeightMapTopLevel = Toplevel(root)
    HeightMapTopLevel.grab_set()
    HeightMapTopLevel.attributes("-topmost",True)
    HeightMapTopLevel.title("Select terrain name")
    HeightMapTopLevel.geometry("350x70")
    HeightMapTopLevel.resizable(width=False,height=False)
    HeightMapTopLevel.iconbitmap(exeDir/"Functions"/"uksf.ico")
    HeightMapWindow = HeightMapTopLevel.winfo_toplevel()
    HeightMapWindow.anchor("nw")
    HeightMapWindow.grid_columnconfigure(0,weight=1)
    HeightMapWindow.grid_rowconfigure(0,weight=1)
    HeightMapFrame = ttk.Frame(HeightMapWindow,padding=10)
    HeightMapFrame.grid(row="0",column="0",sticky="nesw")
    HeightMapFrame.grid_columnconfigure((0,2),minsize=10)
    HeightMapFrame.grid_columnconfigure(1,weight=1)
    HeightMapFrame.grid_rowconfigure(0,weight=1)
    mapName = StringVar()
    HeightMapLabel =ttk.Label(HeightMapFrame,text="Map Name:",justify="right")
    HeightMapEntry = ttk.Entry(HeightMapFrame,textvariable=mapName,justify="center")
    HeightMapButton = ttk.Button(HeightMapFrame,text="Accept",command=HeightMapAccept)
    HeightMapFrame.grid(row="0",column="0",sticky="nesw")
    HeightMapLabel.grid(row="0",column="0",sticky="nesw")
    HeightMapEntry.grid(row="0",column="1",sticky="ew")
    HeightMapButton.grid(row="0",column="2",sticky="ew")
    HeightMapEntry.focus()
    HeightMapEntry.bind("<Return>",HeightMapAccept)
    HeightMapTopLevel.protocol("WM_DELETE_WINDOW",HeightMapTolLevelClosed)

maxRow, maxCol,maxTerrainHeight = 0,0,0.0

def TerrainChange(*args):
    """Change the selected terrain"""
    global terrainHeightMap
    global maxRow
    global maxCol
    global maxTerrainHeight
    if terrain.get() != "":
        try:
            StatusMessageLog(privateMessage=F"Loading {terrain.get()} Height map")
            statusMessageLabel.update_idletasks()
            Json_Save(source=0,newEntry={"terrain" : terrain.get()},localOverride=True)
            terrainHeightMap = pd.read_csv(baseDir/"Terrains"/terrain.get()/(terrain.get()+".gzcsv"),compression="gzip")
            maxRow, maxCol = terrainHeightMap.shape
            maxTerrainHeight = terrainHeightMap.to_numpy().max()
            StatusMessageLog("Loaded "+terrain.get().replace("_"," ")+ " Height map")
            root.bell()
        except Exception as e:
            StatusMessageErrorDump(e,errorMessage=f"Could not find terrain height map data for {terrain.get()}")
            terrain.set(-1)
            Json_Save(source=0,newEntry={"terrain" : terrain.get()},localOverride=True)


def FlipWindowPanes():
    """Flip the panes backwards"""
    if int(flipPaneSide.get()) == 0:
        fireMissionPagePanedWindow.insert(1,pane4)
        fireMissionPagePanedWindow.insert(2,pane3)
        fireMissionPagePanedWindow.insert(3,pane2)
        fireMissionPagePanedWindow.insert(4,pane1)
        flipPaneSide.set(1)
    else:
        fireMissionPagePanedWindow.insert(4,pane4)
        fireMissionPagePanedWindow.insert(3,pane3)
        fireMissionPagePanedWindow.insert(2,pane2)
        fireMissionPagePanedWindow.insert(1,pane1)
        flipPaneSide.set(0)
    StatusMessageLog("Fire Mission window panes flipped")

def ClearMessageLog():
    """Removes all messages from the Log"""
    Json_Delete(source=5)
    StatusMessageLog("Status log cleared")

def ClearFireMission(mission = "", name = "",calculated = False):
    """
    Will the mission (LR,XY,FPF,Combo) and take the name suffixes (...-##) and remove it from the target jsons, the calculated ones to if calculated == True
    
    If name is left empty ("") then all targets/fire missions of the selected mission will be deleted. if mission is not specified. all is removed.
    """
    if mission =="":
        try:
            Json_Delete(source=3)
            StatusMessageLog(message=f"Deleted all target positions from JSON")
        except Exception as e:
            StatusMessageErrorDump(e,errorMessage=f"Failed to delete target positions from JSON")
        else:
            if calculated == True:
                try:
                    Json_Delete(source=4)
                    StatusMessageLog(message=f"Deleted all calculated fire missions from JSON")
                except Exception as e:
                    StatusMessageErrorDump(e,errorMessage=f"Failed to delete calculated fire missions from JSON")
    else:
        if name =="":
            try:
                Json_Delete(source=3,deleteKey=mission)
                StatusMessageLog(message=f"Deleted {mission} target positions from JSON")
            except Exception as e: StatusMessageErrorDump(e,errorMessage=f"Failed to delete {mission} target positions from JSON")
            else:
                if calculated == True:
                    try:
                        FireMissions = Json_Load(source=4)
                        for idfp,missions in list(FireMissions.items()):
                            for key in list(missions.keys()):
                                if key[:2] == mission:
                                    FireMissions[idfp].pop(key,None)
                        Json_Save(source=4,newEntry=FireMissions,append=False)
                        StatusMessageLog(message=f"Deleted calculated {mission} fire missions from JSON")
                    except Exception as e: StatusMessageErrorDump(e,errorMessage=f"Failed to delete calculated {mission} fire missions from JSON")
        else:
            try:
                targets = Json_Load(source=3)
                targets[mission].pop(name)
                Json_Save(source=3,newEntry=targets,append=False)
                StatusMessageLog(message=f"Deleted {mission}-{name} target position from JSON")
            except Exception as e: StatusMessageErrorDump(e,errorMessage=f"Failed to delete {mission}-{name} target position from JSON")
            else:
                if calculated == True:
                    try:
                        FireMissions = Json_Load(source=4)
                        for idfp, missions in list(FireMissions.items()):
                            FireMissions[idfp].pop(f"{mission}-{name}",None)
                        Json_Save(source=4,newEntry=FireMissions,append=False)
                        StatusMessageLog(message=f"Deleted calculated mission {mission}-{name} from JSON")
                    except Exception as e: StatusMessageErrorDump(e,errorMessage=f"Failed to delete calculated mission {mission}-{name} from JSON")
    UpdateSync([3,4])
def ClearIDFP(IDFP = None):
    """Will clear either all IDFPs or the specified IDFP string"""
    if IDFP == None:
        try:
            Json_Delete(source=1)
            Json_Delete(source=4)
            for tabId in idfpNotebook.tabs():
                idfpNotebook.forget(tabId)
            UpdateSync(1)
            StatusMessageLog("Cleared IDFPs")
        except Exception as e:
            StatusMessageErrorDump(e,errorMessage="Failed to delete IDFPs from JSON")
    else:
        try:
            Json_Delete(source=1,deleteKey=IDFP)
            Json_Delete(source=4,deleteKey=IDFP)
            for tabId in idfpNotebook.tabs():
                if idfpNotebook.tab(tabId,option="text") == IDFP:
                    idfpNotebook.forget(tabId)
                    break
            UpdateSync(1)
            StatusMessageLog(message=("Cleared "+IDFP))
        except Exception as e:
            StatusMessageErrorDump(e,errorMessage=f"Failed to delete {IDFP} from JSON")
def ClearFriendlyPositions():
    Json_Delete(source=2)
    StatusMessageLog("Cleared friendly positions")
    friendlyName.set("")
    friendlyNameCombobox["values"] = []
def ClearAll():
    ClearMessageLog()
    ClearFireMission()
    ClearIDFP()
    ClearFriendlyPositions()
    StatusMessageLog("All position(s) cleared")

def ClearSafety(var, index, mode):
    if int(resetSafety.get()) == 0:
        reset_menu.entryconfigure("Status Log",state=NORMAL)
        reset_menu.entryconfigure("IDFP Position(s)",state=NORMAL)
        reset_menu.entryconfigure("Friendly Position(s)",state=NORMAL)
        reset_menu.entryconfigure("Fire Missions",state=NORMAL)
        reset_menu.entryconfigure("All Positions",state=NORMAL)
    else:
        reset_menu.entryconfigure("Status Log",state=DISABLED)
        reset_menu.entryconfigure("IDFP Position(s)",state=DISABLED)
        reset_menu.entryconfigure("Friendly Position(s)",state=DISABLED)
        reset_menu.entryconfigure("Fire Missions",state=DISABLED)
        reset_menu.entryconfigure("All Positions",state=DISABLED)
        
def ReadMessageLog():
    # with open(baseDir/"Functions"/"message_log.dat",mode="r") as messageLogFile:
    #     message = messageLogFile.read()
    #     return message.replace("_", " ")
    return Json_Load(source=5)
def OpenMessageLog(var):
    global messageLogText
    global messageLogOpen
    messageLogOpen = 1
    def MessageLogClosed():
        global messageLogOpen
        messageLogOpen = 0
        messageLog.destroy()
    messageLog = Toplevel(root)
    messageLog.attributes("-topmost",True)
    messageLog.title("Status Log")
    messageLog.geometry("950x100")
    messageLog.iconbitmap(exeDir/"Functions"/"statuslog.ico")
    messageLogWindow = messageLog.winfo_toplevel()
    messageLogWindow.anchor("nw")
    messageLogWindow.rowconfigure(0,weight=1)
    messageLogWindow.columnconfigure(0,weight=1)
    messageLogWindow.minsize(550,150)
    messageLogContent = ttk.Frame(messageLog)
    messageLogContent.grid_rowconfigure(0,weight=1)
    messageLogContent.grid_columnconfigure(0,weight=1)
    messageLogText = Text(messageLogContent,wrap="none",width="500")
    yScroll = Scrollbar(messageLogContent,orient="vertical",command=messageLogText.yview)
    xScroll = Scrollbar(messageLogContent,orient="horizontal",command=messageLogText.xview)
    messageLogText["yscrollcommand"] = yScroll.set
    messageLogText["xscrollcommand"] = xScroll.set
    messageLogText.insert("1.0",ReadMessageLog())
    messageLogText["state"] = "disabled"
    messageLogContent.grid(column=0,row=0,sticky="NESW")
    messageLogText.grid(column=0,row=0,sticky="NESW")
    yScroll.grid(column=1,row=0, sticky="ns")
    xScroll.grid(column=0,row=1, sticky="we")
    messageLogText.yview_moveto(1)
    messageLog.protocol("WM_DELETE_WINDOW",MessageLogClosed)


######################################################################################          CONVERT TO JSON
def SystemChange(*args,newSystem = None,set = False):
    # For trace
    system.trace_remove(mode="write",cbname=settings_to_process["system"]["traceName"])
    if set:
        try:
            oldSystem = Json_Load(source=0)["system"]
        except:
            try:
                Json_Save(source=0,newEntry={"system" : system.get()})
            except Exception as e: StatusMessageErrorDump(e, errorMessage="Could not save current system to JSON after not finding the original system in JSON")
            else:
                StatusMessageLog(f"Changed artillery system to {system.get()}")
                StatusMessageLog(message="",privateMessage="Could not find original system in JSON")
        else:
            try:
                Json_Save(source=0,newEntry={"system" : system.get()})
            except Exception as e: StatusMessageErrorDump(e,errorMessage="Could not save current system to JSON")
            else:
                StatusMessageLog(f"Changed artillery system from {oldSystem} to {system.get()}")
        try: idfpSystemOutput["text"] = system.get()
        except: idfpSystemOutput["text"] = "Error"
        StatusMessageLog("System Change: If pre-existing IDFP selections are present, check selection charges, trajectories and old calculations")
    # For Saving from JSON
    else:
        try:
            oldSystem = system.get()
            system.set(newSystem)
            idfpSystemOutput["text"] = newSystem
            StatusMessageLog(f"Artillery system has changed from {oldSystem} to {newSystem}") if oldSystem !="" else StatusMessageLog(f"Artillery system set to {newSystem}")
            StatusMessageLog(message="",privateMessage="System Change: If pre-existing IDFP selections are present, check selection charges, trajectories and old calculations")
        except Exception as e: StatusMessageErrorDump(e,message="Could not set system from JSON")
    systemTrace = system.trace_add(mode = "write", callback=lambda *args: SystemChange(newSystem=system.get(),set=True))
    settings_to_process["system"]["traceName"] = systemTrace 
    systems = Json_Load(6)
    try:
        idfpEditChargeComboBox["values"] = systems[system.get()]["Charges"]
        idfpEditTrajComboBox["values"] = systems[system.get()]["Trajectories"]
    except Exception as e: StatusMessageErrorDump(e,errorMessage="Failed to set system combo boxes or load system configurations")

def IDFPListInitialise():
    """Updates the list of IDFPs in the list box, it also selects the previous selections made both from last session and just before the listbox is udpated"""
    try:
        idfpFile = Json_Load(1)
        idfpList.set(list(idfpFile.keys()))
        idfpNameCombobox["values"] = list(idfpFile.keys())
    except Exception as e:
        StatusMessageErrorDump(e,errorMessage="Failed to Load IDFPs from JSON")
        return None
    try:
        idfpSelection = (Json_Load(source=0,localOverride=True))["IDFPSelection"]
        if idfpSelection != None or idfpSelection != [-1]:
            for select in idfpSelection:
                idfpListbox.selection_set(select,select)
    except Exception as e:
        StatusMessageErrorDump(e,errorMessage="Failed to Load last IDFP selections")
        Json_Save(0,{"IDFPSelection":[]},localOverride=True)

def IDFPUpdate(idfp):
    try:
        idfpList.set(list(idfp))
        idfpNameCombobox["values"] = list(idfp)
    except Exception as e:
        StatusMessageErrorDump(e,errorMessage="Failed to Load IDFPs from JSON")

def IdfpListBoxChange(option):
    oldList = Json_Load(0,True)
    try:
        list(set(list(option)).symmetric_difference(set(oldList["IDFPSelection"])))
    except KeyError: pass
    oldList["IDFPSelection"] = list(option)
    Json_Save(0,oldList,localOverride=True)

def IDFPHeightAutoFill(event):
    if event.keysym=="Return" or event.keysym=="Tab":
        if len(idfpPosX.get())>=4 and len(idfpPosX.get())<=5 and len(idfpPosY.get())>=4 and len(idfpPosY.get())<=5:
            if len(idfpPosX.get()) == 4:
                x = idfpPosX.get()+"0"
            elif len(idfpPosX.get()) == 5:
                x = idfpPosX.get()
            if len(idfpPosY.get()) == 4:
                y = idfpPosY.get()+"0"
            elif len(idfpPosY.get()) == 5:
                y = idfpPosY.get()
            if int(x) > maxRow:
                x = maxRow-1
            elif int(x) < 0:
                x = 0
            if int(y) > maxCol:
                y = maxCol-1
            elif int(y) < 0:
                y = 0  
            try:
                idfpHeight.set(terrainHeightMap.iat[int(x),int(y)])
            except:
                pass


def LoadInfo(event,source):
    """
    Source:
    1 : IDFP positons
    2 : Friendly positions
    3 : Target positions and their specified missions
    """
    try:
        if event.keysym=="Return" or event.keysym=="Tab":
            if source == 1: json = Json_Load(1)
            elif source == 2: json = Json_Load(2)
            elif source == 3: json = Json_Load(3)
            for name,details in json.items():
                if source == 1:
                    if idfpName.get() == name:
                        idfpPosX.set(details["GridX"])
                        idfpPosY.set(details["GridY"])
                        idfpHeight.set(details["Height"])
                        idfpUseCharge.set(details["ForceCharge"])
                        idfpCharge.set(details["Charge"])
                        idfpTraj.set(details["Trajectory"])
                    
                elif source == 2:
                    if friendlyName.get() == name:
                        friendlyPosX.set(details["GridX"])
                        friendlyPosY.set(details["GridY"])
                        friendlyHeight.set(details["Height"])
                        friendlyDispersion.set(details["Dispersion"])
                    
                #elif source == 3:
    except:
        None
    if source ==1:LabelBold(idfpNameLabel,stringvar="idfpName")
    elif source ==2: LabelBold(friendlyNameLabel,stringvar="friendlyName")

def IDFPPositionAddUpdate():
    try:
        if len(idfpPosX.get()) in (4,5) and len(idfpPosY.get()) in (4,5) and idfpPosX.get().isdigit() and idfpPosY.get().isdigit() and all(not var for var in (idfpName.get().isspace(),idfpHeight.get().isspace(),idfpHeight.get().isalpha())):
            charge = int(idfpCharge.get()) if idfpCharge.get() != "" else 1
            traj = idfpTraj.get() if idfpTraj.get() != "" else "High"
            newPos = {
                idfpName.get() : {
                    "GridX" : idfpPosX.get(),
                    "GridY" : idfpPosY.get(),
                    "Height" : float(idfpHeight.get()),
                    "ForceCharge" : int(idfpUseCharge.get()),
                    "Charge" : charge,
                    "Trajectory" : traj
                }
            }
            try: Json_Load(1)[idfpName.get()]
            except KeyError: StatusMessageLog(message=f"{idfpName.get()} has been added at position {idfpPosX.get()}, {idfpPosY.get()} at {idfpHeight.get()} m")
            except Exception as e: StatusMessageErrorDump(e,errorMessage="Error loading the IDFP")
            else: StatusMessageLog(message=f"{idfpName.get()} has been updated, position {idfpPosX.get()}, {idfpPosY.get()} at {idfpHeight.get()} m")
            Json_Save(1,newPos)
            
            UpdateSync(1)
            LabelBold(idfpNameLabel,"Normal","idfpName")
            boldLables["idfpName"] = False
    except Exception as e:
        StatusMessageErrorDump(e,errorMessage="Failed to Add/Update IDFP")

def IDFPPositionRemove(*args,name):
    if name != "":
        try:
            Json_Delete(source=1,deleteKey=name)
            idfpListbox.select_clear(0,END)
            UpdateSync(1)
        except Exception as e:
            StatusMessageErrorDump(e,errorMessage=f"Failed to delete {name}")
            pass
        else:
            StatusMessageLog(message=name + " has been deleted")
            try:
                Json_Delete(source=4,deleteKey=name)
                for tabId in idfpNotebook.tabs():
                    if idfpNotebook.tab(tabId,option="text") == name:
                        idfpNotebook.forget(tabId)
                        break
                UpdateSync(4)
            except: pass
            else:
                StatusMessageLog(message=name + " calculated fire missions have been deleted")
            try:
                LabelBold(idfpNameLabel,"Normal",idfpName)
                boldLables["idfpName"] = False
            except: pass
            

def IDFPChangeSetting(setting: str,namedIdfp:str,value,*args):
    try:
        idfp = Json_Load(source=1)[namedIdfp]
        idfp[setting] == value
        Json_Save(source=1,newEntry={namedIdfp : idfp})
    except: None

def TemperatureEntryValidate(*args):
    value = (str(airTemperature.get()))
    if str(airTemperature.get()) != "":
        if value.count("-")>1:
            value = value[::-1].replace("-","",1)[::-1]
            airTemperature.set(value)
        if value.count(".")>1:
            value = value.replace(".","",1)
            airTemperature.set(value)
        if (value.isnumeric() and ((len(value) <= 5 and airTemperature.get()[:1] == "-") or (len(value) <= 4))):
            pass
        elif (value.isnumeric() == False and ((len(value) <= 5 and airTemperature.get()[:1] == "-") or (len(value) <= 4))):
            airTemperature.set(re.sub('[^0.-9-]',"",value,flags=re.IGNORECASE))
        else:
            airTemperature.set(re.sub('[^0.-9-]',"",value,flags=re.IGNORECASE)[0:-1])
        Json_Save(source=0,newEntry={"airTemperature" : float(airTemperature.get())})
    else:
        Json_Save(source=0,newEntry={"airTemperature" : 0.0})
    LabelBold(temperatureLabel,"airTemperature")
    boldLables["airTemperature"] = False

def HumidityEntryValidate(*args):
    value = (str(airHumidity.get()))
    if str(airHumidity.get()) != "":
        if value.count(".")>1:
            value = value.replace(".","",1)
            airHumidity.set(value)
        if (value.isnumeric() and (len(value) <= 4 )):
            pass
        elif (value.isnumeric() is False and (len(value) <= 4 )):
            airHumidity.set(re.sub('[^0.-9]',"",value,flags=re.IGNORECASE))
        else:
            airHumidity.set(re.sub('[^0.-9]',"",value,flags=re.IGNORECASE)[0:-1])
        Json_Save(source=0,newEntry={"airHumidity" : float(airHumidity.get())})
    else:
        Json_Save(source=0,newEntry={"airHumidity" : 0.0})
    LabelBold(humidityLabel,stringvar="airHumidity")
    boldLables["airHumidity"] = False

def PressureEntryValidate(*args):
    value = (str(airPressure.get()))
    if str(airPressure.get()) != "":
        if value.count(".")>1:
            value = value.replace(".","",1)
            airPressure.set(value)
        if (value.isnumeric() and (len(value) <= 7 )):
            pass
        elif (value.isnumeric() is False and (len(value) <= 7 )):
            airPressure.set(re.sub('[^0.-9]',"",value,flags=re.IGNORECASE))
        else:
            airPressure.set(re.sub('[^0.-9]',"",value,flags=re.IGNORECASE)[0:-1])
        Json_Save(source=0,newEntry={"airPressure" : float(airPressure.get())})
    else:
        Json_Save(source=0,newEntry={"airPressure" : float(0.0)})
    LabelBold(pressureLabel,stringvar="airPressure")
    boldLables["airPressure"] = False

def DirectionEntryValidate(*args):
    value = (str(windDirection.get()))
    if str(windDirection.get()) != "":
        if (value.isnumeric() and (len(value) <= 3 )):
            pass
        elif (value.isnumeric() is False and (len(value) <= 3 )):
            windDirection.set(re.sub('[^0-9]',"",value,flags=re.IGNORECASE))
        else:
            windDirection.set(re.sub('[^0-9]',"",value,flags=re.IGNORECASE)[0:-1])
        if (float(value) > 360.0):
            windDirection.set(0.0)
        Json_Save(source=0,newEntry={"windDirection" : float(windDirection.get())})
    else:
        Json_Save(source=0,newEntry={"windDirection" : 0.0})
    LabelBold(directionLabel,stringvar="windDirection")
    boldLables["windDirection"] = False

def MagnitudeEntryValidate(*args):
    value = (str(windMagnitude.get()))
    if str(windMagnitude.get()) != "":
        if value.count(".")>1:
            value = value.replace(".","",1)
            windMagnitude.set(value)
        if (value.isnumeric() and (len(value) <= 4 )):
            pass
        elif (value.isnumeric() is False and (len(value) <= 4 )):
            windMagnitude.set(re.sub('[^0.-9]',"",value,flags=re.IGNORECASE))
        else:
            windMagnitude.set(windMagnitude.get()[0:-1])
        Json_Save(source=0,newEntry={"windMagnitude" : float(windMagnitude.get())})
    else:
        Json_Save(source=0,newEntry={"windMagnitude" : 0.0})
    LabelBold(magnitudeLabel,stringvar="windMagnitude")
    boldLables["windMagnitude"] = False

def FriendliesUpdate(jsonKeys):
    try: friendlyNameCombobox["values"] = list(jsonKeys)
    except KeyError: pass
    except Exception as e:
        StatusMessageErrorDump(e, errorMessage="Failed to Load friendlies from JSON")

def FriendlyHeightAutoFill(event):
    if event.keysym=="Return" or event.keysym=="Tab":
        if len(friendlyPosX.get())>=4 and len(friendlyPosX.get())<=5 and len(friendlyPosY.get())>=4 and len(friendlyPosY.get())<=5:
            if len(friendlyPosX.get()) == 4:
                x = friendlyPosX.get()+"0"
            elif len(friendlyPosX.get()) == 5:
                x = friendlyPosX.get()
            if len(friendlyPosY.get()) == 4:
                y = friendlyPosY.get()+"0"
            elif len(friendlyPosY.get()) == 5:
                y = friendlyPosY.get()
            if int(x) > maxRow:
                x = maxRow-1
            elif int(x) < 0:
                x = 0
            if int(y) > maxCol:
                y = maxCol-1
            elif int(y) < 0:
                y = 0  
            try:
                friendlyHeight.set(terrainHeightMap.iat[int(x),int(y)])
            except:
                pass

def TargetHeightAutoFill(event):
        if event.keysym=="Return" or event.keysym=="Tab":
            if len(targetPosX.get())>=4 and len(targetPosX.get())<=5 and len(targetPosY.get())>=4 and len(targetPosY.get())<=5:
                if len(targetPosX.get()) == 4:
                    x = targetPosX.get()+"0"
                elif len(targetPosX.get()) == 5:
                    x = targetPosX.get()
                if len(targetPosY.get()) == 4:
                    y = targetPosY.get()+"0"
                elif len(targetPosY.get()) == 5:
                    y = targetPosY.get()

                if int(x) > maxRow:
                    x = maxRow-1
                elif int(x) < 0:
                    x = 0
                if int(y) > maxCol:
                    y = maxCol-1
                elif int(y) < 0:
                    y = 0    
                try:
                    targetHeight.set(terrainHeightMap.iat[int(x),int(y)])
                except:
                    pass

def FriendlyPositionAddUpdate():
    try:
        if len(friendlyPosX.get()) in (4,5) and len(friendlyPosY.get()) in (4,5) and friendlyPosX.get().isdigit() and friendlyPosY.get().isdigit() and all(not var for var in (friendlyName.get().isspace(),friendlyHeight.get().isspace(),friendlyHeight.get().isalpha())):
            dispersion = float(friendlyDispersion.get()) if friendlyDispersion.get() != "" else 0.0
            newPos = {
                friendlyName.get() : {
                    "GridX" : friendlyPosX.get(),
                    "GridY" : friendlyPosY.get(),
                    "Height" : friendlyHeight.get(),
                    "Dispersion" : dispersion,
                }
            }
            try: Json_Load(2)[friendlyName.get()]
            except KeyError: StatusMessageLog(message=f"{friendlyName.get()} has been added at position {friendlyPosX.get()}, {friendlyPosY.get()} at {friendlyHeight.get()} m")
            else: StatusMessageLog(message=f"{friendlyName.get()} has been updated, position {friendlyPosX.get()}, {friendlyPosY.get()} at {friendlyHeight.get()} m")
            Json_Save(2,newPos)
            UpdateSync(2)
            LabelBold(friendlyNameLabel,"Normal","friendlyName")
            boldLables["friendlyName"] = False
    except Exception as e:
        StatusMessageErrorDump(e,errorMessage="Failed to Add/Update Friendly position")

def FriendlyPositionRemove(*args,name):
    if name != "":
        try:
            Json_Delete(source=2,deleteKey=name)
        except KeyError: StatusMessageLog(message="Failed to delete friendly position")
        except Exception as e: StatusMessageErrorDump(e,errorMessage="Failed to delete friendly position")
        else:
            StatusMessageLog(message=name + " has been deleted")
        UpdateSync(2)
                
def TargetXYLRfpfChange(*args):
    global previousMissionEffect
    if xylrfpf.get() == "0":
        fireMissionEffect.set(previousMissionEffect)
        targetInputReferenceEntry.grid(sticky="NW")
    elif xylrfpf.get() == "2":
        targetInputReferenceEntry.grid(sticky="SW")
    else:
        fireMissionEffect.set(previousMissionEffect)
        targetInputReferenceEntry.grid(sticky="W")
    if xylrfpf.get() =="2":
        fireMissionEffect.set("FPF")
        if fireMissionSelectionLabelframe["text"] == "Fire Mission Selection":
            fireMissionSelectionEffectDestroyRadio.grid_remove()
            fireMissionSelectionEffectNeutraliseRadio.grid_remove()
            fireMissionSelectionEffectCheckRadio.grid_remove()
            fireMissionSelectionEffectSaturationRadio.grid_remove()
            fireMissionSelectionEffectAreaDenialRadio.grid_remove()
            fireMissionSelectionEffectSmokeRadio.grid_remove()
            fireMissionSelectionEffectIllumRadio.grid_remove()
            fireMissionSelectionEffectFPFRadio.grid()
    else:
            fireMissionSelectionEffectFPFRadio.grid_remove()
            fireMissionSelectionEffectDestroyRadio.grid()
            fireMissionSelectionEffectNeutraliseRadio.grid()
            fireMissionSelectionEffectCheckRadio.grid()
            fireMissionSelectionEffectSaturationRadio.grid()
            fireMissionSelectionEffectAreaDenialRadio.grid()
            fireMissionSelectionEffectSmokeRadio.grid()
            fireMissionSelectionEffectIllumRadio.grid()
            
def FireMissionEffectChange(*args):
    global previousMissionEffect
    if fireMissionEffect.get() != "FPF" and xylrfpf.get() != "2":
        previousMissionEffect = fireMissionEffect.get()

def FireMissionLengthChange(*args):
    if fireMissionLength.get().isnumeric()==True:
        fireMissionSelectionLengthUnitLabel["text"] = "s"
    else:
        fireMissionSelectionLengthUnitLabel["text"] = " "

def FireMissionConditionChange(*args):
    if fireMissionCondition.get() == "Time" or fireMissionCondition.get() == "time":
        fireMissionSelectionTimeLabelframe.grid()
        fireMissionHour.set(datetime.now().strftime("%H"))
        fireMissionMinute.set(datetime.now().strftime("%M"))
        fireMissionSecond.set(datetime.now().strftime("%S"))
    else:
        fireMissionSelectionTimeLabelframe.grid_remove()
def AddPairedMission():
    fireMissionSelectionPairedEffectSeriesRadio.grid_remove()

def PairedMissionChange(*args):
    if fireMissionPairedEffect.get() == "Creeping_Barrage":
        fireMissionSelectionPairedEffectCreepingLabelframe.grid()
    else:
        fireMissionSelectionPairedEffectCreepingLabelframe.grid_remove()

def LoadClockSettings():
    try:common = Json_Load(source=0,localOverride=True)
    except Exception as e: StatusMessageErrorDump(e,errorMessage="Failed to Load Common Json")
    try: clockSize.set(common["clockSize"])
    except: clockSize.set("400")
    try: clockRimWidth.set(common["clockRimWidth"])
    except: clockRimWidth.set("4")
    try: clockFontSize.set(common["clockFontSize"])
    except: clockFontSize.set("14")
    try: clockHandSize.set(common["clockHandSize"])
    except: clockHandSize.set("5")
    try: clockSecHandSize.set(common["clockSecHandSize"])
    except: clockSecHandSize.set("1")
    ClockApplySettings()
def ClockSettingsPopout():
    clockNotesNotebook.select(clockFrame)
    clockSettings = Toplevel(root)
    clockSettings.attributes("-topmost",True)
    clockSettings.title("Clock Settings")
    clockSettings.geometry("150x200+200+500")
    clockSettings.resizable(False,True)
    clockSettings.iconbitmap(exeDir/"Functions"/"clock.ico")
    clockSettingsWindow = clockSettings.winfo_toplevel()
    clockSettingsWindow.anchor("nw")
    clockSettingsWindow.grid_columnconfigure(0,weight=1)
    clockSettingsWindow.grid_rowconfigure(0,weight=1)
    clockSettingsFrame = ttk.Frame(clockSettingsWindow,padding=5,relief="groove")
    clockSettingSizeLabel = ttk.Label(clockSettingsFrame,text="Size")
    clockSettingRimWidthLabel = ttk.Label(clockSettingsFrame,text="Rim width")
    clockSettingFontSizeLabel = ttk.Label(clockSettingsFrame,text="Font size")
    clockSettingHandSizeLabel = ttk.Label(clockSettingsFrame,text="Hand Size")
    clockSettingSecHandSizeLabel = ttk.Label(clockSettingsFrame,text="Sec. Hand Size")
    clockSettingSeparator = ttk.Separator(clockSettingsFrame,orient="vertical")
    clockSettingSizeFrame = ttk.Frame(clockSettingsFrame,padding=0)
    clockSettingSizeFrame.grid_columnconfigure(0,minsize=10,weight=1)
    clockSettingSizeFrame.grid_columnconfigure(1,minsize=5)
    clockSettingSizeEntry = ttk.Entry(clockSettingSizeFrame,justify="left",textvariable=clockSize,width=5)
    clockSettingSizeEntry.bind("<Return>",lambda event:ClockApplySettings())
    clockSettingSizeUnitLabel = ttk.Label(clockSettingSizeFrame,text="Px")
    clockSettingRimFrame = ttk.Frame(clockSettingsFrame,padding=0)
    clockSettingRimFrame.grid_columnconfigure(0,minsize=10,weight=1)
    clockSettingRimFrame.grid_columnconfigure(1,minsize=5)
    clockSettingRimWidthEntry = ttk.Entry(clockSettingRimFrame,justify="left",textvariable=clockRimWidth,width=2)
    clockSettingRimWidthEntry.bind("<Return>",lambda event:ClockApplySettings())
    clockSettingRimUnitLabel = ttk.Label(clockSettingRimFrame,text="Px")
    clockSettingFontFrame = ttk.Frame(clockSettingsFrame,padding=0)
    clockSettingFontFrame.grid_columnconfigure(0,minsize=10,weight=1)
    clockSettingFontFrame.grid_columnconfigure(1,minsize=5)
    clockSettingFontSizeEntry = ttk.Entry(clockSettingFontFrame,justify="left",textvariable=clockFontSize,width=2)
    clockSettingFontSizeEntry.bind("<Return>",lambda event:ClockApplySettings())
    clockSettingFontUnitLabel = ttk.Label(clockSettingFontFrame,text="Px")
    clockSettingHandSizeFrame = ttk.Frame(clockSettingsFrame,padding=0)
    clockSettingHandSizeFrame.grid_columnconfigure(0,minsize=10,weight=1)
    clockSettingHandSizeFrame.grid_columnconfigure(1,minsize=5)
    clockSettingHandSizeEntry = ttk.Entry(clockSettingHandSizeFrame,justify="left",textvariable=clockHandSize,width=2)
    clockSettingHandSizeEntry.bind("<Return>",lambda event:ClockApplySettings())
    clockSettingHandSizeUnitLabel = ttk.Label(clockSettingHandSizeFrame,text="Px")
    clockSettingSecHandSizeFrame = ttk.Frame(clockSettingsFrame,padding=0)
    clockSettingSecHandSizeFrame.grid_columnconfigure(0,minsize=10,weight=1)
    clockSettingSecHandSizeFrame.grid_columnconfigure(1,minsize=5)
    clockSettingSecHandSizeEntry = ttk.Entry(clockSettingSecHandSizeFrame,justify="left",textvariable=clockSecHandSize,width=2)
    clockSettingSecHandSizeEntry.bind("<Return>",lambda event:ClockApplySettings())
    clockSettingSecHandSizeUnitLabel = ttk.Label(clockSettingSecHandSizeFrame,text="Px")
    clockSettingApplyButton = ttk.Button(clockSettingsFrame,text="Apply",command=ClockApplySettings)
    clockSettingsFrame.grid(column="0",row="0",sticky="NESW")
    clockSettingSizeLabel.grid(column="0",row="0",sticky="NE")
    clockSettingRimWidthLabel.grid(column="0",row="1",sticky="NE")
    clockSettingFontSizeLabel.grid(column="0",row="2",sticky="NE")
    clockSettingHandSizeLabel.grid(column="0",row="3",sticky="NE")
    clockSettingSecHandSizeLabel.grid(column="0",row="4",sticky="NE")
    clockSettingSeparator.grid(column="1",row="0",rowspan="5",sticky="NS")
    clockSettingSizeFrame.grid(column="2",row="0",sticky="NW",pady=4)
    clockSettingSizeEntry.grid(column="0",row="0",sticky="NW")
    clockSettingSizeUnitLabel.grid(column="1",row="0",sticky="SW")
    clockSettingRimFrame.grid(column="2",row="1",sticky="NW",pady=4)
    clockSettingRimWidthEntry.grid(column="0",row="0",sticky="NW")
    clockSettingRimUnitLabel.grid(column="1",row="0",sticky="SW")
    clockSettingFontFrame.grid(column="2",row="2",sticky="NW",pady=4)
    clockSettingFontSizeEntry.grid(column="0",row="0",sticky="NW")
    clockSettingFontUnitLabel.grid(column="1",row="0",sticky="SW")
    clockSettingHandSizeFrame.grid(column="2",row="3",sticky="NW",pady=4)
    clockSettingHandSizeEntry.grid(column="0",row="0",sticky="NW")
    clockSettingHandSizeUnitLabel.grid(column="1",row="0",sticky="SW")
    clockSettingSecHandSizeFrame.grid(column="2",row="4",sticky="NW",pady=4)
    clockSettingSecHandSizeEntry.grid(column="0",row="0",sticky="NW")
    clockSettingSecHandSizeUnitLabel.grid(column="1",row="0",sticky="SW")
    clockSettingApplyButton.grid(column="0",columnspan="3",row="5",sticky="NESW",pady="4")

def UpdateSync(setting = None):
    """
    Update settings common throughout the Unit, if setting

    0 : Common variables (temperature, windspeed/direction etc.)
    1 : IDFP positons
    2 : Friendly positions
    3 : Target positions and their specified missions
    4 : Calculated fire missions
    5 : Message Log (returns string)
    
    setting can be int, list of ints, or None
    """
    # Convert to list if needed
    if setting is None:
        settings_list = [0, 1, 2, 3, 4]
    elif isinstance(setting, list):
        settings_list = setting
    else:
        settings_list = [setting]
    
    def FetchJSON(setting):
        # This runs in background thread - NO GUI calls at all!
        results = {}
        
        try:
            if setting == 0:
                results['common'] = Json_Load(source=0)
            if setting == 1:
                results['idfp'] = Json_Load(source=1)
            if setting == 2:
                results['friend'] = Json_Load(source=2)
            if setting == 3:
                results['targets'] = Json_Load(source=3)##################SORT OUT TARGETS
            if setting == 4:
                results['fire mission'] = Json_Load(source=4)
        except Exception as e:
            results['error'] = f"Failed to load JSON: {str(e)}"
            StatusMessageErrorDump(e,errorMessage=f"Failed to load JSON: {str(e)}")
        # Put results in queue instead of calling root.after()
        update_queue.put(('process_results', results, setting))
    
    # Start background threads for all settings
    for s in settings_list:
        threading.Thread(target=lambda setting=s: FetchJSON(setting), daemon=True).start()
    
    root.after(5000,UpdateSync)

def ProcessResults(results, setting):
    # This runs on main thread - break up processing to avoid GUI freezing
    if 'error' in results:
        StatusMessageLog(results['error'])
        return
    
    def ProcessStep(step=0):
        if step == 0 and setting == 0 and 'common' in results:
            root.after(1, lambda: ProcessCommonSettings(results['common']))
        elif step == 1 and setting == 1 and 'idfp' in results:
            root.after(1, lambda: IDFPUpdate(list(results['idfp'].keys())))
        elif step == 2 and setting == 2 and 'friend' in results:
            root.after(1, lambda: FriendliesUpdate(list(results['friend'].keys())))
        elif step == 3 and setting == 3 and 'targets' in results:
            root.after(1, lambda: TargetsUpdate(results['targets']))
        elif step == 4 and setting == 4 and 'fire mission' in results:
            root.after(1, lambda: FireMissionLoadInfo(results['fire mission']))
    
    # Process the appropriate step
    ProcessStep(setting)

def ProcessCommonSettings(common):
    # This runs on main thread - break it up to avoid GUI freezing
    
    def UpdateSetting(stringVariable: StringVar, jsonName: str, settingName: str,trace,entryLabel):
        try:
            setting_value = common[jsonName]
        except ValueError:
            StatusMessageLog(f"{settingName} from JSON has an erroneous value")
            return
        except KeyError:
            StatusMessageLog(f"{settingName} key does not exist in JSON")
            Json_Save(0,newEntry={jsonName:""})
            return
        except Exception as e:
            StatusMessageErrorDump(e,errorMessage=f"Failed to load {settingName} from JSON")
            return
        try:       
            if stringVariable.get() != str(setting_value) and stringVariable!="":
                if jsonName == "system":
                    SystemChange(newSystem=setting_value)
                else:
                    if jsonName in boldLables.keys():
                        if boldLables[jsonName] == False:
                            UpdateStringVar(stringVariable, setting_value,trace)
                            if trace!=None:
                                if stringVariable == windDynamic:
                                    trace = windDynamic.trace_add(mode="write", callback=(lambda *args: Json_Save(source=0,newEntry={"windDynamic" : windDynamic.get()})))
                                if entryLabel!=None:
                                    trace = stringVariable.trace_add(mode="write",callback=lambda *args: LabelBold(entryLabel,"Bold",jsonName))
                                settings_to_process[jsonName]["traceName"] = trace
                    else:
                        UpdateStringVar(stringVariable, setting_value,trace)
                        if trace!=None:
                            if stringVariable == windDynamic:
                                trace = windDynamic.trace_add(mode="write", callback=(lambda *args: Json_Save(source=0,newEntry={"windDynamic" : windDynamic.get()})))
                            if entryLabel!=None:
                                trace = stringVariable.trace_add(mode="write",callback=lambda *args: LabelBold(entryLabel,"Bold",jsonName))
                            settings_to_process[jsonName]["traceName"] = trace
        except Exception as e:
            StatusMessageErrorDump(e,errorMessage=f"Failed to set {settingName}")
    
    # List of settings to process
    # settings_to_process = [
    #     (airTemperature, "airTemperature", "Air Temperature",airTemperatureTrace,temperatureLabel),
    #     (airHumidity, "airHumidity", "Air Humidity",airHumidityTrace,humidityLabel),
    #     (airPressure, "airPressure", "Air Pressure",airPressureTrace,pressureLabel),
    #     (windDirection, "windDirection", "Wind Direction",windDirectionTrace,directionLabel),
    #     (windMagnitude, "windMagnitude", "Wind Magnitude",windMagnitudeTrace,magnitudeLabel),
    #     (windDynamic, "windDynamic", "Dynamic Wind setting",None,None),
    #     (system, "system", "Weapon System",None,None)
    # ]
    
    
    # Process all settings with minimal delays
    for i, (jsonName, items) in enumerate(settings_to_process.items()):
        try:
            if boldLables[jsonName] == False:
                root.after(i*200, lambda sv=items["StringVar"], jn=jsonName, sn=items["settingName"],tr=items["traceName"],lbl=items["entryLabel"]: UpdateSetting(sv, jn, sn, tr, lbl))
        except KeyError:
            root.after(i*200, lambda sv=items["StringVar"], jn=jsonName, sn=items["settingName"],tr=items["traceName"],lbl=items["entryLabel"]: UpdateSetting(sv, jn, sn, tr, lbl))
def CheckUpdateQueue():
    """Check for updates from background threads and process them"""
    try:
        while True:
            task, *args = update_queue.get_nowait()
            
            if task == 'process_results':
                results, setting = args
                ProcessResults(results, setting)
                # Add other task types here if needed
    except queue.Empty:
        pass  # No updates to process
    except Exception as e: StatusMessageErrorDump(e,errorMessage=f"Failed to update iterative settings, queue size: {str(update_queue.qsize())}")
    root.after(200,CheckUpdateQueue)
    #FIRE MISSIONS


def Sort_FireMissions(items):
    def sort_key(item):
        segments = []
        for ch in item:
            if ch.isdigit():  # If the character is a digit
                segments.append((False, int(ch)))  # Treat it as a number
            else:  # If the character is not a digit (i.e., alphabetic)
                segments.append((True, ch))  # Treat it as text

        return segments  # The sorting key is now a list of (True/False, value)
    return sorted(items.keys(), key=sort_key)

def RequestEditFireMissionsFromSafety(*args):
    for target, (edit, calculate) in listCheckBox_vars["LR"].items(): edit.set(False)
    for target, (edit, calculate) in seriesDict["LR"].items(): edit.set(False)
    for target, (edit, calculate) in listCheckBox_vars["XY"].items(): edit.set(False)
    for target, (edit, calculate) in seriesDict["XY"].items(): edit.set(False)
    for target, (edit, calculate) in listCheckBox_vars["FPF"].items(): edit.set(False)
    for target, (edit, calculate) in seriesDict["FPF"].items(): edit.set(False)
    for target, (edit, calculate) in listCheckBox_vars["Combo"].items(): edit.set(False)
    for target, (edit, calculate) in seriesDict["Combo"].items(): edit.set(False)
    create_checkboxes(targetListLRCanvasFrame,{key: listCheckBox_vars["LR"][key] for key in Sort_FireMissions(listCheckBox_vars["LR"])},seriesDict["LR"])
    create_checkboxes(targetListXYCanvasFrame,{key: listCheckBox_vars["XY"][key] for key in Sort_FireMissions(listCheckBox_vars["XY"])},seriesDict["XY"])
    create_checkboxes(targetListFPFCanvasFrame,{key: listCheckBox_vars["FPF"][key] for key in Sort_FireMissions(listCheckBox_vars["FPF"])},seriesDict["FPF"])
    create_checkboxes(targetListComboCanvasFrame,{key: listCheckBox_vars["Combo"][key] for key in Sort_FireMissions(listCheckBox_vars["Combo"])},seriesDict["Combo"])
    RequestEditFireMissions()

def RequestEditFireMissions():
    global FPFEditSelected
    global previousMissionEffect
    editList = ""
    editCount = 0
    FPFEditSelected = False
    for target, (edit, calculate) in listCheckBox_vars["FPF"].items():
        if edit.get() == True:
            FPFEditSelected = True
    if FPFEditSelected == False:
        fireMissionEffect.set(previousMissionEffect)
        for target, (edit, calculate) in listCheckBox_vars["LR"].items():
            if edit.get() == True:
                editCount +=1
                editList += ("LR "+target + " | ")
        for target, (edit, calculate) in listCheckBox_vars["XY"].items():
            if edit.get() == True:
                editCount +=1
                editList += ("XY "+target + " | ")
        for target, (edit, calculate) in listCheckBox_vars["Combo"].items():
            if edit.get() == True:
                editCount +=1
                editList += ("Combo "+target + " | ")
        create_checkboxes(targetListLRCanvasFrame,{key: listCheckBox_vars["LR"][key] for key in Sort_FireMissions(listCheckBox_vars["LR"])},seriesDict["LR"])
        create_checkboxes(targetListXYCanvasFrame,{key: listCheckBox_vars["XY"][key] for key in Sort_FireMissions(listCheckBox_vars["XY"])},seriesDict["XY"])
        create_checkboxes(targetListFPFCanvasFrame,{key: listCheckBox_vars["FPF"][key] for key in Sort_FireMissions(listCheckBox_vars["FPF"])},seriesDict["FPF"],True)
        create_checkboxes(targetListComboCanvasFrame,{key: listCheckBox_vars["Combo"][key] for key in Sort_FireMissions(listCheckBox_vars["Combo"])},seriesDict["Combo"])
        if xylrfpf.get() !="2":
            fireMissionSelectionEffectFPFRadio.grid_remove()
            fireMissionSelectionEffectDestroyRadio.grid()
            fireMissionSelectionEffectNeutraliseRadio.grid()
            fireMissionSelectionEffectCheckRadio.grid()
            fireMissionSelectionEffectSaturationRadio.grid()
            fireMissionSelectionEffectAreaDenialRadio.grid()
            fireMissionSelectionEffectSmokeRadio.grid()
            fireMissionSelectionEffectIllumRadio.grid()
    else:
        fireMissionEffect.set("FPF")
        for target, (edit, calculate) in listCheckBox_vars["FPF"].items():
            if edit.get() == True:
                editCount +=1
                editList += ("FPF "+target + " | ")
        for target, (edit, calculate) in listCheckBox_vars["LR"].items():
            edit.set(False)
        for target, (edit, calculate) in seriesDict["LR"].items():
            edit.set(False)
        for target, (edit, calculate) in listCheckBox_vars["XY"].items():
            edit.set(False)
        for target, (edit, calculate) in seriesDict["XY"].items():
            edit.set(False)
        for target, (edit, calculate) in listCheckBox_vars["Combo"].items():
            edit.set(False)
        for target, (edit, calculate) in seriesDict["Combo"].items():
            edit.set(False)
        create_checkboxes(targetListLRCanvasFrame,{key: listCheckBox_vars["LR"][key] for key in Sort_FireMissions(listCheckBox_vars["LR"])},seriesDict["LR"])
        create_checkboxes(targetListXYCanvasFrame,{key: listCheckBox_vars["XY"][key] for key in Sort_FireMissions(listCheckBox_vars["XY"])},seriesDict["XY"])
        create_checkboxes(targetListFPFCanvasFrame,{key: listCheckBox_vars["FPF"][key] for key in Sort_FireMissions(listCheckBox_vars["FPF"])},seriesDict["FPF"],True)
        create_checkboxes(targetListComboCanvasFrame,{key: listCheckBox_vars["Combo"][key] for key in Sort_FireMissions(listCheckBox_vars["Combo"])},seriesDict["Combo"])
        fireMissionSelectionEffectDestroyRadio.grid_remove()
        fireMissionSelectionEffectNeutraliseRadio.grid_remove()
        fireMissionSelectionEffectCheckRadio.grid_remove()
        fireMissionSelectionEffectSaturationRadio.grid_remove()
        fireMissionSelectionEffectAreaDenialRadio.grid_remove()
        fireMissionSelectionEffectSmokeRadio.grid_remove()
        fireMissionSelectionEffectIllumRadio.grid_remove()
        fireMissionSelectionEffectFPFRadio.grid()
    if editList == "":
        fireMissionSelectionLabelframe["text"] = "Fire Mission Selection"
        if xylrfpf.get() =="2":
            fireMissionSelectionEffectDestroyRadio.grid_remove()
            fireMissionSelectionEffectNeutraliseRadio.grid_remove()
            fireMissionSelectionEffectCheckRadio.grid_remove()
            fireMissionSelectionEffectSaturationRadio.grid_remove()
            fireMissionSelectionEffectAreaDenialRadio.grid_remove()
            fireMissionSelectionEffectSmokeRadio.grid_remove()
            fireMissionSelectionEffectIllumRadio.grid_remove()
            fireMissionSelectionEffectFPFRadio.grid()
        else:
            fireMissionSelectionEffectFPFRadio.grid_remove()
            fireMissionSelectionEffectDestroyRadio.grid()
            fireMissionSelectionEffectNeutraliseRadio.grid()
            fireMissionSelectionEffectCheckRadio.grid()
            fireMissionSelectionEffectSaturationRadio.grid()
            fireMissionSelectionEffectAreaDenialRadio.grid()
            fireMissionSelectionEffectSmokeRadio.grid()
            fireMissionSelectionEffectIllumRadio.grid()
        fireMissionSelectionUpdateMission.grid_remove()
    else:
        fireMissionSelectionLabelframe["text"] = editList + "Edit missions"
        fireMissionSelectionUpdateMission.grid()
        if editCount == 1:
            FireMissionEdit()

def FireMissionEdit(*args):
    def PasteSettings(prefix,target,targets):
        fireMissionEffect.set(targets[prefix][target]["Effect"])
        fireMissionWidth.set(str(int(float(targets[prefix][target]["Width"])*2)))
        fireMissionDepth.set(str(int(float(targets[prefix][target]["Depth"])*2)))
        fireMissionLength.set(targets[prefix][target]["Length"])
        fireMissionCondition.set(targets[prefix][target]["Condition"])
        fireMissionHour.set(targets[prefix][target]["Time"]["Hour"])
        fireMissionMinute.set(targets[prefix][target]["Time"]["Minute"])
        fireMissionSecond.set(targets[prefix][target]["Time"]["Second"])
    targets = Json_Load(source=3)
    for target, (edit, calculate) in listCheckBox_vars["LR"].items():
        if edit.get() == True:
            PasteSettings("LR",target,targets)

    for target, (edit, calculate) in listCheckBox_vars["XY"].items():
        if edit.get() == True:
            PasteSettings("XY",target,targets)

    for target, (edit, calculate) in listCheckBox_vars["FPF"].items():
        if edit.get() == True:
            PasteSettings("FPF",target,targets)

def FireMissionEffectUpdate(*args):
    editedFireMission = ""
    def SaveSettings(prefix,target,targets,fireMissions):
        mutator = "None"
        orientation = "None"
        if fireMissionWidth.get() != "0" and fireMissionWidth.get() != "" and fireMissionDepth.get() != "0" and fireMissionDepth.get() != "":
            try:
                int(fireMissionWidth.get())
                int(fireMissionDepth.get())
                mutator = "Box"
            except ValueError:
                try: int(fireMissionWidth.get())
                except: StatusMessageLog(message="Incorrect Width dispersion, defaulting to no diserpsion")
                try: int(fireMissionDepth.get())
                except: StatusMessageLog(message="Incorrect Depth dispersion, defaulting to no diserpsion")
            except Exception as e:
                StatusMessageErrorDump(e,errorMessage="Failed to Update fire mission due to width/depth")
                return
        elif fireMissionDepth.get() != "0" and fireMissionDepth.get() != "":
            try:
                int(fireMissionDepth.get())
                mutator = "Line"
                orientation = "Vertical"
            except ValueError: StatusMessageLog(message="Incorrect Depth dispersion, defaulting to no diserpsion")
            except Exception as e:
                StatusMessageErrorDump(e,errorMessage="Failed to Update fire mission due to depth")
                return
        elif fireMissionWidth.get() != "0" and fireMissionWidth.get() != "":
            try:
                int(fireMissionWidth.get())
                mutator = "Line"
                orientation = "Horizontal"
            except ValueError: StatusMessageLog(message="Incorrect Width dispersion, defaulting to no diserpsion")
            except Exception as e:
                StatusMessageErrorDump(e,errorMessage="Failed to Update fire mission due to width/depth")
                return
        changeFiremission = (int(float(targets[prefix][target]["Width"])*2) == int(fireMissionWidth.get()) and
                             int(float(targets[prefix][target]["Depth"])*2) == int(fireMissionDepth.get()))
        if changeFiremission: 
           for idfp,missions in list(fireMissions.items()):
                if f"{prefix}-{target}" in missions.keys():
                    fireMissions[idfp][f"{prefix}-{target}"]["Effect"] = fireMissionEffect.get()
                    fireMissions[idfp][f"{prefix}-{target}"]["Length"] = fireMissionLength.get()
                    fireMissions[idfp][f"{prefix}-{target}"]["Condition"] = fireMissionCondition.get()
                    if fireMissionCondition.get() == "Time":
                        fireMissions[idfp][f"{prefix}-{target}"]["Time"] = {
                            "Hour": int(fireMissionHour.get()),
                            "Minute": int(fireMissionMinute.get()),
                            "Second": int(fireMissionSecond.get())
                            }
                    elif fireMissionCondition.get() != "Time":
                        fireMissions[idfp][f"{prefix}-{target}"].pop("Time",None)
        else:
            StatusMessageLog(message=f"{prefix}-{target} requires recalculation to change dispersion")
        targets[prefix][target]["Effect"] = fireMissionEffect.get()
        targets[prefix][target]["Width"] = int(fireMissionWidth.get())/2
        targets[prefix][target]["Depth"] = int(fireMissionDepth.get())/2
        targets[prefix][target]["Length"] = fireMissionLength.get()
        targets[prefix][target]["Condition"] = fireMissionCondition.get()
        targets[prefix][target]["Mutator"] = mutator
        targets[prefix][target]["Orientation"] = orientation
        targets[prefix][target]["Time"]["Hour"] = int(fireMissionHour.get())
        targets[prefix][target]["Time"]["Minute"] = int(fireMissionMinute.get())
        targets[prefix][target]["Time"]["Second"] = int(fireMissionSecond.get())
        return targets,fireMissions
        
    targets = Json_Load(source=3)
    fireMissions = Json_Load(source=4)
    for target, (edit, calculate) in listCheckBox_vars["LR"].items():
        if edit.get() == True:
            targets,fireMissions = SaveSettings("LR",target,targets,fireMissions)
            editedFireMission += (str("LR")+"-"+str(target)+", ")

    for target, (edit, calculate) in listCheckBox_vars["XY"].items():
        if edit.get() == True:
            targets,fireMissions = SaveSettings("XY",target,targets,fireMissions)
            editedFireMission += (str("XY")+"-"+str(target)+", ")

    for target, (edit, calculate) in listCheckBox_vars["FPF"].items():
        if edit.get() == True:
            targets,fireMissions = SaveSettings("FPF",target,targets,fireMissions)
            editedFireMission += (str("FPF")+"-"+str(target)+", ")
    try:
        Json_Save(source=3,newEntry=targets)
        StatusMessageLog(message=f"Updated Targets {editedFireMission[:-2]}")
    except Exception as e:
        StatusMessageErrorDump(e, errorMessage="Failed to update targets")
    try:
        Json_Save(source=4,newEntry=fireMissions)
        StatusMessageLog(message=f"Updated fire missions {editedFireMission[:-2]}")
    except Exception as e:
        StatusMessageErrorDump(e, errorMessage="Failed to update fire missions")

def SelectBelow(checkbox,frame,Checkbox_vars):
    focusedWidget = frame.focus_get()
    grid_info = focusedWidget.grid_info()
    focused_row = grid_info.get("row")
    selection=""
    for widget in frame.winfo_children():
        if widget.grid_info().get("row")==focused_row and type(widget) == ttk.Label:
            selection = widget["text"]
    for item, (var1, var2) in Checkbox_vars.items():
        if item[:1] == selection and root.tk.getboolean(root.tk.globalgetvar(focusedWidget.cget("variable"))) == True:
            if checkbox == 1:
                var1.set(True)
            elif checkbox == 2:
                var2.set(True)
        if item[:1] == selection and root.tk.getboolean(root.tk.globalgetvar(focusedWidget.cget("variable"))) == False:
            if checkbox == 1:
                var1.set(False)
            elif checkbox == 2:
                var2.set(False)
    if checkbox == 1:
        RequestEditFireMissions()

def on_mouse_enter(event):
    widget: Widget = event.widget
    grid_info = widget.grid_info()
    focused_row = grid_info.get("row")
    check = True
    try:
        for widg in root.nametowidget(widget.winfo_parent()).winfo_children():
            if widg.grid_info().get("row") == focused_row:
                if type(widg) == ttk.Label:
                    labelframe = root.nametowidget(root.nametowidget(root.nametowidget(widget.winfo_parent()).winfo_parent()).winfo_parent())
                    if labelframe["text"] == "LR":
                        statusReferenceLabel["text"] = "LR-"+ widg["text"]
                        statusGridLabel["text"] = targetList["LR"][widg["text"]]["GridX"]+","+ targetList["LR"][widg["text"]]["GridY"]
                        statusHeightLabel["text"] = targetList["LR"][widg["text"]]["Height"]
                    if labelframe["text"] == "XY":
                        statusReferenceLabel["text"] = "XY-"+ widg["text"]
                        statusGridLabel["text"] = targetList["XY"][widg["text"]]["GridX"]+","+ targetList["XY"][widg["text"]]["GridY"]
                        statusHeightLabel["text"] = targetList["XY"][widg["text"]]["Height"]
                    if labelframe["text"] == "FPF":
                        statusReferenceLabel["text"] = "FPF-"+widg["text"]
                        statusGridLabel["text"] = targetList["FPF"][widg["text"]]["GridX"]+","+ targetList["FPF"][widg["text"]]["GridY"]
                        statusHeightLabel["text"] = targetList["FPF"][widg["text"]]["Height"]
                    if labelframe["text"] == "Combo":
                        statusReferenceLabel["text"] = widg["text"]
                        statusGridLabel["text"] = targetList["Combo"][widg["text"]]["GridX"]+","+ targetList["Combo"][widg["text"]]["GridY"]
                        statusHeightLabel["text"] = targetList["Combo"][widg["text"]]["Height"]
    except:StatusMessageLog(message="",privateMessage="Unable to display target details on the status bar")

def create_checkboxes(frame: ttk.Frame, Checkbox_vars,seriesDict,FPFSelection = False):
    def ShowContextMenu(event,widget: Widget):
        text = widget.cget("text") if widget.winfo_exists() else None
        targetContextMenu.delete(0,END)
        prefix = frame.master.master.cget("text")
        targetContextMenu.add_command(label="Copy Grid",command=lambda w=widget,t=text,p=prefix: CopyGrid(w,t,p))
        targetContextMenu.add_command(label="Clock Splash Offset",command=lambda w=widget,t=text,p=prefix: ClockSplashOffset(w,t,p))
        targetContextMenu.add_command(label="Delete Fire mission",command=lambda: ClearFireMission(mission=prefix,name=text,calculated=True))
        targetContextMenu.post(event.x_root,event.y_root)
    def CopyGrid(widget: Widget,text,prefix):
        try:
            if widget.winfo_exists():
                grid = Json_Load(source=3)[prefix][widget.cget("text")]["GridX"]+Json_Load(source=3)[prefix][widget.cget("text")]["GridY"]
                pyperclip.copy(grid)
                text = widget.cget("text")
            else:
                grid = Json_Load(source=3)[prefix][text]["GridX"]+Json_Load(source=3)[prefix][text]["GridY"]
                pyperclip.copy(grid)
            StatusMessageLog(privateMessage=f"Copied {prefix}-{text} grid {grid} to clipboard")
        except Exception as e:
            StatusMessageErrorDump(e,errorMessage=f"Failed to copy grid from {prefix}-{text}")
    def ClockSplashOffset(widget: Widget,text,prefix):
        global clockHandOffset
        try:
            if widget.winfo_exists():
                clockHandOffset = (float(Json_Load(source=4)[idfpNotebook.tab(idfpNotebook.select(),"text")][prefix+"-"+widget.cget("text")]["TOF"]))
                clockOffset.set(f"{prefix}-{widget.cget("text")}")
            else:
                clockHandOffset = (float(Json_Load(source=4)[idfpNotebook.tab(idfpNotebook.select(),"text")][text]["TOF"]))
                clockOffset.set(text)
        except KeyError: StatusMessageLog(message=f"Calculated Fire Mission {prefix}-{text} is not found or calculated")
        except Exception as e: StatusMessageErrorDump(e,errorMessage=f"Failed to send Clock splash offset from {prefix}-{text}")
    targetContextMenu = Menu(root,tearoff=False)
    global FPFEditSelected
    for widget in frame.winfo_children():
        widget.destroy()
    series = []
    for key in Checkbox_vars.keys():
        series.append(str(key)[:1])
    row = 0
    currentSeries = ""
    for item, (var1, var2) in Checkbox_vars.items():
        if series.count(item[:1]) ==1:
            sep = ttk.Separator(frame,orient="horizontal")
            sep.grid(row=row,column=0,columnspan=5,sticky="WE",pady="4")
            row+=1
            if fmEditSafetyToggle.get() == "1":
                chk1 = ttk.Checkbutton(frame, variable=var1,command=RequestEditFireMissions,state="disabled")
            elif FPFSelection == False and FPFEditSelected ==True:
                chk1 = ttk.Checkbutton(frame, variable=var1,command=RequestEditFireMissions,state="disabled")
            else:
                chk1 = ttk.Checkbutton(frame, variable=var1,command=RequestEditFireMissions,state="normal")
            chk1.bind("<Enter>",on_mouse_enter)
            chk2 = ttk.Checkbutton(frame, variable=var2)
            chk2.bind("<Enter>",on_mouse_enter)
            lbl = ttk.Label(frame,text=item)
            lbl.bind("<Enter>",on_mouse_enter)
            lbl.bind("<Button-3>",lambda event,widget=lbl: ShowContextMenu(event,widget))
            chk1.grid(row=row,column=0,padx=0,pady=0,sticky="w")
            chk2.grid(row=row,column=1,padx=0,pady=0,sticky="w")
            lbl.grid(row=row,column=2,columnspan=3,padx=0,pady=0,sticky="w")
            row += 1
        else:
            if currentSeries != item[:1]:
                currentSeries = item[:1]
                sep = ttk.Separator(frame,orient="horizontal")
                sep.grid(row=row,column=0,columnspan=5,sticky="WE",pady="4")
                row+=1
                try:
                    if fmEditSafetyToggle.get() == "1":
                        but1 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][0],command=lambda *args: SelectBelow(1,frame,Checkbox_vars),state="disabled")
                    elif FPFSelection == False and FPFEditSelected ==True:
                        but1 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][0],command=lambda *args: SelectBelow(1,frame,Checkbox_vars),state="disabled")
                    else:
                        but1 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][0],command=lambda *args: SelectBelow(1,frame,Checkbox_vars),state="normal")
                except:
                    seriesDict[item[:1]] = (BooleanVar(),BooleanVar())
                    if fmEditSafetyToggle.get() == "1":
                        but1 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][0],command=lambda *args: SelectBelow(1,frame,Checkbox_vars),state="disabled")
                    elif FPFSelection == False and FPFEditSelected ==True:
                        but1 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][0],command=lambda *args: SelectBelow(1,frame,Checkbox_vars),state="disabled")
                    else:
                        but1 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][0],command=lambda *args: SelectBelow(1,frame,Checkbox_vars),state="normal")
                but2 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][1],command=lambda *args: SelectBelow(2,frame,Checkbox_vars))
                lblS = ttk.Label(frame,text=item[:1])
                but1.grid(row=row,column=0,padx=0,pady=0,sticky="w")
                but2.grid(row=row,column=1,padx=0,pady=0,sticky="w")
                lblS.grid(row=row,column=2,padx=0,pady=0,sticky="w")
                row += 1
                sep = ttk.Separator(frame,orient="vertical")
                sep.grid(row=row,column=1,rowspan=series.count(item[:1]),sticky="NES")
            if fmEditSafetyToggle.get() == "1":
                chk1 = ttk.Checkbutton(frame, variable=var1,command=RequestEditFireMissions,state="disabled")
            elif FPFSelection == False and FPFEditSelected ==True:
                chk1 = ttk.Checkbutton(frame, variable=var1,command=RequestEditFireMissions,state="disabled")
            else:
                chk1 = ttk.Checkbutton(frame, variable=var1,command=RequestEditFireMissions,state="normal")
            chk1.bind("<Enter>",on_mouse_enter)
            chk2 = ttk.Checkbutton(frame, variable=var2)
            chk2.bind("<Enter>",on_mouse_enter)
            lbl = ttk.Label(frame,text=item)
            lbl.bind("<Enter>",on_mouse_enter)
            lbl.bind("<Button-3>",lambda event,widget=lbl: ShowContextMenu(event,widget))
            chk1.grid(row=row,column=2,padx=0,pady=0,sticky="w")
            chk2.grid(row=row,column=3,padx=0,pady=0,sticky="w")
            lbl.grid(row=row,column=4,padx=0,pady=0,sticky="w")
            row += 1
        if currentSeries != item[:1]:
            currentSeries = item[:1]
    return Checkbox_vars

def TargetsUpdate(targetJSON):
    global targetList
    targetList = targetJSON
    for mission, targets in list(targetJSON.items()):
        if mission == "FPF":
            prefix = "FPF"
            canvas = targetListFPFCanvas
            canvasFrame = targetListFPFCanvasFrame
        elif mission == "LR":
            prefix = "LR"
            canvas = targetListLRCanvas
            canvasFrame = targetListLRCanvasFrame
        elif mission == "XY":
            prefix = "XY"
            canvas = targetListXYCanvas
            canvasFrame = targetListXYCanvasFrame
        elif mission == "Combo":
            prefix = "Combo"
            canvas = targetListComboCanvas
            canvasFrame = targetListComboCanvasFrame
        for target in list(targets.keys()):
            if target not in listCheckBox_vars[prefix]:
                try:
                    listCheckBox_vars[prefix][target]
                except KeyError:
                    listCheckBox_vars[prefix][target] = (BooleanVar(),BooleanVar())
                    sorted_items = Sort_FireMissions(listCheckBox_vars[prefix])
                    create_checkboxes(canvasFrame,{key: listCheckBox_vars[prefix][key] for key in sorted_items},seriesDict[prefix])
                    update_scrollregion(canvasFrame,canvas)
    for mission, targets in listCheckBox_vars.items():
        if mission == "FPF":
            prefix = "FPF"
            canvas = targetListFPFCanvas
            canvasFrame = targetListFPFCanvasFrame
        elif mission == "LR":
            prefix = "LR"
            canvas = targetListLRCanvas
            canvasFrame = targetListLRCanvasFrame
        elif mission == "XY":
            prefix = "XY"
            canvas = targetListXYCanvas
            canvasFrame = targetListXYCanvasFrame
        elif mission == "Combo":
            prefix = "Combo"
            canvas = targetListComboCanvas
            canvasFrame = targetListComboCanvasFrame
        for target in list(targets.keys()):
            try: targetJSON[mission][target]
            except KeyError:
                listCheckBox_vars[mission].pop(target,None)
                for delSeries in [digit for digit in list(seriesDict[mission].keys()) if Counter(key[:1] for key in listCheckBox_vars[mission].keys()).get(digit,0) <= 1]:
                    seriesDict[mission].pop(delSeries,None)
                sorted_items = Sort_FireMissions(listCheckBox_vars[prefix])
                create_checkboxes(canvasFrame,{key: listCheckBox_vars[prefix][key] for key in sorted_items},seriesDict[prefix])
                update_scrollregion(canvasFrame,canvas)

def TargetAdd():
    new_item = targetReference.get().strip()
    if len(new_item)==2 or len(new_item)==3:
        if xylrfpf.get() == "0":
            prefix = "LR"
        elif xylrfpf.get() == "1":
            prefix = "XY"
        elif xylrfpf.get() == "2":
            prefix = "FPF"
        if new_item and new_item not in listCheckBox_vars[prefix]:
            listCheckBox_vars[prefix][new_item] = (BooleanVar(),BooleanVar())
            sorted_items = Sort_FireMissions(listCheckBox_vars[prefix])
            if prefix == "LR":
                create_checkboxes(targetListLRCanvasFrame,{key: listCheckBox_vars[prefix][key] for key in sorted_items},seriesDict[prefix])
            if prefix == "XY":
                create_checkboxes(targetListXYCanvasFrame,{key: listCheckBox_vars[prefix][key] for key in sorted_items},seriesDict[prefix])    
            if prefix == "FPF":
                create_checkboxes(targetListFPFCanvasFrame,{key: listCheckBox_vars[prefix][key] for key in sorted_items},seriesDict[prefix])
            newTarget = {}
            try: newTarget[prefix] = Json_Load(3)[prefix]
            except KeyError: newTarget = {prefix : {}}
            try: targetList[prefix]
            except: targetList[prefix] = {}
            mutator = "None"
            orientation = "None"
            if fireMissionWidth.get() != "0" and fireMissionWidth.get() != "" and fireMissionDepth.get() != "0" and fireMissionDepth.get() != "":
                try:
                    int(fireMissionWidth.get())
                    int(fireMissionDepth.get())
                    mutator = "Box"
                except:
                    try: int(fireMissionWidth.get())
                    except ValueError: StatusMessageLog(message="Incorrect Width dispersion, defaulting to no diserpsion")
                    except Exception as e: StatusMessageErrorDump(e,errorMessage="Incorrect Width dispersion, defaulting to no diserpsion")
                    try: int(fireMissionDepth.get())
                    except ValueError: StatusMessageLog(message="Incorrect Depth dispersion, defaulting to no diserpsion")
                    except Exception as e: StatusMessageErrorDump(e,errorMessage="Incorrect Depth dispersion, defaulting to no diserpsion")
            elif fireMissionDepth.get() != "0" and fireMissionDepth.get() != "":
                try:
                    int(fireMissionDepth.get())
                    mutator = "Line"
                    orientation = "Vertical"
                except ValueError: StatusMessageLog(message="Incorrect Depth dispersion, defaulting to no diserpsion")
                except Exception as e: StatusMessageErrorDump(e,errorMessage="Incorrect Depth dispersion, defaulting to no diserpsion")
            elif fireMissionWidth.get() != "0" and fireMissionWidth.get() != "":
                try:
                    int(fireMissionWidth.get())
                    mutator = "Line"
                    orientation = "Horizontal"
                except ValueError: StatusMessageLog(message="Incorrect Width dispersion, defaulting to no diserpsion")
                except Exception as e: StatusMessageErrorDump(e,errorMessage="Incorrect Width dispersion, defaulting to no diserpsion")
            targetList[prefix][new_item]= {
                "GridX" : targetPosX.get(),
                "GridY" : targetPosY.get(),
                "Height" : float(targetHeight.get()),
                "Effect" : fireMissionEffect.get(),
                "Width" : int(fireMissionWidth.get())/2,
                "Depth" : int(fireMissionDepth.get())/2,
                "Length" : fireMissionLength.get(),
                "Condition" : fireMissionCondition.get(),
                "Mutator" : mutator,
                "Orientation" : orientation,
                "Time" : {"Hour" : int(fireMissionHour.get()),
                        "Minute" : int(fireMissionMinute.get()),
                        "Second" : int(fireMissionSecond.get())}
            }
            newTarget[prefix][new_item] = targetList[prefix][new_item]
            Json_Save(source=3,newEntry=newTarget)
            StatusMessageLog(message=f"Added New Fire mission {prefix}-{new_item}, Position: {targetPosX.get()} {targetPosY.get()}, Height: {targetHeight.get()}")
            if str(new_item)[1:].isdigit():
                if str(new_item)[1:] == "9":
                    nextTarget = str(new_item)[:-1]+"A"
                else:
                    nextTarget = str(new_item)[:-1]+str(int(new_item[1:])+1)
            elif str(new_item)[1:].isalpha():
                if str(new_item)[1:] == "Z":
                    nextTarget = str(new_item)[:-1]
                else:
                    nextTarget = str(new_item)[:-1]+chr(ord(str(new_item)[1:]) + 1)
            targetReference.set(nextTarget)
            if prefix == "LR":
                update_scrollregion(targetListLRCanvasFrame,targetListLRCanvas) 
            elif prefix == "XY":       
                update_scrollregion(targetListXYCanvasFrame,targetListXYCanvas) 
            elif prefix =="FPF":
                update_scrollregion(targetListFPFCanvasFrame,targetListFPFCanvas) 

def FireMissionLoadInfo(newfireMissions):
    global FireMissions
    if newfireMissions != FireMissions:
        FireMissions = newfireMissions
        FireMissionDisplayTabUpdate(FireMissions)
        FireMissionDisplayUpdate(FireMissions)
        

def update_scrollregion(frame: ttk.Frame,canvas: Canvas):
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def FireMissionUpdate(details : dict,idfp : str, target : str):
    """Sends the Fire mission details to the IDFP and target referenced. Overwrites as well"""
    fireMissions = Json_Load(source=4)
    try: fireMissions[idfp][target] = details
    except KeyError: fireMissions[idfp] = {target : details}
    Json_Save(source=4,newEntry=fireMissions)
    UpdateSync(4)

calculations = 0
def Calculate():
    statusProgressBar["value"],statusProgressBar["mode"] = 0,"determinate"
    global calculations
    calculations = 0
    targets = Json_Load(3)
    def CalculationPhasesTotal(mission):
        global calculations
        for target, (edit, calculate) in listCheckBox_vars[mission].items():
            if calculate.get() == True:
                calculations += 1
                try:
                    if targets[mission][target]["Mutator"] == "Line":
                        if targets[mission][target]["Orientation"] == "Vertical":
                            calculations += 2
                    elif targets[mission][target]["Mutator"] == "Box":
                        calculations += 2
                    elif targets[mission][target]["Mutator"] == "LineMultiPoint":
                        if targets[mission][target]["Explicit"] == True:
                            calculations += 1
                except Exception as e: StatusMessageErrorDump(e,errorMessage=f"Failed to get {mission}-{target} mutator")
                    

    CalculationPhasesTotal("FPF")
    CalculationPhasesTotal("LR")
    CalculationPhasesTotal("XY")
    for target, (edit, calculate) in listCheckBox_vars["Combo"].items():
        if calculate.get() == True:
            calculations += 1
            try:
                if targets["Group"][target]["Mutator"] == "Line":
                    if targets["Group"][target]["Orientation"] == "Vertical":
                        calculations += 2
                elif targets["Group"][target]["Mutator"] == "Box":
                    calculations += 2
                elif targets["Group"][target]["Mutator"] == "LineMultiPoint":
                    if targets["Group"][target]["Explicit"] == True:
                        calculations += 2
            except Exception as e: StatusMessageErrorDump(e,errorMessage=f"Failed to get Combo mission-{target} mutator")

    statusProgressBar["maximum"] = int(calculations)
    states = {}
    IDFPDict = {}
    states = Json_Load(0)
    IDFPDict = Json_Load(1)
    def solutions (details,idfp):
        charge = -1 if IDFPDict[idfp]["ForceCharge"] == 0 else int(IDFPDict[idfp]["Charge"])
        if details["Mutator"] == "None":
            solution = AF.Solution(baseDir=exeDir,
                                    artyX=IDFPDict[idfp]["GridX"],
                                    artyY=IDFPDict[idfp]["GridY"],
                                    system=states["system"],
                                    fireAngle=IDFPDict[idfp]["Trajectory"],
                                    tgtX=details["GridX"],tgtY=details["GridY"],
                                    artyHeight=IDFPDict[idfp]["Height"],
                                    targetHeight=details["Height"],
                                    maxHeight=maxTerrainHeight,
                                    windDirection=states["windDirection"],
                                    windMagnitude=states["windMagnitude"],
                                    windDynamic=int(states["windDynamic"]),
                                    humidity=states["airHumidity"],
                                    temperature=states["airTemperature"],
                                    pressure=states["airPressure"],
                                    charge=charge
                                )
            print(solution)
            #############TERRAIN AVOIDANCE +1 Charge
            solution["Effect"],solution["Length"],solution["Condition"],solution["Mutator"],solution["Trajectory"] = details["Effect"],details["Length"],details["Condition"],details["Mutator"],IDFPDict[idfp]["Trajectory"]
            if details["Condition"] == "Time":
                solution["Time"] = {
                    "Hour": details["Time"]["Hour"],
                    "Minute": details["Time"]["Minute"],
                    "Second": details["Time"]["Second"]
                }
            if int(states["windDynamic"]) == 1:
                solution
            del solution["LowPositions"]
            return solution
        elif details["Mutator"] == "Line":
            deviation = details["Depth"] if details["Orientation"] == "Vertical" else details["Width"]
            solution = AF.Line(baseDir=exeDir,
                    orientation=details["Orientation"],
                    deviation=deviation,
                    artyX=IDFPDict[idfp]["GridX"],
                    artyY=IDFPDict[idfp]["GridY"],
                    system=states["system"],
                    fireAngle=IDFPDict[idfp]["Trajectory"],
                    tgtX=details["GridX"],tgtY=details["GridY"],
                    artyHeight=IDFPDict[idfp]["Height"],
                    targetHeight=details["Height"],
                    maxHeight=maxTerrainHeight,
                    windDirection=states["windDirection"],
                    windMagnitude=states["windMagnitude"],
                    windDynamic=int(states["windDynamic"]),
                    humidity=states["airHumidity"],
                    temperature=states["airTemperature"],
                    pressure=states["airPressure"],
                    charge=charge,
                    progressbar=statusProgressBar
            )
            solution["Effect"],solution["Length"],solution["Condition"],solution["Mutator"],solution["Orientation"],solution["Deviation"],solution["Trajectory"] = details["Effect"],details["Length"],details["Condition"],details["Mutator"],details["Orientation"],deviation,IDFPDict[idfp]["Trajectory"]
            if details["Condition"] == "Time":
                solution["Time"] = {
                    "Hour": details["Time"]["Hour"],
                    "Minute": details["Time"]["Minute"],
                    "Second": details["Time"]["Second"]
                }
            del solution["LowPositions"]
            return solution
        
        elif details["Mutator"] == "Box":
            solution = AF.Box(baseDir=exeDir,
                    deviationLength=details["Depth"],
                    deviationWidth=details["Width"],
                    artyX=IDFPDict[idfp]["GridX"],
                    artyY=IDFPDict[idfp]["GridY"],
                    system=states["system"],
                    fireAngle=IDFPDict[idfp]["Trajectory"],
                    tgtX=details["GridX"],tgtY=details["GridY"],
                    artyHeight=IDFPDict[idfp]["Height"],
                    targetHeight=details["Height"],
                    maxHeight=maxTerrainHeight,
                    windDirection=states["windDirection"],
                    windMagnitude=states["windMagnitude"],
                    windDynamic=int(states["windDynamic"]),
                    humidity=states["airHumidity"],
                    temperature=states["airTemperature"],
                    pressure=states["airPressure"],
                    charge=charge,
                    progressbar=statusProgressBar
            )
            solution["Effect"],solution["Length"],solution["Condition"],solution["Mutator"],solution["Trajectory"] = details["Effect"],details["Length"],details["Condition"],details["Mutator"],IDFPDict[idfp]["Trajectory"]
            if details["Condition"] == "Time":
                solution["Time"] = {
                    "Hour": details["Time"]["Hour"],
                    "Minute": details["Time"]["Minute"],
                    "Second": details["Time"]["Second"]
                }
            del solution["LowPositions"]
            return solution
        else:
            None
            #################BOXBOXBOX
    def CalculationIteration(mission):
        for target, (edit,calculate) in listCheckBox_vars[mission].items():
            if calculate.get() == True:
                details = targets[mission][target]
                idfpSelection = Json_Load(0,localOverride=True)["IDFPSelection"]
                for idfp in [list(IDFPDict.keys())[i] for i in list(idfpSelection)]:
                    #try :
                        StatusMessageLog(message=f"Beginning calculation of {mission}-{target}")
                        solution = solutions(details,idfp)
                    #except Exception as e: StatusMessageErrorDump(e,errorMessage=f"Failed to calculate {mission}-{target}")
                    #else:
                        FireMissionUpdate(solution,idfp,f"{mission}-{target}")
                        StatusMessageLog(message="Calculated {}-{}, Range: {}m, Bearing: {:03d}°".format(mission,target,int(solution["Range"]),int(solution["Bearing"]*180/np.pi)))
                        statusMessageLabel.update()
                        statusProgressBar["value"] = statusProgressBar["value"] + 1
                        statusProgressBar.update()
    CalculationIteration("FPF")
    CalculationIteration("LR")
    CalculationIteration("XY")
    CalculationIteration("Combo")
    root.bell()


def StandardFireMissionOutput(FireMissions: dict,idfp: str,textWidget: Text):
    def Standard(details):
        try: 
            if details["Notes"]!= "":
                textWidget.insert(END,"\t\t| Note: {}\n".format(details["Notes"]),("default","border"))
            else: textWidget.insert(END,"\n","border")
        except: textWidget.insert(END,"\n","border")
        textWidget.insert(END,"\t-----------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
        textWidget.insert(END,"\tEffect\t| {}\n\tLength\t| {}\n\tCondition\t| {}\n\tSystem\t| {}\n".format(details["Effect"],details["Length"],details["Condition"],details["System"]),("default","border"))
        textWidget.insert(END,"\t-----------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
        textWidget.insert(END,"\tRange\t| {:04d}".format(int(details["Range"])),("default","border"))
        try:
            if float(details["DeviationLength"]) > 1.0:
                textWidget.insert(END," ± {} m\n".format(int(np.round(details["DeviationLength"]))),("default","border"))
            else:
                textWidget.insert(END," m\n",("default","border"))
        except: textWidget.insert(END," m\n",("default","border"))
        try:
            if float(details["DeviationWidth"]) > 1.0:
                textWidget.insert(END,"\tWidth\t| ± {} m\n".format(int(np.round(details["DeviationWidth"]))),("default","border"))
        except: None
        try:vertex = int(np.ceil(list(details["Vertex"])[2]/5)*5)
        except:vertex = details["Vertex"]
        textWidget.insert(END,"\tTrajectory\t| {} \n\tTOF\t| {:0.1f} s\n\tVertex\t| FL {:03d}\n".format(details["Trajectory"],float(details["TOF"]),vertex),("default","border"))
        try:
            details["ParallelCorrection"]
            textWidget.insert(END,"\t",("default","border"))
            textWidget.insert(END,"Wind Magnitude\t| {:0.1f} m/s\t".format(np.round(float(details["WindMagnitude"])*10)/10),("default"))
            textWidget.insert(END,"\n\t",("default","border"))
            textWidget.insert(END,"Crosswind\t| ±",("default"))
            textWidget.insert(END," {} ".format(int(np.round(float(details["PerpendicularCorrection"])))),("bold"))
            textWidget.insert(END,"mils\t",("default"))
            textWidget.insert(END,"\n\t",("default","border"))
            textWidget.insert(END,"Head/Tailwind\t| ±",("default"))
            textWidget.insert(END," {} ".format(int(np.round(float(details["ParallelCorrection"])))),("bold"))
            textWidget.insert(END,"mils\t",("default"))
            textWidget.insert(END,"\n",("default","border"))
            textWidget.insert(END,"\t-----------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
        except:
            None
        textWidget.insert(END,"")
        textWidget.insert(END,"\tCharge\t| ".format(details["Trajectory"],float(details["TOF"]),vertex),("default","border"))
        textWidget.insert(END," {} ".format(details["Charge"]),("bold","highlight"))
        textWidget.insert(END,"\n\t-----------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
        textWidget.insert(END,"\tAzimuth\t| ",("default","border"))
        
        textWidget.insert(END," {:06.1f} ".format(details["Azimuth"]*3200/np.pi),("bold","highlight"))
        try:
            if float(details["DeviationWidth"]) > 1.0:
                azimuthDeviation = details["Azimuth"]-details["Left"] if (details["Azimuth"]-details["Left"]) > 0 else (details["Azimuth"]-details["Left"])+2*np.pi
                textWidget.insert(END," ± {} mils\n\t⇐      ".format(np.round(azimuthDeviation*3200/np.pi)),("default","border"))
                textWidget.insert(END,"{:04d}".format(int(np.round(details["Left"]*3200/np.pi))),("bold","border"))
                textWidget.insert(END,"\t|",("default","border"))
                textWidget.insert(END,"\t{:04d}".format(int(np.round(details["Right"]*3200/np.pi))),("bold","border"))
                textWidget.insert(END,"      ⇒ \n",("default","border"))
            else: textWidget.insert(END," mils\n",("default","border"))
        except: textWidget.insert(END," mils\n",("default","border"))
        textWidget.insert(END,"\t-----------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
        textWidget.insert(END,"\tElevation\t| ",("default","border"))
        textWidget.insert(END," {:06.1f} ".format(details["Elevation"]),("bold","highlight"))
        try:
            if float(details["DeviationLength"]) > 1.0:
                elevationDeviation = (abs(details["Elevation"]-details["Near"])+abs(details["Elevation"]-details["Far"]))/2
                textWidget.insert(END," ± {} mils\n".format(np.round(elevationDeviation)),("default","border"))
                textWidget.insert(END,"\t⇓       ",("default","border"))
                textWidget.insert(END,"{:04d}".format(int(np.round(details["Near"]))),("bold","border"))
                textWidget.insert(END,"\t| ",("default","border"))
                textWidget.insert(END,"\t{:04d}".format(int(np.round(details["Far"]))),("bold","border"))
                textWidget.insert(END,"       ⇑\n",("default","border"))
            else: textWidget.insert(END," mils\n",("default","border"))
        except: textWidget.insert(END," mils\n",("default","border"))
    #FPF
    for reference, details in FireMissions[idfp].items():
        if reference[:2] == "FP" and reference.count(",") == 0:
            if textWidget.get("1.0", END).strip()!="": textWidget.insert(END,"\n",("default","divide"))
            textWidget.insert(END," {} ".format(reference),"FPF")
            Standard(details)
    #LR
    for reference, details in FireMissions[idfp].items():
        if reference[:2] == "LR" and reference.count(",") == 0:
            if textWidget.get("1.0", END).strip()!="": textWidget.insert(END,"\n",("default","divide"))
            textWidget.insert(END," {} ".format(reference),"LR")
            Standard(details)
    #XY
    for reference, details in FireMissions[idfp].items():
        if reference[:2] == "XY" and reference.count(",") == 0:
            if textWidget.get("1.0", END).strip()!="": textWidget.insert(END,"\n",("default","divide"))
            textWidget.insert(END," {} ".format(reference),"XY")
            Standard(details)
    #Pairs
    for reference, details in FireMissions[idfp].items():
        if reference.count(",") > 0:
            if textWidget.get("1.0", END).strip()!="": textWidget.insert(END,"\n",("default","divide"))
            commaCount = 0
            textWidget.insert(END," ","Group")
            for char in reference:
                if char !=",":
                    textWidget.insert(END,"{}".format(char),"Group")
                elif commaCount == 0:
                    commaCount +=1
                    textWidget.insert(END," ","Group")
                    try:
                        if details["Notes"] != "":
                            textWidget.insert(END,"\t\t| Note: {}\n".format(details["Notes"]),("default","border"))
                        else:
                            textWidget.insert(END,"\n",("default","border"))
                    except:
                        textWidget.insert(END,"\n",("default","border"))
                    textWidget.insert(END," ","Group")
                else:
                    commaCount+=1
                    textWidget.insert(END," ","Group")
                    textWidget.insert(END,"\n",("default","border"))
                    textWidget.insert(END," ","Group")
            textWidget.insert(END," ","Group")
            textWidget.insert(END,"\n",("default","border"))
            textWidget.insert(END,"\t-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
            textWidget.insert(END,"\tEffect\t| {}\t({})\n\tCondition\t| {}\n\tSystem\t| {}\n\tDistance\t| {} ± {} m\n\tWidth\t| {} ± {} m\n".format(details["PairedEffect"],details["Effect"],details["Condition"],details["System"],details["Distance"],details["Dispersion"],details["Width"],details["Dispersion"]),("default","border"))
            textWidget.insert(END,"\t-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
            textWidget.insert(END,"\tTrajectory\t| {} \n\tTOF\t| {:0.1f} s\n\tVertex\t| FL {} \n\tRound Count\t| ".format(details["Trajectory"],float(details["TOF"]),details["Vertex"]),("default","border"))
            textWidget.insert(END,"{} rounds\n".format(details["RoundCount"]),("bold","border"))
            textWidget.insert(END,"\tCharge\t| ",("default","border"))
            textWidget.insert(END,"{}\n".format(details["Charge"]),("bold","border"))
            textWidget.insert(END,"\t-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
            textWidget.insert(END,"\tAzimuth\t| ",("default","border"))
            textWidget.insert(END,"{:04d}".format(details["Azimuth"]),("bold","border"))
            textWidget.insert(END," ± ",("default","border"))
            textWidget.insert(END," {} ".format(details["AzimuthDeviation"]),("bold","highlight"))
            textWidget.insert(END," mils with ",("default","border"))
            textWidget.insert(END,"{}".format(details["AzimuthRounds"]),("bold","border"))
            textWidget.insert(END," rounds or lines\n\t⇐      ",("default","border"))
            textWidget.insert(END," {:04d} ".format(details["AzimuthLeft"]),("bold","highlight"))
            textWidget.insert(END,"\t|\t",("default","border"))
            textWidget.insert(END," {:04d} ".format(details["AzimuthRight"]),("bold","highlight"))
            textWidget.insert(END,"      ⇒ \n",("default","border"))
            textWidget.insert(END,"\t-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
            textWidget.insert(END,"\tElevation\t| ",("default","border"))
            textWidget.insert(END,"{:04d}".format(details["Elevation"]),("bold","border"))
            textWidget.insert(END," ± ",("default","border"))
            textWidget.insert(END," {} ".format(details["ElevationDeviation"]),("bold","highlight"))
            textWidget.insert(END," mils with ",("default","border"))
            textWidget.insert(END,"{}".format(details["ElevationRounds"]),("bold","border"))
            textWidget.insert(END," lines or rounds\n",("default","border"))
            if details["Trajectory"] == "High":
                textWidget.insert(END,"\t⇓       ",("default","border"))
                textWidget.insert(END," {:04d} ".format(details["ElevationHigh"]),("bold","highlight"))
                textWidget.insert(END,"\t|\t",("default","border"))
                textWidget.insert(END," {:04d} ".format(details["ElevationLow"]),("bold","highlight"))
                textWidget.insert(END,"       ⇑\n",("default","border"))
            else:
                textWidget.insert(END,"\t⇓       ",("default","border"))
                textWidget.insert(END," {:04d} ".format(details["ElevationLow"]),("bold","highlight"))
                textWidget.insert(END,"\t|\t",("default","border"))
                textWidget.insert(END," {:04d} ".format(details["ElevationHigh"]),("bold","highlight"))
                textWidget.insert(END,"       ⇑\n",("default","border"))
    textWidget["state"] = "disabled"
    return True


def IDFPTextFrameConfiguration(idfpNotebookFrame: ttk.Frame):
    idfpNotebookFrame.grid(row=0,column=0,sticky="NESW")
    idfpNotebookFrame.grid_rowconfigure(0,weight=1)
    idfpNotebookFrame.grid_rowconfigure(1,minsize=20)
    idfpNotebookFrame.grid_columnconfigure(0,weight=1)
    idfpNotebookFrame.grid_columnconfigure(1,minsize=20)
    idfpNotebookText = Text(idfpNotebookFrame,wrap="none",background="black",foreground="black",width=55,tabs=("2c","5c","6.5c","3c"))#bg="#BBBBBB",
    idfpNotebookText.tag_configure("default",font=("Microsoft Tai Le",10),background="white")
    idfpNotebookText.tag_configure("line",font=("Microsoft Tai Le",4),background="white")
    idfpNotebookText.tag_configure("XY",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,background="#2C5F2D",foreground="#FFE77A")
    idfpNotebookText.tag_configure("LR",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,background="#5B84B1",foreground="#FC766A")
    idfpNotebookText.tag_configure("FPF",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,foreground="white",background="#BB5050",bgstipple="@tempstipple.xbm")
    idfpNotebookText.tag_configure("Group",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,foreground="#D9514E",background="#006747",bgstipple="@tempstipple.xbm")
    #idfpNotebookText.tag_configure("Group",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,foreground="#D9514E",background="#006747",bgstipple='@Functions/warning.xbm')
    idfpNotebookText.tag_configure("bold",font=("Microsoft Tai Le",10,"bold"),background="white")
    idfpNotebookText.tag_configure("border",relief="ridge",borderwidth="2",background="white")
    idfpNotebookText.tag_configure("highlight",relief="raised",borderwidth="2",background="white")
    #idfpNotebookText.tag_configure("highlight",relief="raised",borderwidth="2",background="white")
    idfpNotebookText.tag_configure("divide",font=("Microsoft Tai Le",4),background="grey",bgstipple="@tempstipple.xbm")
    yScroll = Scrollbar(idfpNotebookFrame,orient="vertical",command=idfpNotebookText.yview)
    xScroll = Scrollbar(idfpNotebookFrame,orient="horizontal",command=idfpNotebookText.xview)
    idfpNotebookText["yscrollcommand"] = yScroll.set
    idfpNotebookText["xscrollcommand"] = xScroll.set
    idfpNotebookText.grid(row=0,column=0,sticky="nesw")
    yScroll.grid(row=0,column=1,sticky="ns")
    xScroll.grid(row=1,column=0,sticky="ew")
    idfpNotebookText["state"] = "disabled"

def UpdateFireMissionNotebook(FireMissions):
    global idfpNotebookFrameDict
    for idfp in FireMissions.keys():
        previous = False
        for previousIDFP in idfpNotebookFrameDict.keys():
            if idfp == previousIDFP:
                previous = True
                break
        if previous == False:
            idfpNotebookFrame = ttk.Frame(idfpNotebook,width="500")
            idfpNotebookFrameDict[idfp] = idfpNotebookFrame
            idfpNotebookFrame.grid(row=0,column=0,sticky="NESW")
            
            idfpNotebookFrame.grid_rowconfigure(0,weight=1)
            idfpNotebookFrame.grid_rowconfigure(1,minsize=20)
            idfpNotebookFrame.grid_columnconfigure(0,weight=1)
            idfpNotebookFrame.grid_columnconfigure(1,minsize=20)
            idfpNotebookText = Text(idfpNotebookFrame,wrap="none",background="black",foreground="black",width=55,tabs=("2c","5c","6.5c"))#bg="#BBBBBB",
            idfpNotebookText.tag_configure("default",font=("Microsoft Tai Le",10),background="white")
            idfpNotebookText.tag_configure("line",font=("Microsoft Tai Le",4),background="white")
            idfpNotebookText.tag_configure("XY",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,background="#2C5F2D",foreground="#FFE77A")
            idfpNotebookText.tag_configure("LR",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,background="#5B84B1",foreground="#FC766A")
            idfpNotebookText.tag_configure("FPF",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,foreground="white",background="#BB5050",bgstipple="@Functions/warning.xbm")
            idfpNotebookText.tag_configure("Group",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,foreground="#D9514E",background="#006747",bgstipple="@Functions/warning.xbm")
            #idfpNotebookText.tag_configure("Group",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,foreground="#D9514E",background="#006747",bgstipple='@Functions/warning.xbm')
            idfpNotebookText.tag_configure("bold",font=("Microsoft Tai Le",10,"bold"),background="white")
            idfpNotebookText.tag_configure("border",relief="ridge",borderwidth="2",background="white")
            idfpNotebookText.tag_configure("highlight",relief="raised",borderwidth="2",background="white")
            idfpNotebookText.tag_configure("divide",font=("Microsoft Tai Le",4),background="grey",bgstipple="@Functions/warning.xbm")
            yScroll = Scrollbar(idfpNotebookFrame,orient="vertical",command=idfpNotebookText.yview)
            xScroll = Scrollbar(idfpNotebookFrame,orient="horizontal",command=idfpNotebookText.xview)
            idfpNotebookText["yscrollcommand"] = yScroll.set
            idfpNotebookText["xscrollcommand"] = xScroll.set
            idfpNotebookText.grid(row=0,column=0,sticky="nesw")
            yScroll.grid(row=0,column=1,sticky="ns")
            xScroll.grid(row=1,column=0,sticky="ew")
            idfpNotebookText["state"] = "disabled"
            idfpNotebook.add(idfpNotebookFrame,text=idfp,sticky="NESW",padding="10")

def FireMissionDisplayTabUpdate(FireMissions):
    global idfpNotebookFrameDict
    tabs = []
    for tabId in idfpNotebook.tabs():
        tabs.append(idfpNotebook.tab(tabId,option="text"))
        if idfpNotebook.tab(tabId,option="text") not in FireMissions.keys():
            idfpNotebook.forget(tabId)
            try: del idfpNotebookFrameDict[idfpNotebook.tab(tabId,option="text")]
            except Exception as e: StatusMessageErrorDump(e,errorMessage="Failed to remove Fire Missions")
    for idfp in FireMissions.keys():
        if idfp not in tabs:
            idfpNotebookFrame = ttk.Frame(idfpNotebook,width="500")
            idfpNotebookFrameDict[idfp] = idfpNotebookFrame
            IDFPTextFrameConfiguration(idfpNotebookFrame)
            idfpNotebook.add(idfpNotebookFrame,text=idfp,sticky="NESW",padding="10")



def FireMissionDisplayUpdate(FireMissions):
    global idfpNotebookFrameDict
    if idfpNotebookFrameDict!= {}:
        for idfp in FireMissions.keys():
            for widget in idfpNotebookFrameDict[idfp].winfo_children():
                if type(widget) == Text:
                    widget["state"] = "normal"
                    widget.delete("1.0",END)
                    StandardFireMissionOutput(FireMissions,idfp,widget)     
    return True

boldLables = {
    "idfpName" : False,
    "airTemperature" : False,
    "airHumidity" : False,
    "airPressure" : False,
    "windDirection" : False,
    "windMagnitude" : False,
}

def LabelBold(label : Widget,type="Normal",stringvar = ""):
    """Will make the specified widget font be made bold if type = 'Bold'"""
    label.config(font=("Microsoft Tai Le",9,"bold")) if type.lower() == "bold" else label.config(font=("Microsoft Tai Le",9))
    if stringvar != "":
        if type.lower() == "bold":
            boldLables[stringvar] = True
    return True

def CancelSettingChange(StrVar: StringVar, label: Widget,stringvar = ""):
    StrVar.set(" ")
    LabelBold(label,type="Normal",stringvar=stringvar)
    boldLables[stringvar] = False

def Maps():
    None

menubar = Menu(root)
content = ttk.Frame(root)
content.grid_columnconfigure(0,weight=1)
content.grid_rowconfigure(0,weight=1)
mainframe = ttk.Frame(content, padding="1",)
mainframe.grid_columnconfigure(0,weight=1)
mainframe.grid_rowconfigure(0,weight=1)
mainframe.grid_rowconfigure(1,)

#STATUS BAR########################################################################
statusBar = ttk.Frame(mainframe,height=105,relief="ridge",padding="5")
statusBar.grid_columnconfigure(0,weight=3)
statusBar.grid_columnconfigure(1,minsize="195")
statusBar.grid_columnconfigure(2,weight=1)
statusMessageFrame = ttk.Frame(statusBar,relief="sunken",padding="3")
statusMessageFrame.grid_columnconfigure(0,weight=1)
statusMessageLabel = ttk.Label(statusMessageFrame,text="C.A.S.T. start up")
statusMessageFrame.bind("<Double-1>",OpenMessageLog)
statusMessageLabel.bind("<Double-1>",OpenMessageLog)
statusGridFrame = ttk.Frame(statusBar,relief="sunken",padding="3")
statusGridFrame.grid_columnconfigure((0,1,2),minsize=30,weight=1)
statusReferenceLabel = ttk.Label(statusGridFrame,text="",justify="left")
statusGridLabel = ttk.Label(statusGridFrame,text="",justify="right")
statusHeightLabel = ttk.Label(statusGridFrame,text="",justify="right")
statusProgressBar = ttk.Progressbar(statusBar,orient="horizontal")

StatusMessageLog(message="", privateMessage="-----New Session-----\n")
mainNotebook = ttk.Notebook(mainframe)
notePage1 = ttk.Frame(mainNotebook,relief="groove",padding="10")
notePage2 = ttk.Frame(mainNotebook,relief="groove",padding="10")
mainNotebook.add(notePage1,text="Fire Mission",padding=1)
mainNotebook.add(notePage2,text="Maps",sticky="NESW",padding=1)
notePage1.grid_rowconfigure(0,weight=1)
notePage1.grid_columnconfigure(0,weight=1)
notePage2.grid_rowconfigure(0,weight=1)
notePage2.grid_columnconfigure(0,weight=1)
fireMissionPagePanedWindow = ttk.Panedwindow(notePage1,orient="horizontal")
pane0 = ttk.Frame(fireMissionPagePanedWindow,width=0,padding=1)
pane1 = ttk.Frame(fireMissionPagePanedWindow,width=500,padding=1)
pane2 = ttk.Frame(fireMissionPagePanedWindow,width=500,padding=1)
pane3 = ttk.Frame(fireMissionPagePanedWindow,width=500,padding=1)
pane4 = ttk.Frame(fireMissionPagePanedWindow,width=500,padding=1)
pane5 = ttk.Frame(fireMissionPagePanedWindow,width=0,padding=1)
fireMissionPagePanedWindow.add(pane0)
fireMissionPagePanedWindow.add(pane1)
fireMissionPagePanedWindow.add(pane2)
fireMissionPagePanedWindow.add(pane3)
fireMissionPagePanedWindow.add(pane4)
fireMissionPagePanedWindow.add(pane5)
pane1.grid_rowconfigure(0,weight=1)
pane1.grid_columnconfigure(0,weight=1)
pane2.grid_rowconfigure(0,weight=1)
pane2.grid_columnconfigure(0,weight=1)
pane3.grid_rowconfigure(0,weight=1)
pane3.grid_columnconfigure(0,weight=1)
pane4.grid_rowconfigure(0,weight=1)
pane4.grid_columnconfigure(0,weight=1)
pane1pane = ttk.PanedWindow(pane1,orient="vertical")
pane11 = ttk.Frame(pane1pane,height=200,padding=5)
pane12 = ttk.Frame(pane1pane,height=200,padding=5)
pane13 = ttk.Frame(pane1pane,height=200,padding=5)
pane14 = ttk.Frame(pane1pane,height=450,padding=5)


pane1pane.add(pane11,weight=0)
pane11.grid_rowconfigure(0,weight=1)
pane11.grid_columnconfigure(0,weight=1)
pane11Labelframe = ttk.Labelframe(pane11,text="IDFP",height=200,padding=10,relief="groove")
pane11Labelframe.grid_rowconfigure(0,weight=1)
pane11Labelframe.grid_rowconfigure(1,weight=0)
pane11Labelframe.grid_columnconfigure(0,weight=1)
idfpCreationFrame = ttk.Labelframe(pane11Labelframe,text="Creation",height=200,padding=10,relief="groove")
idfpCreationFrame.grid_rowconfigure((0,1,2,3,4),weight=1)
idfpCreationFrame.grid_columnconfigure(0,weight=0,minsize=10)
idfpCreationFrame.grid_columnconfigure(1,weight=1,minsize=40)
idfpCreationFrame.grid_columnconfigure(2,weight=1,minsize=40)
idfpNameLabel = ttk.Label(idfpCreationFrame,text="Name:",justify="right",padding=4)
idfpNameCombobox = ttk.Combobox(idfpCreationFrame,justify="center",textvariable=idfpName)
idfpNameCombobox.bind("<Return>",lambda event: LoadInfo(event,source=1))
idfpNameCombobox.bind("<Tab>",lambda event: LoadInfo(event,source=1))
idfpName.trace_add("write",callback=lambda *args: LabelBold(idfpNameLabel,"Bold","idfpName"))
idfpPosLabel = ttk.Label(idfpCreationFrame,text="Position:",justify="right",padding=4)
idfpPosXEntry  = ttk.Entry(idfpCreationFrame, justify="center",textvariable=idfpPosX)
idfpPosXEntry.bind("<Return>",IDFPHeightAutoFill)
idfpPosXEntry.bind("<Tab>",IDFPHeightAutoFill)
idfpPosYEntry  = ttk.Entry(idfpCreationFrame, justify="center",textvariable=idfpPosY)
idfpPosYEntry.bind("<Return>",IDFPHeightAutoFill)
idfpPosYEntry.bind("<Tab>",IDFPHeightAutoFill)
idfpHeightLabel = ttk.Label(idfpCreationFrame,text="Height:",justify="right",padding=4)
idfpHeightFrame = ttk.Frame(idfpCreationFrame)
idfpHeightFrame.grid_rowconfigure(0,weight=1)
idfpHeightFrame.grid_columnconfigure(0,weight=1,minsize=30)
idfpHeightFrame.grid_columnconfigure(1,weight=0,minsize=5)
idfpHeightEntry = ttk.Entry(idfpHeightFrame, justify="center",textvariable=idfpHeight)
idfpHeightUnitLabel = ttk.Label(idfpHeightFrame,text="m")
idfpButtonFrame = ttk.Frame(idfpCreationFrame,padding=5)
idfpButtonFrame.grid_columnconfigure(0,weight=1)
#idfpButtonFrame.grid_rowconfigure(0,weight=5)
idfpButtonFrame.grid_rowconfigure((0,1,2),weight=1)
idfpSystemFrame = ttk.Frame(idfpButtonFrame,padding=4,relief="solid")
idfpSystemFrame.grid_columnconfigure(0,minsize=9,weight=1)
idfpSystemFrame.grid_columnconfigure(1,minsize=4)
idfpSystemFrame.grid_columnconfigure(2,minsize=9,weight=5)
idfpSystemFrame.grid_rowconfigure(0,weight=1)
idfpSystemLabel = ttk.Label(idfpSystemFrame,text="System")
idfpSystemSep = ttk.Separator(idfpSystemFrame,orient="vertical")
idfpSystemOutput = ttk.Label(idfpSystemFrame,text="None",justify="right")
idfpAddButton = ttk.Button(idfpButtonFrame,text="Add/Update",command=IDFPPositionAddUpdate)
idfpRemoveButton = ttk.Button(idfpButtonFrame,text="Remove",command=lambda: IDFPPositionRemove(name=idfpName.get()))
idfpSeparator = ttk.Separator(idfpCreationFrame,orient="horizontal")
idfpControlFrame = ttk.Frame(idfpCreationFrame)
idfpControlFrame.grid_columnconfigure(0,weight=0,minsize=10)
idfpControlFrame.grid_columnconfigure(1,weight=1)
idfpControlFrame.grid_rowconfigure((0,1),weight=1)
idfpEditChargeLabel = ttk.Label(idfpControlFrame,text="Charge",justify="right",padding=2)
idfpChargeFrame = ttk.Frame(idfpControlFrame)
idfpChargeFrame.grid_columnconfigure(0,weight=0,minsize=5)
idfpChargeFrame.grid_columnconfigure(1,weight=1)
idfpChargeFrame.grid_rowconfigure(0,weight=1)
idfpEditChargeCheckbox = ttk.Checkbutton(idfpChargeFrame,variable=idfpUseCharge,offvalue=0,onvalue=1,padding=2)
idfpUseCharge.set(0)#idfpUseCharge.trace_add(mode="write",callback=lambda *args, s="ForceCharge", n=idfpName.get(),v = idfpUseCharge.get(): IDFPChangeSetting(s,n,v))
idfpEditChargeComboBox = ttk.Combobox(idfpChargeFrame,textvariable=idfpCharge,width=4,state="readonly")
#idfpCharge.trace_add(mode="write",callback=lambda *args, s="Charge", n=idfpName.get(),v = idfpCharge.get(): IDFPChangeSetting(s,n,v))
idfpEditTrajLabel = ttk.Label(idfpControlFrame,text="Trajectory",justify="right",padding=2)
idfpEditTrajComboBox = ttk.Combobox(idfpControlFrame,textvariable=idfpTraj,width=4,state="readonly")
#idfpTraj.trace_add(mode="write",callback=lambda *args, s="Trajectory", n=idfpName.get(),v = idfpTraj.get(): IDFPChangeSetting(s,n,v))

idfpListBoxFrame = ttk.Labelframe(pane11Labelframe,text="Selection",height=200,padding=10,relief="groove")
idfpListBoxFrame.grid_rowconfigure(0,weight=1)
idfpListBoxFrame.grid_columnconfigure(0,weight=1)
idfpListbox = Listbox(idfpListBoxFrame,height=5,width=7,listvariable=idfpList,relief="sunken",justify="center",activestyle="dotbox",selectmode="multiple",borderwidth=2,exportselection=False)
idfpListbox.bind("<<ListboxSelect>>",lambda *arg: IdfpListBoxChange(idfpListbox.curselection()))


pane1pane.add(pane12,weight=0)
pane12.grid_rowconfigure(0,weight=1)
pane12.grid_columnconfigure(0,weight=1)
pane12Labelframe = ttk.Labelframe(pane12,text="Atmosphere",width=200,height=200,padding=5,relief="groove")
pane12Labelframe.grid_rowconfigure((0,1),weight=1)
pane12Labelframe.grid_columnconfigure(0,weight=1)
airLabelFrame = ttk.Labelframe(pane12Labelframe,text="Air",height=200,padding=2)
airLabelFrame.grid_columnconfigure(0,weight=5)
airLabelFrame.grid_columnconfigure(1)
airLabelFrame.grid_columnconfigure(2,minsize=75)
airLabelFrame.grid_columnconfigure(3,weight=4)
airLabelFrame.grid_rowconfigure((0,1,2),weight=1)
airSeparator = ttk.Separator(airLabelFrame,orient="vertical")
temperatureLabel = ttk.Label(airLabelFrame, text="Temperature",padding=4)
airTemperatureTrace = airTemperature.trace_add(mode="write",callback=lambda *args: LabelBold(temperatureLabel,"Bold","airTemperature"))
temperatureEntry = ttk.Entry(airLabelFrame,width="5",textvariable=airTemperature,justify="right")
temperatureEntry.bind("<Return>",TemperatureEntryValidate)
temperatureEntry.bind("<Tab>",TemperatureEntryValidate)
temperatureEntry.bind("<Escape>",lambda *args: CancelSettingChange(StrVar=airTemperature,label=temperatureLabel,stringvar="airTemperature"))
temperatureUnits = ttk.Label(airLabelFrame,text="°C")
humidityLabel = ttk.Label(airLabelFrame, text="Air Humidity",padding=4)
airHumidityTrace = airHumidity.trace_add(mode="write",callback=lambda *args: LabelBold(humidityLabel,"Bold","airHumidity"))
humidityEntry = ttk.Entry(airLabelFrame,width="5",textvariable=airHumidity,justify="right")
humidityEntry.bind("<Return>",HumidityEntryValidate)
humidityEntry.bind("<Tab>",HumidityEntryValidate)
humidityEntry.bind("<Escape>",lambda *args: CancelSettingChange(StrVar=airHumidity,label=humidityLabel,stringvar="airHumidity"))
humidityUnits = ttk.Label(airLabelFrame,text="%")
pressureLabel = ttk.Label(airLabelFrame, text="Air Pressure",padding=4)
airPressureTrace = airPressure.trace_add(mode="write",callback=lambda *args: LabelBold(pressureLabel,"Bold","airPressure"))
pressureEntry = ttk.Entry(airLabelFrame,width="7",textvariable=airPressure,justify="right")
pressureEntry.bind("<Return>",PressureEntryValidate)
pressureEntry.bind("<Tab>",PressureEntryValidate)
pressureEntry.bind("<Escape>",lambda *args: CancelSettingChange(StrVar=airPressure,label=pressureLabel,stringvar="airPressure"))
pressureUnits = ttk.Label(airLabelFrame,text="hPa")
windLabelFrame = ttk.Labelframe(pane12Labelframe,text="Wind",height=200,padding=2)
windLabelFrame.grid_columnconfigure(0,weight=1)
windLabelFrame.grid_columnconfigure(1)
windLabelFrame.grid_columnconfigure(2,minsize=75)
windLabelFrame.grid_columnconfigure(3,weight=1)
windLabelFrame.grid_rowconfigure((0,1,2),weight=1)
windSeparator = ttk.Separator(windLabelFrame,orient="vertical")
directionLabel = ttk.Label(windLabelFrame, text="Wind Direction",padding=4)
windDirectionTrace = windDirection.trace_add(mode="write",callback=lambda *args: LabelBold(directionLabel,"Bold","windDirection"))
directionEntry = ttk.Entry(windLabelFrame,width="3",textvariable=windDirection,justify="right")
directionEntry.bind("<Return>",DirectionEntryValidate)
directionEntry.bind("<Tab>",DirectionEntryValidate)
directionEntry.bind("<Escape>",lambda *args: CancelSettingChange(StrVar=windDirection,label=directionLabel,stringvar="windDirection"))
directionUnits = ttk.Label(windLabelFrame,text="°")
magnitudeLabel = ttk.Label(windLabelFrame, text="Wind Magnitude",padding=4)
windMagnitudeTrace = windMagnitude.trace_add(mode="write",callback=lambda *args: LabelBold(magnitudeLabel,"Bold","windMagnitude"))
magnitudeEntry = ttk.Entry(windLabelFrame,width="5",textvariable=windMagnitude,justify="right")
magnitudeEntry.bind("<Return>",MagnitudeEntryValidate)
magnitudeEntry.bind("<Tab>",MagnitudeEntryValidate)
magnitudeEntry.bind("<Escape>",lambda *args: CancelSettingChange(StrVar=windMagnitude,label=magnitudeLabel,stringvar="windMagnitude"))
magnitudeUnits = ttk.Label(windLabelFrame,text="m/s")
dynamicLabel = ttk.Label(windLabelFrame, text="Dynamic Wind",padding=4)
dynamicCheckBox = ttk.Checkbutton(windLabelFrame,variable=windDynamic,onvalue=1,offvalue=0,padding=4)
windDynamicTrace = windDynamic.trace_add(mode="write", callback=(lambda *args: Json_Save(source=0,newEntry={"windDynamic" : windDynamic.get()})))
pane1pane.add(pane13,weight=0)
pane13.grid_rowconfigure(0,weight=1)
pane13.grid_columnconfigure(0,weight=1)
pane13Labelframe = ttk.Labelframe(pane13,text="Friendly Position",height=200,width=500,padding=5,relief="groove")
pane13Labelframe.grid_rowconfigure((0,1,2,3),weight=1)
pane13Labelframe.grid_columnconfigure(0,weight=1,minsize="68")
pane13Labelframe.grid_columnconfigure(1,weight=5,minsize="20")
pane13Labelframe.grid_columnconfigure(2,minsize="10")
pane13Labelframe.grid_columnconfigure(3,weight=5,minsize="30")
friendlyNameLabel = ttk.Label(pane13Labelframe,text="Name:",justify="right",padding=4)
friendlyNameCombobox = ttk.Combobox(pane13Labelframe,justify="center",textvariable=friendlyName)
friendlyNameCombobox.bind("<Return>",lambda event: LoadInfo(event, source=2))
friendlyNameCombobox.bind("<Tab>",lambda event: LoadInfo(event, source=2))
friendlyName.trace_add(mode="write", callback=lambda *args: LabelBold(friendlyNameLabel,"Bold","friendlyName"))

friendlyPosLabel = ttk.Label(pane13Labelframe,text="Position:",justify="right",padding=4)
friendlyPosXEntry  = ttk.Entry(pane13Labelframe, justify="center",textvariable=friendlyPosX)
friendlyPosXEntry.bind("<Return>",FriendlyHeightAutoFill)
friendlyPosXEntry.bind("<Tab>",FriendlyHeightAutoFill)
friendlyPosYEntry  = ttk.Entry(pane13Labelframe, justify="center",textvariable=friendlyPosY)
friendlyPosYEntry.bind("<Return>",FriendlyHeightAutoFill)
friendlyPosYEntry.bind("<Tab>",FriendlyHeightAutoFill)
friendlyHeightLabel = ttk.Label(pane13Labelframe,text="Height:",justify="right",padding=4)
friendlyHeightEntry = ttk.Entry(pane13Labelframe, justify="center",textvariable=friendlyHeight)
friendlyHeightUnitLabel = ttk.Label(pane13Labelframe,text="m")
friendlyDispersionLabel = ttk.Label(pane13Labelframe,text="Dispersion:",justify="right",padding=4)
friendlyDispersionEntry = ttk.Entry(pane13Labelframe, justify="center",textvariable=friendlyDispersion)
friendlyDispersionUnitLabel = ttk.Label(pane13Labelframe,text="m")
friendlyAddButton = ttk.Button(pane13Labelframe,text="Add/Update",command=FriendlyPositionAddUpdate)
friendlyRemoveButton = ttk.Button(pane13Labelframe,text="Remove",command=lambda: FriendlyPositionRemove(name=friendlyName.get()))


pane1pane.add(pane14,weight=0)

pane2pane = ttk.PanedWindow(pane2,orient="vertical")
pane21 = ttk.Frame(pane2pane,height=200,padding=5)
pane22 = ttk.Frame(pane2pane,height=200,padding=5)
pane23 = ttk.Frame(pane2pane,height=200,padding=5)
pane2pane.add(pane21,weight=1)
pane21.grid_rowconfigure(0,weight=1)
pane21.grid_columnconfigure(0,weight=1)
targetInputLabelFrame = ttk.Labelframe(pane21,text="Create Target",height=200,width=500,padding=5,relief="groove")
targetInputLabelFrame.grid_rowconfigure(0,weight=1)
targetInputLabelFrame.grid_columnconfigure(0,weight=1)
targetInputFrame = ttk.Frame(targetInputLabelFrame)
targetInputFrame.grid_columnconfigure(0,minsize=30,weight=1)
targetInputFrame.grid_columnconfigure(1,minsize=30,weight=2)
targetInputFrame.grid_columnconfigure(2,minsize=10,weight=2)
targetInputFrame.grid_columnconfigure(3,minsize=6)
targetInputFrame.grid_columnconfigure(4,minsize=34,weight=4)
targetInputFrame.grid_rowconfigure((0,1,2,3,4,5),weight=1)
targetInputXYRadio = ttk.Radiobutton(targetInputFrame,text="LR - ",variable=xylrfpf,value=0)
targetInputLRRadio = ttk.Radiobutton(targetInputFrame,text="XY - ",variable=xylrfpf,value=1)
targetInputFPFRadio = ttk.Radiobutton(targetInputFrame,text="FPF- ",variable=xylrfpf,value=2)
xylrfpf.trace_add(mode="write",callback=TargetXYLRfpfChange)
targetInputReferenceEntry = ttk.Entry(targetInputFrame,width=3,textvariable=targetReference)
targetInputAddSeparator = ttk.Separator(targetInputFrame,orient="vertical")
targetInputSeparator = ttk.Separator(targetInputFrame,orient="horizontal")
targetInputGridLabel = ttk.Label(targetInputFrame,text="Position:",padding=4)
targetInputGridXEntry = ttk.Entry(targetInputFrame,justify="center",width=5,textvariable=targetPosX)
targetInputGridXEntry.bind("<Return>",TargetHeightAutoFill)
targetInputGridXEntry.bind("<Tab>",TargetHeightAutoFill)
targetInputGridYEntry = ttk.Entry(targetInputFrame,justify="center",width=5,textvariable=targetPosY)
targetInputGridYEntry.bind("<Return>",TargetHeightAutoFill)
targetInputGridYEntry.bind("<Tab>",TargetHeightAutoFill)
targetInputHeightLabel = ttk.Label(targetInputFrame,justify="right",text="Height:",padding=4)
targetInputHeightEntry = ttk.Entry(targetInputFrame,width=5,justify="center",textvariable=targetHeight)
targetInputHeightUnitLabel = ttk.Label(targetInputFrame,justify="left",text="m")
targetInputReferenceAdd = ttk.Button(targetInputFrame,text="Add",command=lambda *args: TargetAdd())

pane2pane.add(pane22,weight=1)
pane22.grid_rowconfigure(0,weight=1)
pane22.grid_columnconfigure(0,weight=1)
fireMissionSelectionLabelframe = ttk.Labelframe(pane22,text="Fire Mission Selection",height=200,width=500,padding=5,relief="groove")
fireMissionSelectionLabelframe.grid_columnconfigure((0,1,2,3),minsize=70,weight=1)
fireMissionSelectionLabelframe.grid_rowconfigure((0,1,2,3),weight=1)
fireMissionSelectionEffectLabelframe = ttk.Labelframe(fireMissionSelectionLabelframe,text="Effect")
fireMissionSelectionEffectLabelframe.grid_columnconfigure((0,2),weight=5)
fireMissionSelectionEffectLabelframe.grid_columnconfigure(1,weight=1)
fireMissionSelectionEffectLabelframe.grid_rowconfigure((0,1,2,3,4,5,6,7),weight=1)
fireMissionSelectionEffectDestroyRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Destroy",variable=fireMissionEffect,value="Destroy")
fireMissionSelectionEffectNeutraliseRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Neutralise",variable=fireMissionEffect,value="Neutralise")
fireMissionSelectionEffectCheckRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Check",variable=fireMissionEffect,value="Checkround")
fireMissionSelectionEffectSaturationRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Saturation",variable=fireMissionEffect,value="Saturate")
fireMissionSelectionEffectFPFRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="FPF",variable=fireMissionEffect,value="FPF")
fireMissionSelectionEffectAreaDenialRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Area Denial",variable=fireMissionEffect,value="Area_Denial")
fireMissionSelectionEffectSmokeRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Smoke",variable=fireMissionEffect,value="Smoke")
fireMissionSelectionEffectIllumRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Illum",variable=fireMissionEffect,value="Illum")
fireMissionEffect.set("0")
fireMissionEffect.trace_add(mode="write",callback=FireMissionEffectChange)
fireMissionSelectionUpdateMission = ttk.Button(fireMissionSelectionLabelframe,text="Update",command=lambda: FireMissionEffectUpdate())
fireMissionSelectionDispersionLabelframe = ttk.Labelframe(fireMissionSelectionLabelframe,text="Dispersion",padding=4)
fireMissionSelectionDispersionLabelframe.grid_columnconfigure(0,weight=1,minsize=30)
fireMissionSelectionDispersionLabelframe.grid_columnconfigure(1)
fireMissionSelectionDispersionLabelframe.grid_rowconfigure(0,weight=1)
fireMissionSelectionWidthLabel = ttk.Label(fireMissionSelectionDispersionLabelframe,text="Wid",padding=4,justify="right")
fireMissionSelectionDepthLabel = ttk.Label(fireMissionSelectionDispersionLabelframe,text="Dep",padding=4,justify="right")
fireMissionSelectionWidthCombobox = ttk.Combobox(fireMissionSelectionDispersionLabelframe,textvariable=fireMissionWidth,justify="right",width=4,values=("0","10","20","40","50","100","150","200","250"))
fireMissionWidth.set("0")
fireMissionSelectionDepthCombobox = ttk.Combobox(fireMissionSelectionDispersionLabelframe,textvariable=fireMissionDepth,justify="right",width=4,values=("0","10","20","40","50","100","150","200","250"))
fireMissionDepth.set("0")
fireMissionSelectionWidthUnitLabel = ttk.Label(fireMissionSelectionDispersionLabelframe,text="m",padding=4,justify="left")
fireMissionSelectionDepthUnitLabel = ttk.Label(fireMissionSelectionDispersionLabelframe,text="m",padding=4,justify="left")
fireMissionSelectionLengthLabelframe = ttk.Labelframe(fireMissionSelectionLabelframe,text="Length",padding=4)
fireMissionSelectionLengthLabelframe.grid_columnconfigure(0,weight=1,minsize=30)
fireMissionSelectionLengthLabelframe.grid_columnconfigure(1)
fireMissionSelectionLengthLabelframe.grid_rowconfigure(0,weight=1)
fireMissionSelectionLengthCombobox = ttk.Combobox(fireMissionSelectionLengthLabelframe,width=5,textvariable=fireMissionLength,justify="right",values=("30","Fig 1","90","Fig 2","Fig 3","Fig 4"))
fireMissionLength.set("Fig 1")
fireMissionLength.trace_add(mode="write",callback=FireMissionLengthChange)
fireMissionSelectionLengthUnitLabel = ttk.Label(fireMissionSelectionLengthLabelframe,text=" ",padding=4,justify="left")
fireMissionSelectionConditionLabelframe = ttk.Labelframe(fireMissionSelectionLabelframe,text="Condition",padding=4)
fireMissionSelectionConditionLabelframe.grid_columnconfigure(0,weight=1)
fireMissionSelectionConditionLabelframe.grid_rowconfigure(0,weight=1)
fireMissionSelectionConditionCombobox = ttk.Combobox(fireMissionSelectionConditionLabelframe,textvariable=fireMissionCondition,values=("FWR","Time"),width=10,justify="center")
fireMissionCondition.set("FWR")
fireMissionCondition.trace_add(mode="write",callback=FireMissionConditionChange)
fireMissionSelectionTimeLabelframe = ttk.Labelframe(fireMissionSelectionLabelframe,text="Time",padding=4)
fireMissionSelectionTimeLabelframe.grid_columnconfigure((0,2,4),minsize=20,weight=1)
fireMissionSelectionTimeLabelframe.grid_rowconfigure(0,weight=1)
fireMissionSelectionTimeHoursEntry = ttk.Entry(fireMissionSelectionTimeLabelframe,width=2,textvariable=fireMissionHour,justify="center")
fireMissionHour.set(datetime.now().strftime("%H"))
fireMissionSelectionTimeColonLabel1 = ttk.Label(fireMissionSelectionTimeLabelframe,text=" : ")
fireMissionSelectionTimeMinutesEntry = ttk.Entry(fireMissionSelectionTimeLabelframe,width=2,textvariable=fireMissionMinute,justify="center")
fireMissionMinute.set(datetime.now().strftime("%M"))
fireMissionSelectionTimeColonLabel2 = ttk.Label(fireMissionSelectionTimeLabelframe,text=" : ")
fireMissionSelectionTimeSecondsEntry = ttk.Entry(fireMissionSelectionTimeLabelframe,width=2,textvariable=fireMissionSecond,justify="center")
fireMissionSecond.set(datetime.now().strftime("%S"))
fireMissionSelectionPairedEffectLabelframe = ttk.Labelframe(fireMissionSelectionLabelframe,text="Paired Effect")
fireMissionSelectionPairedEffectLabelframe.grid_columnconfigure((0,1,2,3),weight=1)
fireMissionSelectionPairedEffectLabelframe.grid_rowconfigure((0,1,2,3),weight=1)
fireMissionSelectionPairedEffectLineRadio = ttk.Radiobutton(fireMissionSelectionPairedEffectLabelframe,text="Line",variable=fireMissionPairedEffect,value="Line")
fireMissionSelectionPairedEffectELineRadio = ttk.Radiobutton(fireMissionSelectionPairedEffectLabelframe,text="Explicit Line",variable=fireMissionPairedEffect,value="Explicit_Line")
fireMissionSelectionPairedEffectCreepingRadio = ttk.Radiobutton(fireMissionSelectionPairedEffectLabelframe,text="Creeping Barrage",variable=fireMissionPairedEffect,value="Creeping_Barrage")
fireMissionSelectionPairedEffectCreepingLabelframe = ttk.Labelframe(fireMissionSelectionLabelframe,text="Width")
fireMissionSelectionPairedEffectCreepingLabelframe.grid_columnconfigure(0,weight=1)
fireMissionSelectionPairedEffectCreepingLabelframe.grid_columnconfigure(1)
fireMissionSelectionPairedEffectCreepingLabelframe.grid_rowconfigure(0,weight=1)
fireMissionSelectionPairedEffectCreepingCombobox = ttk.Combobox(fireMissionSelectionPairedEffectCreepingLabelframe,justify="center",width=3,values=(100,150,200,250,300))
fireMissionSelectionPairedEffectCreepingUnitLabel = ttk.Label(fireMissionSelectionPairedEffectCreepingLabelframe,text="m",justify="left")
fireMissionSelectionPairedEffectSeriesRadio = ttk.Radiobutton(fireMissionSelectionPairedEffectLabelframe,text="Series",variable=fireMissionPairedEffect,value="Series")
fireMissionPairedEffect.set("-1")
fireMissionPairedEffect.trace_add(mode="write", callback = PairedMissionChange)
fireMissionSelectionPairedEffectAddButton = ttk.Button(fireMissionSelectionPairedEffectLabelframe,width=3,text="Add\nPaired\nMission",command=AddPairedMission)
pane2pane.add(pane23,weight=1)

#CLOCK
clockHandOffset = 0.0
def ClockOffsetTime(event):
    global clockHandOffset
    offset = clockOffset.get()
    if offset.isspace() == False or offset == "0":
        try: clockHandOffset = float(offset)
        except ValueError:
            common = Json_Load(source=0,localOverride=True)
            try:
                idfp = idfpNameCombobox["values"][int(common["IDFPSelection"][0])]
                fireMissions = Json_Load(source=4)
                time = fireMissions[idfp][offset]["TOF"]
                clockHandOffset = float(time)
                clockOffset.set(np.round(time*10)/10)
            except: clockHandOffset = 0
    else:
        clockHandOffset = 0.0
        clockOffset.set("0")

clockWidth,clockHeight,clockRadius,clockRim = 400,400,180,4
clockCenterX = clockWidth//2
clockCenterY = clockHeight//2
pane23.grid_rowconfigure(0,weight=1)
pane23.grid_columnconfigure(0,weight=1)
clockNotesNotebook = ttk.Notebook(pane23,width=420,height=450)
clockFrame = ttk.Frame(clockNotesNotebook,height=clockHeight,width=clockWidth,padding=5,relief="groove")
#clockFrame.grid_rowconfigure((0,1),weight=1)
clockFrame.grid_columnconfigure(0,weight=1)
clockCanvas = Canvas(clockFrame,width=clockWidth,height=clockHeight,bg="white")
clockOffsetFrame = ttk.Frame(clockFrame,padding=4)
clockOffsetFrame.grid_columnconfigure(0,weight=0,minsize=25)
clockOffsetFrame.grid_columnconfigure(1,weight=0,minsize=4)
clockOffsetFrame.grid_columnconfigure(2,weight=1,minsize=10)
clockOffsetFrame.grid_rowconfigure(0,weight=1)
clockOffsetLabel = ttk.Label(clockOffsetFrame,text="Splash Offset")
clockOffsetSeparator = ttk.Separator(clockOffsetFrame,orient="vertical")
clockOffsetEntry = ttk.Entry(clockOffsetFrame,textvariable=clockOffset,justify="left",width=10)
clockOffsetEntry.bind("<Return>",ClockOffsetTime)
def ClockApplySettings():
    try: Json_Save(source=0,newEntry={"clockSize":clockSize.get(),"clockRimWidth":clockRimWidth.get(),"clockFontSize":clockFontSize.get(),"clockHandSize":clockHandSize.get(),"clockSecHandSize":clockSecHandSize.get()},localOverride=True)
    except Exception as e: StatusMessageErrorDump(e,errorMessage="Failed to save clock settings to JSON")
    try:
        global clockWidth
        global clockHeight
        global clockRadius
        global clockRim
        global clockCenterX
        global clockCenterY
        global clockFont
        global clockHand
        global secClockHand
        outerBounds = int(clockSize.get())*1.05
        clockWidth,clockHeight,clockRadius,clockRim = outerBounds,outerBounds,int(np.round(float(clockSize.get())/2)),int(clockRimWidth.get())
        clockCenterX = clockWidth//2
        clockCenterY = clockHeight//2
        clockFont = int(np.round(float(clockFontSize.get())))
        clockHand = int(np.round(float(clockHandSize.get())))
        secClockHand = int(np.round(float(clockSecHandSize.get())))
    except Exception as e: StatusMessageErrorDump(e,errorMessage="Failed to set clock settings")
    clockCanvas.delete("all")
    DrawClockFace()
    
clockSettingsFrame = ttk.Frame(clockNotesNotebook,height=clockHeight,width=clockWidth,padding=5,relief="groove")
clockSettingsFrame.grid_columnconfigure(0,minsize=40)
clockSettingsFrame.grid_columnconfigure(1,minsize=9)
clockSettingsFrame.grid_columnconfigure(2,minsize=40,weight=1)
clockSettingsFrame.grid_columnconfigure(3,minsize=3)
clockSettingSizeLabel = ttk.Label(clockSettingsFrame,text="Size")
clockSettingRimWidthLabel = ttk.Label(clockSettingsFrame,text="Rim width")
clockSettingFontSizeLabel = ttk.Label(clockSettingsFrame,text="Font size")
clockSettingHandSizeLabel = ttk.Label(clockSettingsFrame,text="Hand Size")
clockSettingSecHandSizeLabel = ttk.Label(clockSettingsFrame,text="Sec. Hand Size")
clockSettingSeparator = ttk.Separator(clockSettingsFrame,orient="vertical")
clockSettingSizeFrame = ttk.Frame(clockSettingsFrame,padding=0)
clockSettingSizeFrame.grid_columnconfigure(0,minsize=10,weight=1)
clockSettingSizeFrame.grid_columnconfigure(1,minsize=5)
clockSettingSizeEntry = ttk.Entry(clockSettingSizeFrame,justify="left",textvariable=clockSize,width=5)
clockSettingSizeEntry.bind("<Return>",lambda event:ClockApplySettings())
clockSettingSizeUnitLabel = ttk.Label(clockSettingSizeFrame,text="Px")
clockSettingRimFrame = ttk.Frame(clockSettingsFrame,padding=0)
clockSettingRimFrame.grid_columnconfigure(0,minsize=10,weight=1)
clockSettingRimFrame.grid_columnconfigure(1,minsize=5)
clockSettingRimWidthEntry = ttk.Entry(clockSettingRimFrame,justify="left",textvariable=clockRimWidth,width=2)
clockSettingRimWidthEntry.bind("<Return>",lambda event:ClockApplySettings())
clockSettingRimUnitLabel = ttk.Label(clockSettingRimFrame,text="Px")
clockSettingFontFrame = ttk.Frame(clockSettingsFrame,padding=0)
clockSettingFontFrame.grid_columnconfigure(0,minsize=10,weight=1)
clockSettingFontFrame.grid_columnconfigure(1,minsize=5)
clockSettingFontSizeEntry = ttk.Entry(clockSettingFontFrame,justify="left",textvariable=clockFontSize,width=2)
clockSettingFontSizeEntry.bind("<Return>",lambda event:ClockApplySettings())
clockSettingFontUnitLabel = ttk.Label(clockSettingFontFrame,text="Px")
clockSettingHandSizeFrame = ttk.Frame(clockSettingsFrame,padding=0)
clockSettingHandSizeFrame.grid_columnconfigure(0,minsize=10,weight=1)
clockSettingHandSizeFrame.grid_columnconfigure(1,minsize=5)
clockSettingHandSizeEntry = ttk.Entry(clockSettingHandSizeFrame,justify="left",textvariable=clockHandSize,width=2)
clockSettingHandSizeEntry.bind("<Return>",lambda event:ClockApplySettings())
clockSettingHandSizeUnitLabel = ttk.Label(clockSettingHandSizeFrame,text="Px")
clockSettingSecHandSizeFrame = ttk.Frame(clockSettingsFrame,padding=0)
clockSettingSecHandSizeFrame.grid_columnconfigure(0,minsize=10,weight=1)
clockSettingSecHandSizeFrame.grid_columnconfigure(1,minsize=5)
clockSettingSecHandSizeEntry = ttk.Entry(clockSettingSecHandSizeFrame,justify="left",textvariable=clockSecHandSize,width=2)
clockSettingSecHandSizeEntry.bind("<Return>",lambda event:ClockApplySettings())
clockSettingSecHandSizeUnitLabel = ttk.Label(clockSettingSecHandSizeFrame,text="Px")
clockSettingApplyButton = ttk.Button(clockSettingsFrame,text="Apply",command=ClockApplySettings)
clockSettingPopoutButton = ttk.Button(clockSettingsFrame,text="P\no\np\no\nu\nt",width=3,command=ClockSettingsPopout)
noteFrame = ttk.Frame(clockNotesNotebook,height=clockHeight,width=clockWidth,padding=5,relief="groove")
noteFrame.grid_rowconfigure(0,weight=1)
noteFrame.grid_columnconfigure(0,weight=1)
noteText = Text(noteFrame,font=("Microsoft Tai Le",12),wrap="word")
def SaveNotes(): Json_Save(source=0,newEntry={"notes": noteText.get("1.0", END).strip()},localOverride=True)
def LoadNotes():
    try: noteText.insert(END,Json_Load(source=0,localOverride=True)["notes"])
    except: noteText.insert(END,"Pressing 'return' in this text box will save the contents")
noteText.bind("<Return>",lambda event:SaveNotes())
clockNotesNotebook.add(clockFrame,text="Clock",sticky="NESW",padding=1)
clockNotesNotebook.add(clockSettingsFrame,text="Clock Settings",sticky="NESW",padding=1)
clockNotesNotebook.add(noteFrame,text="Notes",sticky="NESW",padding=1)
clockFont = 14
clockTextSize = 0.9
clockHand = 5
secClockHand = 1
def DrawClockFace():
    clockCanvas["width"]=clockWidth
    clockCanvas["height"]=clockHeight
    if clockWidth>50:
        clockOffsetEntry["width"] = int(np.round(clockWidth/20))
    else: clockOffsetEntry["width"] = 3
    clockCanvas.create_oval(clockCenterX-clockRadius,clockCenterY-clockRadius,clockCenterX+clockRadius,clockCenterY+clockRadius,width=clockRim)
    for i in range(12):
        angle = np.radians(i*30)
        sinA = np.sin(angle)
        cosA = np.cos(angle)
        if i in [3,6,9,0]:
            innerRadius = clockRadius * 0.65
            outerRadius = clockRadius * 0.8
            HandSize = clockRadius * clockTextSize
            width = clockRim
            numeral = {0: "12", 3: "3", 6: "6", 9: "9"}[i]
            xText = clockCenterX + HandSize * sinA
            yText = clockCenterY - HandSize * cosA
            clockCanvas.create_text(xText,yText,text=numeral,font=("Microsoft Tai Le",clockFont,"bold"))
        else:
            innerRadius = clockRadius * 0.75
            outerRadius = clockRadius * 0.95
            HandSize = clockRadius * (clockTextSize-0.1)
            width = clockRim/2
        xOuter = clockCenterX + outerRadius * sinA
        yOuter = clockCenterY - outerRadius * cosA
        xInner = clockCenterX + innerRadius * sinA
        yInner = clockCenterY - innerRadius * cosA
        clockCanvas.create_line(xInner,yInner,xOuter,yOuter,width=width)
    for i in range(60):
        if i not in [15,30,45,0]:
            angle = np.radians(i * 6)
            sinA = np.sin(angle)
            cosA = np.cos(angle)

            outer = clockRadius*0.95
            inner = clockRadius*0.85
            xOuter = clockCenterX + outer * sinA
            yOuter = clockCenterY - outer * cosA
            xInner = clockCenterX + inner * sinA
            yInner = clockCenterY - inner * cosA
            clockCanvas.create_line(xInner,yInner,xOuter,yOuter,width=1)
    clockCanvas.create_text(clockCenterX,clockCenterY+clockRadius/2,text="ZULU",fill="lightgrey",font=("Microsoft Tai Le",clockFont,"bold"))
def UpdateClock():
    clockCanvas.delete("hand")
    now = datetime.now(timezone.utc)
    microsecond = now.microsecond
    second = now.second + microsecond /1000000
    minute = now.minute
    hour = now.hour % 12

    offSecAngle = np.radians(second*6-clockHandOffset*6)
    secAngle = np.radians(second*6)
    minAngle = np.radians(minute * 6 + second * 0.1)
    hourAngle = np.radians(hour *30 + minute * 0.5)

    if clockHandOffset!= 0.0:
        xOffSec = clockCenterX + clockRadius * 0.9 * np.sin(offSecAngle)
        yOffSec = clockCenterY - clockRadius * 0.9 * np.cos(offSecAngle)
        clockCanvas.create_line(clockCenterX,clockCenterY, xOffSec,yOffSec,fill="red",width=secClockHand,tag="hand")
        if clockHandOffset < 60.0: clockCanvas.create_arc(int(clockCenterX-clockRadius/2),int(clockCenterY-clockRadius/2),int(clockCenterX+clockRadius/2),int(clockCenterY+clockRadius/2),start=-np.rad2deg(secAngle-np.pi/2),extent=clockHandOffset*6,style=PIESLICE,fill="#FFAAAA",outline="#FF0000",tag="hand",width=secClockHand)
        elif clockHandOffset < 120:
            clockCanvas.create_arc(int(clockCenterX-clockRadius/1.5),int(clockCenterY-clockRadius/1.5),int(clockCenterX+clockRadius/1.5),int(clockCenterY+clockRadius/1.5),start=-np.rad2deg(secAngle-np.pi/2),extent=clockHandOffset*6,style=PIESLICE,fill="#FFAAAA",outline="#FF0000",tag="hand",width=secClockHand)
            clockCanvas.create_oval(int(clockCenterX-clockRadius/2),int(clockCenterY-clockRadius/2),int(clockCenterX+clockRadius/2),int(clockCenterY+clockRadius/2),fill="#FF7777",outline="#FF0000",tag="hand",width=secClockHand)
    xSec = clockCenterX + clockRadius * 0.9 * np.sin(secAngle)
    ySec = clockCenterY - clockRadius * 0.9 * np.cos(secAngle)
    xSecCircle = clockCenterX + (clockRadius * 0.9+5) * np.sin(secAngle)
    ySecCircle = clockCenterY - (clockRadius * 0.9+5) * np.cos(secAngle)
    clockCanvas.create_line(clockCenterX,clockCenterY, xSec,ySec,fill="blue",width=secClockHand,tag="hand")
    clockCanvas.create_oval(xSecCircle-5,ySecCircle-5,xSecCircle+5,ySecCircle+5,width=secClockHand,outline="blue",tag="hand")
    xMin = clockCenterX + clockRadius * 0.75 * np.sin(minAngle)
    YMin = clockCenterY - clockRadius * 0.75 * np.cos(minAngle)
    clockCanvas.create_line(clockCenterX,clockCenterY, xMin,YMin,fill="black",width=int(np.round(clockHand/2)),tag="hand")
    clockCanvas.create_oval(xMin-int(np.round(clockHand/4)),YMin-int(np.round(clockHand/4)),xMin+int(np.round(clockHand/4)),YMin+int(np.round(clockHand/4)),fill="black",outline="black",tag="hand")
    xHour = clockCenterX + clockRadius * 0.5 * np.sin(hourAngle)
    yHour = clockCenterY - clockRadius * 0.5 * np.cos(hourAngle)
    clockCanvas.create_line(clockCenterX,clockCenterY, xHour,yHour,fill="black",width=int(np.round(clockHand)),tag="hand")
    clockCanvas.create_oval(clockCenterX-int(np.round(clockHand)/2),clockCenterY-int(np.round(clockHand)/2),clockCenterX+int(np.round(clockHand)/2),clockCenterY+int(np.round(clockHand)/2),fill="black",outline="black",tag="hand")
    clockCanvas.create_oval(xHour-int(np.round(clockHand)/2),yHour-int(np.round(clockHand)/2),xHour+int(np.round(clockHand)/2),yHour+int(np.round(clockHand)/2),fill="black",outline="black",tag="hand")
    delay = int(50 - (microsecond / 1000) % 50)
    if delay == 0: delay = 50
    root.after(delay, UpdateClock)

DrawClockFace()
UpdateClock()

def TerrainFolderCheck():
    global terrainTrace
    for terrainFolder in terrainsFolders[0]: 
        terrain_menu.add_radiobutton(label=terrainFolder,variable=terrain,value=terrainFolder)
    terrainTrace = terrain.trace_add(mode="write",callback=TerrainChange)


pane3pane = ttk.PanedWindow(pane3,orient="vertical")
pane31 = ttk.Frame(pane3pane,height=200,padding=5)
pane31.grid_columnconfigure(0,weight=1)
pane31.grid_rowconfigure(0,weight=1)
pane32 = ttk.Frame(pane3pane,height=200,padding=5)
pane33 = ttk.Frame(pane3pane,height=200,padding=5)
pane3pane.add(pane31)
targetListLabelframe = ttk.Labelframe(pane31,text="Target List",height=200,width=500,padding=5,relief="groove")
targetListLabelframe.grid_columnconfigure((0,1,2,3,4),weight=1)
targetListLabelframe.grid_columnconfigure(5,weight=10000)
targetListLabelframe.grid_rowconfigure((0,1),minsize=30)

targetListEditImage = PhotoImage(file=exeDir/"Functions"/"edit.png")
targetListCalcImage = PhotoImage(file=exeDir/"Functions"/"calc.png")
targetListHeaderImageEmpty = ttk.Frame(targetListLabelframe,width=25)
targetListSeriesEditImage = ttk.Label(targetListLabelframe,image=targetListEditImage)
targetListSeriesCalcImage = ttk.Label(targetListLabelframe,image=targetListCalcImage)
targetListHeaderSeparator = ttk.Separator(targetListLabelframe,orient="vertical")
targetListIndexEditImage = ttk.Label(targetListLabelframe,image=targetListEditImage)
targetListIndexCalcImage = ttk.Label(targetListLabelframe,image=targetListCalcImage)
targetListSeriesEditImage.image = targetListEditImage
targetListSeriesCalcImage.image = targetListCalcImage
targetListIndexEditImage.image = targetListEditImage
targetListIndexCalcImage.image = targetListCalcImage
targetListCalculate = ttk.Button(targetListLabelframe,text="Calculate",command=Calculate,image=targetListCalcImage,compound="left")
targetListCalculate.image = targetListCalcImage
targetListFrame = ttk.Frame(targetListLabelframe)
targetListFrame.grid_columnconfigure(0,weight=1)
targetListFrame.grid_rowconfigure(0,weight=1)
targetListPanedwindow = ttk.Panedwindow(targetListFrame,orient="vertical")

targetListPanedwindowLRFrame = ttk.Frame(targetListPanedwindow,padding="5")
targetListPanedwindowXYFrame = ttk.Frame(targetListPanedwindow,padding="5")
targetListPanedwindowFPFFrame = ttk.Frame(targetListPanedwindow,padding="5")
targetListPanedwindowComboFrame = ttk.Frame(targetListPanedwindow,padding="5")
targetListPanedwindowEmptyFrame = ttk.Frame(targetListPanedwindow,padding="5")
targetListPanedwindow.add(targetListPanedwindowLRFrame,weight=1)
targetListPanedwindow.add(targetListPanedwindowXYFrame,weight=1)
targetListPanedwindow.add(targetListPanedwindowFPFFrame,weight=1)
targetListPanedwindow.add(targetListPanedwindowComboFrame,weight=1)
targetListPanedwindow.add(targetListPanedwindowEmptyFrame,weight=0)
targetListPanedwindowLRFrame.grid_columnconfigure(0)
targetListPanedwindowLRFrame.grid_rowconfigure(0,weight=1)
targetListPanedwindowXYFrame.grid_columnconfigure(0)
targetListPanedwindowXYFrame.grid_rowconfigure(0,weight=1)
targetListPanedwindowFPFFrame.grid_columnconfigure(0)
targetListPanedwindowFPFFrame.grid_rowconfigure(0,weight=1)
targetListPanedwindowComboFrame.grid_columnconfigure(0)
targetListPanedwindowComboFrame.grid_rowconfigure(0,weight=1)

targetContextMenu = Menu(root,tearoff=False)
targetListLRLabelframe = ttk.Labelframe(targetListPanedwindowLRFrame,text="LR",padding=5,relief="groove")
targetListLRCanvas = Canvas(targetListLRLabelframe,bg="white",width=128,height=120)
targetListLRCanvasFrame = ttk.Frame(targetListLRCanvas, padding=10)
targetListLRCanvas.create_window((0, 0), window=targetListLRCanvasFrame, anchor="nw")
targetListLRScrollbar = ttk.Scrollbar(targetListLRLabelframe, orient="vertical", command=targetListLRCanvas.yview)
targetListLRCanvas.configure(yscrollcommand=targetListLRScrollbar.set)
targetListLRCanvas.pack(side="left", fill="both", expand=True)
targetListLRLabelframe.grid(row=0, column=0, sticky="nsew")
targetListLRScrollbar.pack(side="right", fill="y")
sortedLRItems = Sort_FireMissions(listCheckBox_vars["LR"])


targetListXYLabelframe = ttk.Labelframe(targetListPanedwindowXYFrame,text="XY",padding=5,relief="groove")
targetListXYCanvas = Canvas(targetListXYLabelframe,bg="white",width=128,height=120)
targetListXYCanvasFrame = ttk.Frame(targetListXYCanvas, padding=10)
targetListXYCanvas.create_window((0, 0), window=targetListXYCanvasFrame, anchor="nw")
targetListXYScrollbar = ttk.Scrollbar(targetListXYLabelframe, orient="vertical", command=targetListXYCanvas.yview)
targetListXYCanvas.configure(yscrollcommand=targetListXYScrollbar.set)
targetListXYCanvas.pack(side="left", fill="both", expand=True)
targetListXYLabelframe.grid(row=0, column=0, sticky="nsew")
targetListXYScrollbar.pack(side="right", fill="y")
sortedXYItems = Sort_FireMissions(listCheckBox_vars["XY"])


targetListFPFLabelframe = ttk.Labelframe(targetListPanedwindowFPFFrame,text="FPF",padding=5,relief="groove")
targetListFPFCanvas = Canvas(targetListFPFLabelframe,bg="white",width=128,height=120)
targetListFPFCanvasFrame = ttk.Frame(targetListFPFCanvas, padding=10)
targetListFPFCanvas.create_window((0, 0), window=targetListFPFCanvasFrame, anchor="nw")
targetListFPFScrollbar = ttk.Scrollbar(targetListFPFLabelframe, orient="vertical", command=targetListFPFCanvas.yview)
targetListFPFCanvas.configure(yscrollcommand=targetListFPFScrollbar.set)
targetListFPFCanvas.pack(side="left", fill="both", expand=True)
targetListFPFLabelframe.grid(row=0, column=0, sticky="nsew")
targetListFPFScrollbar.pack(side="right", fill="y")
sortedFPFItems = Sort_FireMissions(listCheckBox_vars["FPF"])


targetListComboLabelframe = ttk.Labelframe(targetListPanedwindowComboFrame,text="Grouped",padding=5,relief="groove")
targetListComboCanvas = Canvas(targetListComboLabelframe,bg="white",height=120)
targetListComboCanvasFrame = ttk.Frame(targetListComboCanvas, padding=10)
targetListComboCanvas.create_window((0, 0), window=targetListComboCanvasFrame, anchor="nw")
targetListComboScrollbar = ttk.Scrollbar(targetListComboLabelframe, orient="vertical", command=targetListComboCanvas.yview)
targetListComboCanvas.configure(yscrollcommand=targetListComboScrollbar.set)
targetListComboCanvas.pack(side="left", fill="both", expand=True)
targetListComboLabelframe.grid(row=0, column=0, sticky="nsew")
targetListComboScrollbar.pack(side="right", fill="y")
sortedComboItems = Sort_FireMissions(listCheckBox_vars["Combo"])


pane3pane.add(pane32)
#mapLabelFrame = ttk.LabelFrame(pane32,text="Map",width=50,height=50)
pane3pane.add(pane33)

idfpNotebook = ttk.Notebook(pane4,width=500)

#MAP NOTEBOOK PAGE
mapPagePanedWindow = ttk.Panedwindow(notePage2,orient="horizontal")
mapPagePane0 = ttk.Frame(mapPagePanedWindow,width=800,padding=1)
mapPagePane1 = ttk.Frame(mapPagePanedWindow,width=400,padding=1)
mapPagePane2 = ttk.Frame(mapPagePanedWindow,width=400,padding=1)
mapPagePanedWindow.add(mapPagePane0)
mapPagePanedWindow.add(mapPagePane1)
mapPagePanedWindow.add(mapPagePane2)
mapPagePane0.grid_rowconfigure(0,weight=1)
mapPagePane0.grid_columnconfigure(0,weight=1)
mapPagePane1.grid_rowconfigure(0,weight=1)
mapPagePane1.grid_columnconfigure(0,weight=1)
mapPagePane2.grid_rowconfigure(0,weight=1)
mapPagePane2.grid_columnconfigure(0,weight=1)
mapPageFrame0 = ttk.Frame(mapPagePane0,height=800,width=800,padding=5)
mapPageFrame1 = ttk.Frame(mapPagePane1,height=400,width=400,padding=5)
mapPageFrame2 = ttk.Frame(mapPagePane2,height=400,width=400,padding=5)

root.config(menu=menubar)
system_menu = Menu(menubar,tearoff=False)
system_menu.add_radiobutton(label="M6",variable=system,value="M6")
system_menu.add_radiobutton(label="L16",variable=system,value="L16")
system_menu.add_radiobutton(label="L119",variable=system,value="L119")
system_menu.add_radiobutton(label="Sholef",variable=system,value="Sholef")
idfpSystemFrame.bind("<Button-3>",lambda event : system_menu.post(event.x_root,event.y_root))
idfpSystemOutput.bind("<Button-3>",lambda event : system_menu.post(event.x_root,event.y_root))
idfpSystemLabel.bind("<Button-3>",lambda event : system_menu.post(event.x_root,event.y_root))
idfpSystemSep.bind("<Button-3>",lambda event : system_menu.post(event.x_root,event.y_root))
terrain_menu = Menu(menubar,tearoff=False)

terrainValue = StringVar()
terrain_menu.add_command(label="Install New Height Map (Keithenneu)",command=HeightMapFileDialog)
terrain_menu.add_separator()

flipPaneSide = StringVar()
fmEditSafetyToggle = StringVar()
flipPaneSide.set(0)
settings_menu = Menu(menubar,tearoff=False)
login_menu = Menu(settings_menu,tearoff=False)
settings_menu.add_cascade(label="UKSF Login",menu=login_menu)
login_menu.add_command(label="Login",command=LoginWindow)
login_menu.add_command(label="Logout",state="disabled",command=Logout)
settings_menu.add_command(label="Flip window panes", command=FlipWindowPanes)
settings_menu.add_checkbutton(label="Target edit safety",offvalue= 0,onvalue= 1, variable=fmEditSafetyToggle)
fmEditSafetyToggle.set(1)
fmEditSafetyToggle.trace_add(mode="write",callback=RequestEditFireMissionsFromSafety)

create_checkboxes(targetListLRCanvasFrame, {key: listCheckBox_vars["LR"][key] for key in sortedLRItems},seriesDict["LR"])
create_checkboxes(targetListXYCanvasFrame, {key: listCheckBox_vars["XY"][key] for key in sortedXYItems},seriesDict["XY"])
create_checkboxes(targetListFPFCanvasFrame, {key: listCheckBox_vars["FPF"][key] for key in sortedFPFItems},seriesDict["FPF"],True)
create_checkboxes(targetListComboCanvasFrame, {key: listCheckBox_vars["Combo"][key] for key in sortedComboItems},seriesDict["Combo"])
resetSafety = StringVar()
reset_menu = Menu(menubar,tearoff=False)
reset_firemission_menu = Menu(reset_menu,tearoff=False)
reset_menu.add_command(label="Status Log",command=ClearMessageLog,state="disabled")
reset_menu.add_separator()
reset_firemission_menu.add_command(label="All",command=ClearFireMission)
reset_firemission_menu.add_separator()
reset_firemission_menu.add_command(label="FPF",command=lambda: ClearFireMission(mission="FPF",calculated=True))
reset_firemission_menu.add_command(label="LR",command=lambda: ClearFireMission(mission="LR",calculated=True))
reset_firemission_menu.add_command(label="XY",command=lambda: ClearFireMission(mission="XY",calculated=True))
reset_menu.add_command(label="IDFP Position(s)",command=ClearIDFP,state="disabled")
reset_menu.add_command(label="Friendly Position(s)",command=ClearFriendlyPositions,state="disabled")
reset_menu.add_cascade(label="Fire Missions",menu=reset_firemission_menu,state="disabled")
reset_menu.add_separator()
reset_menu.add_command(label="All Positions",command=ClearAll,state="disabled")
reset_menu.add_separator()
reset_menu.add_checkbutton(label="Safety Toggle",onvalue=1,offvalue=0,variable=resetSafety)
resetSafety.trace_add(mode = "write", callback=ClearSafety)
resetSafety.set(1)

style_menu = Menu(menubar,tearoff=False)
style_menu.add_command(label="Clam",command=lambda: ttk.Style().theme_use('clam'))
style_menu.add_command(label="Winnative",command=lambda: ttk.Style().theme_use('winnative'))
style_menu.add_command(label="Vista",command=lambda: ttk.Style().theme_use('vista'))
style_menu.add_command(label="Alt",command=lambda: ttk.Style().theme_use('alt'))
style_menu.add_command(label="Default",command=lambda: ttk.Style().theme_use('default'))
style_menu.add_command(label="Classic",command=lambda: ttk.Style().theme_use('classic'))

help_menu = Menu(menubar,tearoff=False)
help_menu.add_command(label=version)

menubar.add_cascade(label="System",menu=system_menu)
menubar.add_cascade(label="Terrain",menu=terrain_menu)
menubar.add_cascade(label="Settings",menu=settings_menu)
menubar.add_cascade(label="Clear",menu=reset_menu)
menubar.add_cascade(label="Style",menu=style_menu)
menubar.add_cascade(label="Help",menu=help_menu,underline=0)

systemTrace = system.trace_add(mode = "write", callback=lambda *args: SystemChange(newSystem=system.get(),set=True))

window=root.winfo_toplevel()
window.minsize(950,650)
window.rowconfigure(0,weight=1)
window.columnconfigure(0,weight=1)
content.grid(column="0",row="0",sticky="NESW")
mainframe.grid(column="0",row="0",sticky="NESW",padx=4, pady=4)
mainNotebook.grid(column="0",row="0",sticky="NESW")
fireMissionPagePanedWindow.grid(column="0",row="0",sticky="NWS")
pane1pane.grid(column="0",row="0",sticky="NEWS")
pane11Labelframe.grid(column="0",row="0",sticky="NEW")

idfpCreationFrame.grid(column="0",row="0",sticky="NESW")
idfpNameLabel.grid(column="0",row="0",sticky="NE")
idfpNameCombobox.grid(column="1",columnspan=2,row="0",sticky="NEW")
idfpPosLabel.grid(column=0,row=1,sticky="NES")
idfpPosXEntry.grid(column=1,row=1,sticky="NEW")
idfpPosYEntry.grid(column=2,row=1,sticky="NEW")
idfpHeightLabel.grid(column=0,row=2,sticky="NES")
idfpHeightFrame.grid(column=1,row=2,sticky="NEW")
idfpHeightEntry.grid(column=0,row=0,sticky="NEW")
idfpHeightUnitLabel.grid(column=1,row=0,sticky="NW")
idfpButtonFrame.grid(column=2,row=2,rowspan=3,sticky="NEW")
idfpSystemFrame.grid(column=0,row=0,sticky="NEWS")
idfpSystemLabel.grid(column=0,row=0,sticky="NWS")
idfpSystemSep.grid(column=1,row=0,sticky="NS")
idfpSystemOutput.grid(column=2,row=0,sticky="NSE")
idfpAddButton.grid(column=0,row=1,sticky="NEW")
idfpRemoveButton.grid(column=0,row=2,sticky="NEW")
idfpSeparator.grid(column=0,columnspan=2,row=3,sticky="EW",pady=4)
idfpControlFrame.grid(column=0,columnspan=2,row=4,sticky="NEW")
idfpEditChargeLabel.grid(column=0,row=0,sticky="NE")
idfpChargeFrame.grid(column=1,row=0,sticky="NEW")
idfpEditChargeCheckbox.grid(column=0,row=0,sticky="NE")
idfpEditChargeComboBox.grid(column=1,row=0,sticky="NEW")
idfpEditTrajLabel.grid(column=0,row=1,sticky="NE")
idfpEditTrajComboBox.grid(column=1,row=1,sticky="NEW")

idfpListBoxFrame.grid(column="0",row="1",sticky="NEWS")
idfpListbox.grid(column="0",row="0",sticky="NEW")
#idfpEditLabelFrame.grid(column="0",row="1",sticky="NEW")
# idfpEditChargeCheckbox.grid(column="0",row="0",sticky="NES")
# idfpEditChargeLabel.grid(column="1",row="0",sticky="NS")
# idfpEditChargeComboBox.grid(column="2",row="0",sticky="NW")
# #idfpEditSeparator.grid(column=0,row="1",columnspan=4,sticky="NESW")
# idfpEditTrajLabel.grid(column="1",row="2",sticky="NS")
# idfpEditTrajComboBox.grid(column="2",row="2",sticky="NW")

pane12Labelframe.grid(column="0",row="0",sticky="NEW")

airLabelFrame.grid(column="0",row="0",sticky="NEW",pady=5)
airSeparator.grid(column=1,row=0,rowspan=3,sticky="NESW")
temperatureLabel.grid(column="0",row="0",sticky="E")
temperatureEntry.grid(column="2",row="0",sticky="E",padx=4)
temperatureUnits.grid(column="3",row="0",sticky="W",padx=4)
humidityLabel.grid(column="0",row="1",sticky="E")
humidityEntry.grid(column="2",row="1",sticky="E",padx=4)
humidityUnits.grid(column="3",row="1",sticky="W",padx=4)
pressureLabel.grid(column="0",row="2",sticky="E")
pressureEntry.grid(column="2",row="2",sticky="E",padx=4)
pressureUnits.grid(column="3",row="2",sticky="W",padx=4)
windLabelFrame.grid(column="0",row="1",sticky="NEW",pady=5)
windSeparator.grid(column=1,row=0,rowspan=3,sticky="NESW")
directionLabel.grid(column=0,row=0,sticky="E")
directionEntry.grid(column=2,row=0,sticky="E",padx=4)
directionUnits.grid(column=3,row=0,sticky="W",padx=4)
magnitudeLabel.grid(column=0,row=1,sticky="E")
magnitudeEntry.grid(column=2,row=1,sticky="E",padx=4)
magnitudeUnits.grid(column=3,row=1,sticky="W",padx=4)
dynamicLabel.grid(column=0,row=2,sticky="NSE")
dynamicCheckBox.grid(column=2,row=2,sticky="NSE")
pane13Labelframe.grid(column="0",row="0",sticky="NEW")
friendlyNameLabel.grid(column="0",row="0",sticky="NE")
friendlyNameCombobox.grid(column="1",row="0",columnspan=3,sticky="NEW")
friendlyPosLabel.grid(column="0",row="1",sticky="NE")
friendlyPosXEntry.grid(column="1",row="1",columnspan=2,sticky="NEW")
friendlyPosYEntry.grid(column="3",row="1",sticky="NEW")
friendlyHeightLabel.grid(column="0",row="2",sticky="E")
friendlyHeightEntry.grid(column="1",row="2",sticky="EW")
friendlyHeightUnitLabel.grid(column="2",row="2",sticky="W")
friendlyDispersionLabel.grid(column="0",row="3",sticky="E")
friendlyDispersionEntry.grid(column="1",row="3",sticky="EW")
friendlyDispersionUnitLabel.grid(column="2",row="3",sticky="W")
friendlyAddButton.grid(column="3",row="2",sticky="NESW")
friendlyRemoveButton.grid(column="3",row="3",sticky="NESW")


pane2pane.grid(column="0",row="0",sticky="NEWS")
targetInputLabelFrame.grid(column="0",row="0",sticky="NEW")
targetInputFrame.grid(column="0",row="0",sticky="NEW")
targetInputXYRadio.grid(column="0",row="0",sticky="E")
targetInputLRRadio.grid(column="0",row="1",sticky="E")
targetInputFPFRadio.grid(column="0",row="2",sticky="E")
targetInputReferenceEntry.grid(column="1",row="0",rowspan=3,columnspan=2,sticky="W")
targetInputAddSeparator.grid(column="3",row="0",rowspan=2,sticky="NESW")
targetInputReferenceAdd.grid(column="4",row="0",rowspan=2,sticky="EW")
targetInputSeparator.grid(column="0",row="3",columnspan=5,sticky="EW")
targetInputGridLabel.grid(column="0",row="4",sticky="E")
targetInputGridXEntry.grid(column="1",row="4",columnspan=2,sticky="NEW")
targetInputGridYEntry.grid(column="3",row="4",columnspan=2,sticky="NEW")
targetInputHeightLabel.grid(column="0",row="5",sticky="E")
targetInputHeightEntry.grid(column="1",row="5",sticky="EW")
targetInputHeightUnitLabel.grid(column="2",row="5",sticky="W")

fireMissionSelectionLabelframe.grid(column="0",row="0",sticky="NEW")
fireMissionSelectionEffectLabelframe.grid(column="0",row="0",rowspan=2,sticky="NEW",padx=4)
fireMissionSelectionEffectFPFRadio.grid(column="1",row="0",rowspan="7",sticky="EW",padx=4)
fireMissionSelectionEffectFPFRadio.grid_remove()
fireMissionSelectionEffectDestroyRadio.grid(column="1",row="0",sticky="EW",padx=4)
fireMissionSelectionEffectNeutraliseRadio.grid(column="1",row="1",sticky="EW",padx=4)
fireMissionSelectionEffectCheckRadio.grid(column="1",row="2",sticky="EW",padx=4)
fireMissionSelectionEffectSaturationRadio.grid(column="1",row="3",sticky="EW",padx=4)
fireMissionSelectionEffectAreaDenialRadio.grid(column="1",row="5",sticky="EW",padx=4)
fireMissionSelectionEffectSmokeRadio.grid(column="1",row="6",sticky="EW",padx=4)
fireMissionSelectionEffectIllumRadio.grid(column="1",row="7",sticky="EW",padx=4)
fireMissionSelectionUpdateMission.grid(column="0",row="2",sticky="NESW",padx=4)
fireMissionSelectionUpdateMission.grid_remove()
fireMissionSelectionDispersionLabelframe.grid(column="1",row="0",sticky="NEW",padx=4)
fireMissionSelectionWidthLabel.grid(column="0",row="0",sticky="NEW")
fireMissionSelectionDepthLabel.grid(column="0",row="1",sticky="NEW")
fireMissionSelectionWidthCombobox.grid(column="1",row="0",sticky="NEW")
fireMissionSelectionDepthCombobox.grid(column="1",row="1",sticky="NEW")
fireMissionSelectionWidthUnitLabel.grid(column="2",row="0",sticky="NW")
fireMissionSelectionDepthUnitLabel.grid(column="2",row="1",sticky="NW")
fireMissionSelectionLengthLabelframe.grid(column="2",row="0",sticky="NEW",padx=4)
fireMissionSelectionLengthCombobox.grid(column="0",row="0",sticky="NEW")
fireMissionSelectionLengthUnitLabel.grid(column="1",row="0",sticky="NW")
fireMissionSelectionConditionLabelframe.grid(column="3",row="0",sticky="NEW",padx=4)
fireMissionSelectionConditionCombobox.grid(column="0",row="0",sticky="NEW")
fireMissionSelectionTimeLabelframe.grid(column="2",row="1",columnspan=2,sticky="NEW",padx=4)
fireMissionSelectionTimeHoursEntry.grid(column="0",row="0",sticky="NEW")
fireMissionSelectionTimeColonLabel1.grid(column="1",row="0",sticky="NEW")
fireMissionSelectionTimeMinutesEntry.grid(column="2",row="0",sticky="NEW")
fireMissionSelectionTimeColonLabel2.grid(column="3",row="0",sticky="NEW")
fireMissionSelectionTimeSecondsEntry.grid(column="4",row="0",sticky="NEW")
fireMissionSelectionPairedEffectLabelframe.grid(column="0",row="3",columnspan=4,sticky="NEW",padx=4)
fireMissionSelectionPairedEffectLabelframe.grid_remove()
fireMissionSelectionPairedEffectLineRadio.grid(column="1",row="0",sticky="NEW")
fireMissionSelectionPairedEffectELineRadio.grid(column="1",row="1",sticky="NEW")
fireMissionSelectionPairedEffectCreepingRadio.grid(column="1",row="2",sticky="NEW")
fireMissionSelectionPairedEffectSeriesRadio.grid(column="1",row="3",sticky="NEW")
fireMissionSelectionPairedEffectCreepingLabelframe.grid(column="2",row="2",sticky="EW",padx=4,pady=2)
fireMissionSelectionPairedEffectCreepingCombobox.grid(column="0",row="0",sticky="EW")
fireMissionSelectionPairedEffectCreepingUnitLabel.grid(column="1",row="0",sticky="W")
fireMissionSelectionPairedEffectAddButton.grid(column="3",row="0",rowspan=4,sticky="EW")

clockNotesNotebook.grid(column="0",row="0",sticky="NEW")
#clockFrame.grid(column="0",row="0",sticky="NEW")
clockCanvas.grid(column="0",row="0",sticky="NW")
clockOffsetFrame.grid(column="0",row="1",sticky="NESW")
clockOffsetLabel.grid(column="0",row="0",sticky="NES")
clockOffsetSeparator.grid(column="1",row="0",sticky="NS")
clockOffsetEntry.grid(column="2",row="0",sticky="NSW")
#clockSettingsFrame.grid(column="0",row="0",sticky="NESW")
clockSettingSizeLabel.grid(column="0",row="0",sticky="NE")
clockSettingRimWidthLabel.grid(column="0",row="1",sticky="NE")
clockSettingFontSizeLabel.grid(column="0",row="2",sticky="NE")
clockSettingHandSizeLabel.grid(column="0",row="3",sticky="NE")
clockSettingSecHandSizeLabel.grid(column="0",row="4",sticky="NE")
clockSettingSeparator.grid(column="1",row="0",rowspan="5",sticky="NS")
clockSettingSizeFrame.grid(column="2",row="0",sticky="NW",pady=4)
clockSettingSizeEntry.grid(column="0",row="0",sticky="NW")
clockSettingSizeUnitLabel.grid(column="1",row="0",sticky="SW")
clockSettingPopoutButton.grid(column="3",row="0",rowspan=6,sticky="NS")
clockSettingRimFrame.grid(column="2",row="1",sticky="NW",pady=4)
clockSettingRimWidthEntry.grid(column="0",row="0",sticky="NW")
clockSettingRimUnitLabel.grid(column="1",row="0",sticky="SW")
clockSettingFontFrame.grid(column="2",row="2",sticky="NW",pady=4)
clockSettingFontSizeEntry.grid(column="0",row="0",sticky="NW")
clockSettingFontUnitLabel.grid(column="1",row="0",sticky="SW")
clockSettingHandSizeFrame.grid(column="2",row="3",sticky="NW",pady=4)
clockSettingHandSizeEntry.grid(column="0",row="0",sticky="NW")
clockSettingHandSizeUnitLabel.grid(column="1",row="0",sticky="SW")
clockSettingSecHandSizeFrame.grid(column="2",row="4",sticky="NW",pady=4)
clockSettingSecHandSizeEntry.grid(column="0",row="0",sticky="NW")
clockSettingSecHandSizeUnitLabel.grid(column="1",row="0",sticky="SW")
clockSettingApplyButton.grid(column="0",columnspan="3",row="5",sticky="NESW",pady="4")
# noteFrame.grid(column="0",row="0",sticky="NESW")
noteText.grid(column="0",row="0",sticky="NESW")

pane3pane.grid(column="0",row="0",sticky="NEWS")
targetListLabelframe.grid(column="0",row="0",sticky="NESW")
targetListHeaderImageEmpty.grid(row="0", column="0", sticky="NW")
targetListSeriesEditImage.grid(row="0", column="1", sticky="NW")
targetListSeriesCalcImage.grid(row="0", column="2", sticky="NW")
targetListHeaderSeparator.grid(row="0", column="3", sticky="NEWS",padx="2")
targetListIndexEditImage.grid(row="0", column="4", sticky="NW")
targetListIndexCalcImage.grid(row="0", column="5", sticky="NW")
targetListCalculate.grid(row="0", column="6", sticky="NESW")
targetListFrame.grid(column="0",row="1",columnspan="6",sticky="NW")
targetListPanedwindow.grid(row="1", column="0", sticky="nsew")
targetListLRLabelframe.grid(column="0",row="0",sticky="NESW")

#mapLabelFrame.grid(column="0",row="0",sticky="NESW")

statusBar.grid(column="0",row="1",sticky="SEW")
statusMessageFrame.grid(column="0",row="0",sticky="EW",)
statusMessageLabel.grid(column="0",row="0",sticky="W")
statusGridFrame.grid(column="1",row="0",sticky="EW")
statusReferenceLabel.grid(column="0",row="0",sticky="W")
statusGridLabel.grid(column="1",row="0",sticky="EW")
statusHeightLabel.grid(column="2",row="0",sticky="E")
statusProgressBar.grid(column="2",row="0",sticky="EW")
fireMissionSelectionTimeLabelframe.grid_remove()
fireMissionSelectionPairedEffectCreepingLabelframe.grid_remove()

idfpNotebook.grid(column="0",row="0", sticky="NESW")

#MAP GRID definitiions
mapPagePanedWindow.grid(column=0,row=0,sticky="NESW")
mapPageFrame0.grid(column=0,row=0,sticky="NESW")
mapPageFrame1.grid(column=0,row=0,sticky="NESW")
mapPageFrame2.grid(column=0,row=0,sticky="NESW")

# update_scrollregion(targetListLRCanvasFrame, targetListLRCanvas)
# update_scrollregion(targetListXYCanvasFrame, targetListXYCanvas)

settings_to_process = {
        "airTemperature": {
            "StringVar": airTemperature,
            "settingName": "Air Temperature",
            "traceName": airTemperatureTrace,
            "entryLabel": temperatureLabel
        },
        "airHumidity": {
            "StringVar": airHumidity,
            "settingName": "Air Humidity",
            "traceName": airHumidityTrace,
            "entryLabel": humidityLabel
        },
        "airPressure": {
            "StringVar": airPressure,
            "settingName": "Air Pressure",
            "traceName": airPressureTrace,
            "entryLabel": pressureLabel
        },
        "windDirection": {
            "StringVar": windDirection,
            "settingName": "Wind Direction",
            "traceName": windDirectionTrace,
            "entryLabel": directionLabel
        },
        "windMagnitude": {
            "StringVar": windMagnitude,
            "settingName": "Wind Magnitude",
            "traceName": windMagnitudeTrace,
            "entryLabel": magnitudeLabel
        },
        "windDynamic": {
            "StringVar": windDynamic,
            "settingName": "Dynamic Wind setting",
            "traceName": windDynamicTrace,
            "entryLabel": None
        },
        "system": {
            "StringVar": system,
            "settingName": "Weapon System",
            "traceName": systemTrace,
            "entryLabel": None
        }
    }

def StartUp(login = False,terrains = True):
    def InitialSettings():
        global terrainsFolders
        terrainsFolders = ListTerrainFolders()
        TerrainFolderCheck()
        IDFPListInitialise()
        if terrains == True:
            terrain.set(Json_Load(source=0,localOverride=True)["terrain"])
        LoadClockSettings()
        LoadNotes()
        UpdateSync()
        CheckUpdateQueue()
    if login ==True or jsonType == 0:
        StatusMessageLog(message="---New Session---\n")
        InitialSettings()
    elif jsonType == 1:
        if LoginRefresh() == True:
            StatusMessageLog(message="---New Session---\n")
            InitialSettings()
def TerrainStartPrompt():
    try:
        if Json_Load(source=0,localOverride=True)["terrain"] == "-1":
            return StartUp(terrains=False)
    except: StartUp(terrains=False)
    else:
        def No():
            terrainPrompt.grab_release()
            terrainPrompt.destroy()
            return StartUp(terrains=False)
        def Yes():
            terrainPrompt.grab_release()
            terrainPrompt.destroy()
            return StartUp(terrains=True)
        terrainPrompt = Toplevel(root)
        terrainPrompt.grab_set()
        terrainPrompt.attributes("-topmost",True)
        terrainPrompt.title("Load Last Terrain?")
        terrainPrompt.geometry("350x100+900+500")
        terrainPrompt.resizable(False, False)
        terrainPrompt.iconbitmap(exeDir/"Functions"/"uksf.ico")
        terrainPromptWindow = terrainPrompt.winfo_toplevel()
        terrainPromptWindow.anchor("nw")
        terrainPromptWindow.grid_columnconfigure(0,weight=1)
        terrainPromptWindow.grid_rowconfigure(0,weight=1)
        terrainPromptFrame = ttk.Frame(terrainPromptWindow,padding=20)
        terrainPromptFrame.grid_columnconfigure((0,1),weight=1)
        terrainPromptFrame.grid_rowconfigure((0,1),weight=1)
        try: terrainPromptLabel = ttk.Label(terrainPromptFrame,justify="center",text=f'Do you wish to load the last terrain? "{Json_Load(source=0,localOverride=True)["terrain"]}"')
        except: terrainPromptLabel = ttk.Label(terrainPromptFrame,justify="center",text="Do you wish to load the last terrain?")
        terrainPromptNo = ttk.Button(terrainPromptFrame,text="No",command=No)
        terrainPromptNo.bind("<Return>",lambda event:No())
        terrainPromptYes = ttk.Button(terrainPromptFrame,text="Yes",command=Yes)
        terrainPromptYes.bind("<Return>",lambda event:Yes())
        terrainPromptFrame.grid(row=0,column=0,sticky="NS")
        terrainPromptLabel.grid(row=0,column=0,columnspan=2,sticky="NESW")
        terrainPromptNo.grid(row=1,column=0,sticky="NESW")
        terrainPromptYes.grid(row=1,column=1,sticky="NESW")
        terrainPromptYes.focus()
        terrainPrompt.protocol("WM_DELETE_WINDOW",No)

root.after(100,TerrainStartPrompt)
root.mainloop()
