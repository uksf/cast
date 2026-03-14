from collections import namedtuple
from tkinter import *
from tkinter import ttk
from enum import Enum, IntEnum
from typing import Literal
import json
import requests
import os
import numpy as np
from PIL import Image,ImageTk
from io import BytesIO
import zipfile
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import RectangleSelector
from matplotlib import cbook
from matplotlib.backend_tools import Cursors
import matplotlib.patches as mpatches
from matplotlib.offsetbox import AnnotationBbox, DrawingArea,AnchoredText
from matplotlib.lines import Line2D
from matplotlib.text import Text as matplotText
from matplotlib.font_manager import FontProperties
from matplotlib.axes import Axes
from matplotlib.path import Path as MPLPath
from matplotlib.artist import Artist
import pandas as pd
from Functions.JsonFunctions import JsonSource
from Functions.UI_Components import IDFPCreation,TargetCreation,TargetDetails,Targets,FireMissions
import queue
import threading
# from CAST import CastUI

class Terrain():
    def __init__(self):
        pass
    def NewTerrainImage(url: str,terrainImagePreviewSquare:ttk.Label,terrainStitchDiagram:ttk.Label,toplevel: Toplevel,baseDir: Path,terrainImageTerrainName:str)-> bool | Exception:
        """Used to select a new map image to be obtained from plan-ops"""
        #"https://atlas.plan-ops.fr/data/1/maps/160/162/" Mehland
        completed = False
        resolutionImage = False
        res = 0
        y = 0
        stitch = ""
        line = False
        os.makedirs(baseDir/"Terrains"/terrainImageTerrainName/"Terrain Images",exist_ok=True)
        try:
            while completed == False:
                resolutionImage = False
                y = 0
                stitch = f"Resolution: {str(res)}\n"
                while resolutionImage == False:
                    line = False
                    x = 0
                    rowImages = []
                    while line == False:
                        response = requests.get(url+str(res)+"/"+str(x)+"/"+str(y)+".png")
                        if response.status_code == 200:
                            imageSave = Image.open(BytesIO(response.content)).convert("RGB")
                            if imageSave.width == 1:
                                return True
                            image = ImageTk.PhotoImage(imageSave)
                            terrainImagePreviewSquare.config(image= image)
                            terrainImagePreviewSquare.image = image
                            name = str(res)+"-"+str(x)+"-"+str(y)+".png"
                            imageSave.save(baseDir/"Terrains"/terrainImageTerrainName/"Terrain Images"/name) 
                            stitch += "■  "
                            terrainStitchDiagram.config(text= stitch)
                            toplevel.update()
                            x+=1
                        elif x == 0 and y == 0:
                            return True
                        elif x == 0:
                            resolutionImage = True
                            line = True
                            break
                        else:
                            line = True
                            break
                    y+=1
                    stitch += "\n"
                res+=1
        except Exception as e:
            return e
    def CompressImages(rootTerrainFolder,terrainName,removeFolder = True):
        try:
            if os.path.exists(rootTerrainFolder/terrainName/"Terrain Images"):
                with zipfile.ZipFile(file=rootTerrainFolder/terrainName/(terrainName+".terrainimage"),mode="w",compression=zipfile.ZIP_STORED) as zipF:
                    for imageName in os.listdir(rootTerrainFolder/terrainName/"Terrain Images"):
                        if imageName[-4:]==".png":
                            imagePath = os.path.join(rootTerrainFolder/terrainName/"Terrain Images",imageName)
                            zipF.write(imagePath,arcname=imageName)
            if removeFolder:
                for imageName in os.listdir(rootTerrainFolder/terrainName/"Terrain Images"):
                    Path(rootTerrainFolder/terrainName/"Terrain Images"/imageName).unlink(missing_ok=True)
                Path(rootTerrainFolder/terrainName/"Terrain Images").rmdir()
        except:
            None
    def NewTerrainHeightmap(baseDir:Path,filePath:str, terrainName: str, compression = True,targets = None, **kwargs):
        for key, value in kwargs.items():
            if key == "calculateButton":
                calculateButton = value
            elif key == "progressBar":
                progressbar = value
            elif key == "statusMessageLog":
                StatusMessageLog = value
            elif key == "statusMessageLabel":
                statusMessageLabel = value
            elif key == "statusMessageErrorDump":
                StatusMessageErrorDump = value
                
        calculateButton.config(state= DISABLED)
        
        start = ""
        end = ""
        with open(file=filePath) as file:
            for line in file:
                start = line
                break
        with open(file=filePath,mode="rb") as file:
            try:
                file.seek(-2,os.SEEK_END)
                while file.read(1)!= b'\n':
                    file.seek(-2,os.SEEK_CUR)
            except OSError:
                file.seek(0)
            except Exception as e:
                StatusMessageErrorDump(e,errorMessage = "Failed to seek in file")
            end = file.readline().decode()
        start = start.replace("\n","").replace("\r","").split(sep=" ")
        end = end.replace("\n","").replace("\r","").split(sep=" ")
        print(start,end)
        progressbar.config(value = 0,mode="determinate",maximum=int(end[0])-int(start[0]))
        xrow = None
        rowList = []
        heights = ""
        os.makedirs(baseDir/"Terrains"/terrainName,exist_ok=True)
        StatusMessageLog(f"Beginning {terrainName} height map formatting")
        with open(file=filePath,mode="r") as file:
            with open(file=baseDir/"Terrains"/terrainName/f"{terrainName}.gzcsv",mode="w") as outputFile:
                outputFile.write("")
            for line in file:
                line = line.replace("\n","").replace("\r","").split(sep=" ")
                if float(line[2])<0:
                    rowList.append(0)
                else:
                    rowList.append(round(float(line[2]),ndigits=1))
                if line[1] == end[1]:
                    if (line != end): heights += str(rowList).replace("[","").replace("]","") + "\n"
                    else: heights += str(rowList).replace("[","").replace("]","")
                    if len(heights) > 17500000:
                        with open(file=baseDir/"Terrains"/terrainName/f"{terrainName}.gzcsv",mode="a") as outputFile:
                            outputFile.write(str(heights))
                        heights = ""
                    rowList = []
                    progressbar.config(value= int(line[0])-int(start[0]))
                    progressbar.update()
            with open(file=baseDir/"Terrains"/terrainName/f"{terrainName}.gzcsv",mode="a") as outputFile:
                outputFile.write(str(heights))
        StatusMessageLog(f"Completed {terrainName} height map formatting")
        statusMessageLabel.update()
        if compression:
            StatusMessageLog(f"Beginning {terrainName} height map compression, this will take several minutes, go get a drink")
            statusMessageLabel.update()
            data = pd.read_csv(baseDir/"Terrains"/terrainName/f"{terrainName}.gzcsv",header=None)
            print(data.iat[int(1),int(0)])
            data.to_csv(baseDir/"Terrains"/terrainName/f"{terrainName}.gzcsv",compression="gzip",header=False,index=False)
            StatusMessageLog(f"Finished compression of {terrainName}'s height map")
        calculateButton.config(state=NORMAL)
        progressbar.config(value = 0)
        progressbar.update()
        progressbar.stop()


class TerrainSettingsFile():
    def __init__(self,terrainFolder: Path,StatusMessageErrorDump):
        self.terrainFolder = terrainFolder
        self.StatusMessageErrorDump = StatusMessageErrorDump
        if Path.joinpath(self.terrainFolder,self.terrainFolder.name+".json").exists() == False:
            with open(Path.joinpath(self.terrainFolder,self.terrainFolder.name+".json"),"w") as file:
                json.dump({},file,indent=4)
    def Get(self,key: str | None = None):
        try:
            with open(Path.joinpath(self.terrainFolder,self.terrainFolder.name+".json"),"r") as file:
                if key == None:
                    return json.load(file)
                elif type(key) == str:
                    return json.load(file)[key]
        except:
            return {}
    def Save(self,key: str | None = None,entry = None,append = True):
        jsonData = {}
        if append:
            jsonData = self.Get()
            if key != None:
                jsonData[key] = entry
            else:
                jsonData = jsonData | entry
        else:
            if key != None:
                jsonData = {key : entry}
            else:
                jsonData = entry
        with open(Path.joinpath(self.terrainFolder,self.terrainFolder.name+".json"),"w") as file:
            json.dump(jsonData,file,indent=4)
    

class MapTileManager():
    def __init__(self,terrainTileFolder : Path,StatusMessageErrorDump,matPlotLibWidget):
        try:
            self.terrainTileFolder = terrainTileFolder
            self.tileCache = {}
            self.maxCacheSize = 100
            self.tileSizes = {}
            self.StatusMessageErrorDump = StatusMessageErrorDump
            self.maxTileSize = 0
            self.packaged = terrainTileFolder.is_file()
            self.customScale = 1
            if self.packaged:
                self.zipFile = zipfile.ZipFile(terrainTileFolder,"r")
            self.GetMaxZoom()
        except Exception as e:
            self.StatusMessageErrorDump(e,errorMessage = "Failed to load image tiles")
            matPlotLibWidget.loadedTerrainImage = False

    def GetTile(self,zoom,xTile,yTile):
        key = f"{zoom}-{xTile}-{yTile}"
        if key in self.tileCache:
            return self.tileCache[key]
        if self.packaged:
            try:
                with self.zipFile.open(f"{key}.png") as tileFile:
                    tileImg = Image.open(tileFile)
                    tileImgArray = np.array(tileImg)
            except Exception as e:
                self.StatusMessageErrorDump(e,errorMessage = f"Failed to load map tile {key} from file")
        else:
            tilePath = os.path.join(self.terrainTileFolder,f"{key}.png")
            if os.path.exists(tilePath):
                try:
                    tileImg = Image.open(tilePath)
                    tileImgArray = np.array(tileImg)
                except Exception as e:
                    self.StatusMessageErrorDump(e,errorMessage = f"Failed to load map tile {key} from folder")
                    return None
            else:
                return None
        if len(self.tileCache) >= self.maxCacheSize:
            self.tileCache.pop(next(iter(self.tileCache)))
        self.tileCache[key] = tileImgArray
        return tileImgArray

    def GetMaxZoom(self):
        zoomTest = (0,1,2,3,4,5,6,7,8)
        for level in zoomTest:
            try:
                self.zipFile.open(f"{level}-{0}-{0}.png")
                self.maxTileSize = level
            except:
                None
    def GetZoomLevelFromScale(self,xlim:tuple,ylim:tuple,maxSize: tuple):
        """lim tuple [min, max]
        maxsize is max terrain size in x and y"""
        maxSpan = max(xlim[1]-xlim[0],ylim[1]-ylim[0])
        maxSize = max(maxSize)
        if maxSpan > maxSize*2 or self.maxTileSize == 0:
            return 0
        elif maxSpan > maxSize or self.maxTileSize == 1:
            return 1
        elif maxSpan > maxSize/2 or self.maxTileSize == 2:
            return 2
        elif maxSpan > maxSize/4 or self.maxTileSize == 3:
            return 3
        elif maxSpan > maxSize/8 or self.maxTileSize == 4:
            return 4
        elif maxSpan > maxSize/16 or self.maxTileSize == 5:
            return 5
        elif maxSpan > maxSize/32 or self.maxTileSize == 6:
            return 6
        elif maxSpan > maxSize/64 or self.maxTileSize == 7:
            return 7
        else: return 8
        
    def GetTilesInView(self,xlim: tuple,ylim: tuple,zoom:int,maxSize:tuple):
        """zoomTileCount tuple (x,y) count"""
        zoomTileCount = pow(2,zoom)
        tileScale = (maxSize[0]/zoomTileCount*self.customScale,maxSize[1]/zoomTileCount*self.customScale)
        tiles = []
        ylim = (maxSize[1]-ylim[1],maxSize[1]-ylim[0])
        xMinTile = max(0,int(xlim[0]/tileScale[0]))
        xMaxTile = min(zoomTileCount-1,int(xlim[1]/tileScale[0]))
        yMinTile = max(0,int(ylim[0]/tileScale[1]))
        yMaxTile = min(zoomTileCount-1,int(ylim[1]/tileScale[1]))
        for x in range(xMinTile,xMaxTile+1):
            for y in range(yMinTile,yMaxTile+1):
                tiles.append((x,y))
        return tiles,tileScale
    
    def ClearCache(self):
        "Clear Tile Cache"
        self.tileCache.clear()

class Mode(str, Enum):
    NONE = ""
    PAN = "pan/zoom"
    ZOOM = "zoom rect"
    XY = "xy placement"
    LR = "lr placement"
    FPF = "fpf placement"
    QUICK = "quick fire mission"
    REFERENCE = "reference points"
    MARKER = "marker settings"
    def __str__(self):
        return self.value

class MouseButton(IntEnum):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    BACK = 8
    FORWARD = 9

class Mark(str, Enum):
    IDFP = "IDFP"
    FPF = "FPF"
    FPF_BOUNDS = "FPFBounds"
    LR = "LR"
    LR_BOUNDS = "LRBounds"
    XY = "XY"
    XY_BOUNDS = "XYBounds"
    GROUP = "Group"
    GROUP_BOUNDS = "GroupBounds"
    NOFLY = "nofly"
    NOFLY_BOUNDS = "noflyBounds"
    FRIENDLY = "friendly"
    FRIENDLY_BOUNDS = "friendlyBounds"
    SNAPSHOT = "snapshot"
    def __str__(self):
        return self.value

def add_tooltip(widget, text):
    tipwindow = None

    def showtip(event):
        """Display text in tooltip window."""
        nonlocal tipwindow
        if tipwindow or not text:
            return
        x, y, _, _ = widget.bbox("insert")
        x = x + widget.winfo_rootx() + widget.winfo_width()
        y = y + widget.winfo_rooty()
        tipwindow = Toplevel(widget)
        tipwindow.overrideredirect(1)
        tipwindow.geometry(f"+{x}+{y}")
        try:  # For Mac OS
            tipwindow.tk.call("::tk::unsupported::MacWindowStyle",
                              "style", tipwindow._w,
                              "help", "noActivates")
        except TclError:
            pass
        label = Label(tipwindow, text=text, justify=LEFT,
                         relief="solid", borderwidth=1)
        label.pack(ipadx=1)

    def hidetip(event):
        nonlocal tipwindow
        if tipwindow:
            tipwindow.destroy()
        tipwindow = None

    widget.bind("<Enter>", showtip)
    widget.bind("<Leave>", hidetip)

class PolygonDoublet(mpatches.Polygon):
    def __init__(self, xy, offsetWidth : int, offsetSide : Literal["inner","outer"], offsetStyle : Literal["solid","dotted","dashed","dashdot"] | tuple,**kwargs):
        super().__init__(xy, **kwargs)
        self.set_fill(False)
        self.offsetPolygon = None
        self.offsetWidth = offsetWidth
        self.offsetSide = offsetSide
        self.offsetStyle = offsetStyle

    def _offsetPolygon(self,vertices,offset,side : Literal["inner","outer"]):
        """Offset polygon inward in display coordinates."""
        n = len(vertices)
        offsetVertices = []
        
        for i in range(n):
            prev = vertices[(i - 2) % n] if i == 0 else vertices[(i - 1) % n]
            curr = vertices[i]
            next = vertices[1] if i == n-1 else vertices[(i + 1) % n]
            
            edge1 = curr - prev
            edge2 = next - curr
            
            edge1_norm = np.linalg.norm(edge1)
            edge2_norm = np.linalg.norm(edge2)
            
            if edge1_norm > 1e-10:
                edge1 = edge1 / edge1_norm
            if edge2_norm > 1e-10:
                edge2 = edge2 / edge2_norm
            
            normal1 = np.array([edge1[1], -edge1[0]])
            normal2 = np.array([edge2[1], -edge2[0]])
            
            avgNormal = normal1 + normal2
            norm = np.linalg.norm(avgNormal)
            
            if norm > 1e-10:
                avgNormal = avgNormal / norm
                
                dot_product = np.dot(normal1, avgNormal)
                
                if abs(dot_product) > 0.1:
                    miterLength = offset / abs(dot_product)
                else:
                    miterLength = offset * 10
                
                miterLength = min(miterLength, offset * 10)
            
                if side == "outer": offsetVertices.append(curr - avgNormal * miterLength)
                else: offsetVertices.append(curr + avgNormal *miterLength)
            else:
                if side == "outer": offsetVertices.append(curr - normal1*offset)
                else: offsetVertices.append(curr + normal1*offset)
        return np.array(offsetVertices)
    
    def draw(self,renderer):
        super().draw(renderer)
        vertices = self.get_xy()
        linewidth = self.get_linewidth()
        offsetDisplay = self.offsetWidth*linewidth

        transform = self.get_transform()
        displayVertices = transform.transform(vertices)
        offsetDisplayVertices = self._offsetPolygon(displayVertices,offsetDisplay,self.offsetSide)
        offsetDataVertices = transform.inverted().transform(offsetDisplayVertices)
        if self.offsetPolygon is None:
            self.offsetPolygon = mpatches.Polygon(offsetDataVertices,transform=transform,edgecolor = self.get_edgecolor(),fill = False,linestyle = self.offsetStyle,linewidth = self.get_linewidth())
            self.offsetPolygon.set_clip_box(self.get_clip_box())
            self.offsetPolygon.set_clip_path(self.get_clip_path())
        else:
            self.offsetPolygon.set_xy(offsetDataVertices)
            self.offsetPolygon.set_linewidth(linewidth)
            self.offsetPolygon.set_transform(transform)
        
        # Draw inner polygon with renderer
        self.offsetPolygon.draw(renderer)

class WedgeDoublet(mpatches.Wedge):
    def __init__(self, center, r, theta1, theta2, width, offsetWidth: int, offsetSide: Literal["inner", "outer"], offsetStyle: Literal["solid", "dotted", "dashed", "dashdot"] | tuple, **kwargs):
        super().__init__(center, r, theta1, theta2, width=width, **kwargs)
        self.set_fill(False)
        self.offsetWedge = None
        self.offsetWidth = offsetWidth
        self.offsetSide = offsetSide
        self.offsetStyle = offsetStyle
    
    def _offsetPath(self, vertices,codes: np.ndarray, offset, side: Literal["inner", "outer"]):
        """Offset path uniformly around entire perimeter."""
        n = len(vertices)
        offsetVertices = []
        for i in range(n):
            prev = vertices[(i - 2) % n] if i == 0 else vertices[(i - 1) % n]
            curr = vertices[i]
            next = vertices[0] if i == n-2 else vertices[(i + 1) % n]

            # Calculate edge vectors
            edge1 = curr - prev
            edge2 = next - curr
            
            edge1_norm = np.linalg.norm(edge1)
            edge2_norm = np.linalg.norm(edge2)
            
            # Normalize edges
            if edge1_norm > 1e-10:
                edge1 = edge1 / edge1_norm
            if edge2_norm > 1e-10:
                edge2 = edge2 / edge2_norm
            
            # Calculate perpendicular normals (pointing outward)
            normal1 = np.array([-edge1[1], edge1[0]])
            normal2 = np.array([-edge2[1], edge2[0]])
            
            # Average normal for miter joint
            avgNormal = normal1 + normal2
            norm = np.linalg.norm(avgNormal)
            
            if norm > 1e-10:
                avgNormal = avgNormal / norm
                
                # Calculate miter length to maintain uniform offset
                dotProduct = np.dot(normal1, avgNormal)
                
                if abs(dotProduct) > 0.1:
                    miterLength = offset / abs(dotProduct)
                else:
                    miterLength = offset * 10
                
                # Limit extreme miter lengths
                miterLength = min(miterLength, offset * 10)
                
                if side == "outer":
                    offsetVertices.append(curr - avgNormal * miterLength)
                else:
                    offsetVertices.append(curr + avgNormal * miterLength)
            else:
                # Fallback for degenerate cases
                if side == "outer":
                    offsetVertices.append(curr - normal1 * offset)
                else:
                    offsetVertices.append(curr + normal1 * offset)
        
        return np.array(offsetVertices)
    
    def draw(self, renderer):
        # Draw the main wedge
        super().draw(renderer)
        
        # Get the wedge path
        path = self.get_path()
        transform = self.get_transform()
        
        # Get vertices and convert to display coordinates
        vertices = path.vertices
        linewidth = self.get_linewidth()
        
        # Transform to display coordinates for offsetting
        displayVertices = transform.transform(vertices)
        
        # Calculate offset in display units (points)
        offsetDisplay = self.offsetWidth * linewidth
        codes = path.codes
        # Offset the path
        offsetDisplayVertices = self._offsetPath(
            displayVertices,codes, offsetDisplay, self.offsetSide
        )
        
        # Transform back to data coordinates
        offsetVertices = transform.inverted().transform(offsetDisplayVertices)
        # Get the path codes from original path
        
        
        # Create or update offset patch
        if self.offsetWedge is None:
            offset_path = MPLPath(offsetVertices, codes)
            self.offsetWedge = mpatches.PathPatch(
                offset_path,
                transform=transform,
                edgecolor=self.get_edgecolor(),
                facecolor='none',
                linestyle=self.offsetStyle,
                linewidth=linewidth
            )
            self.offsetWedge.set_clip_box(self.get_clip_box())
            self.offsetWedge.set_clip_path(self.get_clip_path())
        else:
            offset_path = MPLPath(offsetVertices, codes)
            self.offsetWedge.set_path(offset_path)
            self.offsetWedge.set_linewidth(linewidth)
            self.offsetWedge.set_edgecolor(self.get_edgecolor())
            self.offsetWedge.set_transform(transform)
        
        # Draw offset patch
        self.offsetWedge.draw(renderer)

class CircleDoublet(mpatches.Circle):
    def __init__(self, xy, radius, offsetWidth: int, offsetSide: Literal["inner", "outer"], offsetStyle: Literal["solid", "dotted", "dashed", "dashdot"] | tuple, **kwargs):
        super().__init__(xy, radius, **kwargs)
        self.set_fill(False)
        self.offsetCircle = None
        self.offsetWidth = offsetWidth
        self.offsetSide = offsetSide
        self.offsetStyle = offsetStyle

    def _offsetPath(self, vertices, codes, offset, side: Literal["inner", "outer"]):
        """Offset circle path radially."""
        n = len(vertices)
        offsetVertices = []
        valid_vertices = [vertices[i] for i in range(n) if codes[i] != 79]
        center = np.mean(valid_vertices, axis=0)
        for i in range(n):
            curr = vertices[i]
            code = codes[i]
            
            # Skip CLOSEPOLY vertices
            if code == 79:
                offsetVertices.append(curr)
                continue
            
            # Offset radially from center
            direction = curr - center
            directionNorm = np.linalg.norm(direction)
            
            if directionNorm > 1e-10:
                direction = direction / directionNorm
                if side == "inner":
                    offsetVertices.append(curr - direction * offset)
                else:
                    offsetVertices.append(curr + direction * offset)
            else:
                offsetVertices.append(curr)
        
        return np.array(offsetVertices)
    
    def draw(self, renderer):
        super().draw(renderer)
        
        path = self.get_path()
        transform = self.get_transform()
        
        vertices = path.vertices
        codes = path.codes
        linewidth = self.get_linewidth()
        
        displayVertices = transform.transform(vertices)
        display_center = transform.transform([self.center])[0]
        
        offsetDisplay = self.offsetWidth * linewidth
        
        offsetDisplayVertices = self._offsetPath(
            displayVertices, codes, offsetDisplay, self.offsetSide
        )
        offsetDataVertices = transform.inverted().transform(offsetDisplayVertices)
        
        if self.offsetCircle is None:
            offset_path = MPLPath(offsetDataVertices, codes)
            self.offsetCircle = mpatches.PathPatch(
                offset_path,
                transform=transform,
                edgecolor=self.get_edgecolor(),
                facecolor='none',
                linestyle=self.offsetStyle,
                linewidth=linewidth
            )
            self.offsetCircle.set_clip_box(self.get_clip_box())
            self.offsetCircle.set_clip_path(self.get_clip_path())
        else:
            offset_path = MPLPath(offsetDataVertices, codes)
            self.offsetCircle.set_path(offset_path)
            self.offsetCircle.set_linewidth(linewidth)
            self.offsetCircle.set_edgecolor(self.get_edgecolor())
            self.offsetCircle.set_transform(transform)
        
        self.offsetCircle.draw(renderer)

class PolarLine(Line2D):
    def __init__(self, r, theta, center=(0, 0), **kwargs):
        x, y = self._polarToCart(r, theta, center)
        super().__init__(x, y, **kwargs)

    @staticmethod
    def _polarToCart(r, theta, center=(0, 0)):
        theta_rad = np.deg2rad(theta)
        x = center[0] + np.array(r) * np.cos(theta_rad)
        y = center[1] + np.array(r) * np.sin(theta_rad)
        return x, y

class MapMarking():
    def __init__(self, xy:tuple[float,float],ax : Axes, size:float = 10,**kwargs):
        self.x,self.y = xy[0],xy[1]
        self.ax = ax
        self.size = float(size)
        self.IDFP = None
        for setting,value in kwargs.items():
            if setting == "IDFP":
                self.IDFP = value

    def Flag(self,colour: str = "black",flagColour: str | None = None,text: str | None = None):
        drawArea = DrawingArea(self.size+5, self.size+5,0,-self.size/2)
        pole = Line2D((0,0),(0,self.size*10),linewidth=self.size,color=colour,solid_capstyle="round")
        flag = mpatches.Rectangle((0,self.size*4.5),self.size*7,self.size*5.5,edgecolor=colour,facecolor = flagColour,linewidth=self.size)
        if text is not None:
            textBox = matplotText(x=self.size*10,y=self.size*6.5,text=text,color=colour,horizontalalignment="left",fontproperties=FontProperties(size=self.size*5))
            drawArea.add_artist(textBox)
        if flagColour is None:
            flag.set_fill(False)
        drawArea.add_artist(pole)
        drawArea.add_artist(flag)
        self.axArtist = self.ax.add_artist(AnnotationBbox(drawArea,(self.x,self.y),xycoords="data",box_alignment=(0,0),frameon=False,pad=0))
        return self.axArtist
    def Cross(self,colour: str = "black",text: str | None = None):
        drawArea = DrawingArea(self.size+5,self.size+5,0,0)
        line1 = Line2D((0,0),(self.size*5,-self.size*5),linewidth=self.size,color=colour,solid_capstyle="round")
        line2 = Line2D((self.size*5,-self.size*5),(0,0),linewidth=self.size,color=colour,solid_capstyle="round")
        if text is not None:
            textBox = matplotText(x=self.size*3,y=self.size*3,text=text,color=colour,horizontalalignment="left",fontproperties=FontProperties(size=self.size*5))
            drawArea.add_artist(textBox)
        drawArea.add_artist(line1)
        drawArea.add_artist(line2)
        self.axArtist = self.ax.add_artist(AnnotationBbox(drawArea,(self.x,self.y),xycoords="data",box_alignment=(0,0),frameon=False,pad=0))
        return self.axArtist
    def Exclamation(self, colour: str = "black",caretColour: str | None = None,text: str | None = None):
        drawArea = DrawingArea(self.size+10,self.size+10,0,0)
        # point = self.ax.plot(self.x,self.y,color=colour, marker='o')
        point = mpatches.Circle((0,0),radius=self.size,facecolor=colour)
        caret = mpatches.Polygon(([0,self.size*3],[-self.size*2,self.size*10],[self.size*2,self.size*10]),closed=True,edgecolor=colour,facecolor = caretColour,linewidth=self.size)
        if caretColour is None:
            caret.set_fill(False)
        if text is not None:
            textBox = matplotText(x=self.size*2,y=self.size*2,text=text,color=colour,horizontalalignment="left",fontproperties=FontProperties(size=self.size*5))
            drawArea.add_artist(textBox)
        drawArea.add_artist(point)
        drawArea.add_artist(caret)
        self.axArtist = self.ax.add_artist(AnnotationBbox(drawArea,(self.x,self.y),xycoords="data", box_alignment=(0,0),frameon=False,pad=0))
        return self.axArtist
    def Bounds(self,orientation : Literal["grid","orthogonal","circle"],distance: int | float | dict,style : Literal["solid","dotted","dashed","dashdot","denseDash","sparseDash","sparsestDash","sparseDot","sparsestDot"],colour: str = "black",doubleStyle : Literal["same","solid","dotted","dashed","dashdot","denseDash","sparseDash","sparsestDash","sparseDot","sparsestDot"] | None = None, doubleSide : Literal["inner","outer"] = "inner",noflyZone = False):
        if style not in ("solid","dotted","dashed","dashdot"):
            if style == "denseDash":
                style = (5,(10,3))
            elif style == "sparseDash":
                style = (0,(5,5))
            elif style == "sparsestDash":
                style = (0,(5,10))
            elif style == "sparseDot":
                style = (0,(1,5))
            elif style == "sparsestDot":
                style = (0,(1,10))
            else:
                raise AttributeError(self.Bounds)
        if doubleStyle is not None or doubleStyle != "None":
            if doubleStyle not in ("solid","dotted","dashed","dashdot"):
                if doubleStyle == "same":
                    doubleStyle = style
                elif doubleStyle == "denseDash":
                    doubleStyle = (5,(10,3))
                elif doubleStyle == "sparseDash":
                    doubleStyle = (0,(5,5))
                elif doubleStyle == "sparsestDash":
                    doubleStyle = (0,(5,10))
                elif doubleStyle == "sparseDot":
                    doubleStyle = (0,(1,5))
                elif doubleStyle == "sparsestDot":
                    doubleStyle = (0,(1,10))
                else:
                    doubleStyle = None
        if orientation == "grid":
            if doubleStyle is not None:
                vertices = [(self.x-distance,self.y-distance),(self.x+distance,self.y-distance),(self.x+distance,self.y+distance),(self.x-distance,self.y+distance)]
                bounds = PolygonDoublet(vertices,offsetWidth=self.size*3,offsetSide=doubleSide,offsetStyle=doubleStyle,linestyle=style,linewidth=self.size,edgecolor = colour)
            else:
                bounds = mpatches.Rectangle([self.x-distance,self.y-distance],width=distance*2,height=distance*2,edgecolor = colour,linewidth=self.size,linestyle=style,fill=False)
            self.axArtist = self.ax.add_artist(bounds)
            return self.axArtist
        elif orientation == "circle":
            if doubleStyle is not None:
                vertices = [(self.x-distance,self.y-distance),(self.x+distance,self.y-distance),(self.x+distance,self.y+distance),(self.x-distance,self.y+distance)]
                bounds = CircleDoublet([self.x,self.y], radius=distance,offsetWidth=self.size*3,offsetSide=doubleSide,offsetStyle=doubleStyle,linestyle=style,linewidth=self.size,edgecolor = colour)
            else:
                bounds = mpatches.Circle([self.x,self.y], radius=distance,edgecolor = colour,linewidth=self.size,linestyle=style,fill=False)
            self.axArtist = self.ax.add_artist(bounds)
            return self.axArtist
            
        elif orientation == "orthogonal":
            width,height,origin = distance["Width"], distance["Depth"], distance["Origin"]
            range = np.sqrt((self.x-origin[0])*(self.x-origin[0])+(self.y-origin[1])*(self.y-origin[1]))
            halfangle = np.rad2deg(width/range)
            direction = np.rad2deg(np.arctan2((self.y-origin[1]),(self.x-origin[0])))
            if noflyZone == False:
                length = height*2
            else:
                length = None
            if doubleStyle is not None:
                bounds = WedgeDoublet(origin,r=range+height,width=length,theta1=direction - halfangle,theta2=direction + halfangle,offsetWidth=self.size*3,offsetStyle=doubleStyle,offsetSide=doubleSide,linestyle=style,linewidth=self.size,edgecolor = colour)
            else:
                bounds = mpatches.Wedge(origin,r=range+height,width=length,theta1=direction - halfangle,theta2=direction + halfangle,linestyle=style,linewidth=self.size,edgecolor = colour,fill = False)
            self.axArtist = self.ax.add_artist(bounds)
            return self.axArtist
    def NATOStandards(self,force : Literal["BLUFOR","OPFOR","Civilian"],colour: str | None,*args,**kwargs):
        for setting,value in kwargs.items():
            setattr(self,setting,value)
        drawArea = DrawingArea(self.size+10,self.size+10,0,0)
        if force == "BLUFOR":
            outerRim = mpatches.Rectangle((-self.size/2,-self.size/1.5),self.size,self.size*0.75)
            if "tracked" in args:
                None
        elif force == "OPFOR":
            outerRim = mpatches.Rectangle((-self.size/2,-self.size/2),self.size,self.size,angle=45,rotation_point="center")
        elif force == "Civilian":
            outerRim = mpatches.Rectangle((-self.size/2,-self.size/2),self.size,self.size)
        
        
        
        None

class MarkerSettings():
    def __init__(self,**kwargs):
        
        '''
        Accepted Linestyles:

        "solid" , "dotted" , "dashed" , "dashdot" , "denseDash" , "sparseDash" , "sparsestDash" , "sparseDot" , "sparsestDot"
        '''
        self.settingsFileSaveFunction = None
        '''
        (method) def Save
        (
            key: str | None = None,
            entry: Any | None = None,
            append: bool = True
        ) -> None
        '''
        self.defaults = {"visible_IDFP":"1",
                    "size_IDFP":1.0,
                    "declutter_IDFP":"0",
                    "visible_FPF":"1",
                    "visible_FPFBounds":"1",
                    "size_FPF":1.0,
                    "size_FPFBounds":1.0,
                    "linestyle_FPFBounds":"solid",
                    "double_linestyle_FPFBounds":"dotted",
                    "double_side_FPFBounds":"inner",
                    "visible_XY":"1",
                    "visible_XYBounds":"1",
                    "size_XY":1.0,
                    "size_XYBounds":1.0,
                    "linestyle_XYBounds":"denseDash",
                    "double_linestyle_XYBounds":"None",
                    "double_side_XYBounds":"inner",
                    "visible_LR":"1",
                    "visible_LRBounds":"1",
                    "size_LR":1.0,
                    "size_LRBounds":1.0,
                    "linestyle_LRBounds":"denseDash",
                    "double_linestyle_LRBounds":"None",
                    "double_side_LRBounds":"inner",
                    "visible_Group":"1",
                    "visible_GroupBounds":"1",
                    "size_Group":1.0,
                    "size_GroupBounds":1.0,
                    "linestyle_GroupBounds":"sparseDash",
                    "double_linestyle_GroupBounds":"None",
                    "double_side_GroupBounds":"inner",
                    "visible_nofly":"1",
                    "visible_noflyBounds":"1",
                    "size_nofly":1.0,
                    "size_noflyBounds":1.0,
                    "declutter_nofly":"0",
                    "linestyle_noflyBounds":"sparsestDash",
                    "double_linestyle_noflyBounds":"sparsestDot",
                    "double_side_noflyBounds":"outer",
                    "visible_friendly":"1",
                    "visible_friendlyBounds":"1",
                    "size_friendly":1.0,
                    "size_friendlyBounds":1.0,
                    "declutter_friendly":"0",
                    "linestyle_friendlyBounds":"sparseDash",
                    "double_linestyle_friendlyBounds":"same",
                    "double_side_friendlyBounds":"inner",
                    "visible_snapshotBounds":"1",
                    "size_snapshot":1.0,
                    "size_snapshotBounds":1.0,
                    "linestyle_snapshotBounds":"solid",
                    "double_linestyle_snapshotBounds":"None",
                    "double_side_snapshotBounds":"inner"}
        for var in self.defaults.keys():
            setattr(self,var,StringVar(value=self.defaults[var]))
            saveTrace = getattr(self,var).trace_add(mode="write",callback = lambda *args, v=var: self.SaveSettings(v))
            setattr(getattr(self,var),"saveTrace",saveTrace)
    def LoadSettings(self,settingsDict):
        for key,value in settingsDict.items():
            setattr(self,key,StringVar(value=value))

    def SaveSettings(self,key):
        if self.settingsFileSaveFunction is not None:
            self.settingsFileSaveFunction(key,getattr(self,key).get())
    def ReturnSettings(self,*args) -> dict[str,StringVar]:
        '''"visible_IDFP",
        "size_IDFP", declutter_IDFP

        "visible_FPF","visible_FPFBounds",
        "size_FPF","size_FPFBounds",
        "linestyle_FPFBounds","double_linestyle_FPFBounds","double_side_FPFBounds",

        "visible_XY","visible_XYBounds",
        "size_XY","size_XYBounds",
        "linestyle_XYBounds","double_linestyle_XYBounds","double_side_XYBounds",

        "visible_LR","visible_LRBounds",
        "size_LR","size_LRBounds",
        "linestyle_LRBounds","double_linestyle_LRBounds","double_side_LRBounds",

        "visible_Group","visible_GroupBounds",
        "size_Group","size_GroupBounds",
        "linestyle_GroupBounds","double_linestyle_GroupBounds","double_side_GroupBounds",

        "visible_nofly","visible_nofly","declutter_nofly",
        "size_nofly","size_noflyBounds",
        "linestyle_noflyBounds","double_linestyle_noflyBounds","double_side_noflyBounds",

        "visible_friendly","visible_friendlyBounds", "declutter_friendly",
        "size_friendly","size_friendlyBounds",
        "linestyle_friendlyBounds","double_linestyle_friendlyBounds","double_side_friendlyBounds",

        "visible_snapshotBounds","size_snapshot","size_snapshotBounds",
        "linestyle_snapshotBounds","double_linestyle_snapshotBounds","double_side_snapshotBounds"'''
        if not args:
            args = self.defaults.keys()
        settings = {}
        for key in args:
            
            settings[key] = getattr(self,key)
        return settings
        


        



class MatPlotLibWidget():
    def __init__(self,UIMaster):
        self.UIMaster = UIMaster
        self.activeMaps = UIMaster.activeMaps
        self.StatusMessageErrorDump = UIMaster.StatusMessageErrorDump
        self.MessageLog = UIMaster.StatusMessageLog
        self.loadedTerrainHeightMap = False
        self.loadedTerrainImage = False
        self.terrain = ""
        
    def StartMarkerUpdate(self):
        setattr(self,"markerUpdateEvent",self.frame.after(self.mapDelay,self.toolbar.MapUpdate))
    def StopMarkerUpdate(self):
        self.frame.after_cancel(getattr(self,"markerUpdateEvent"))
        delattr(self,"markerUpdateEvent")

    def Initialise(self,frame,popout = False):
        self.frame = ttk.Frame(frame)
        self.frame.grid_rowconfigure(0,weight=1)
        self.frame.grid_columnconfigure(1,weight=1)
        self.toolbarIconPath = self.UIMaster.exeDir/"Functions"/"icons"
        self.fig = Figure(figsize=(self.UIMaster.root.winfo_screenheight()/self.UIMaster.root.winfo_fpixels("1i")/1.95,self.UIMaster.root.winfo_screenheight()/self.UIMaster.root.winfo_fpixels("1i")/1.95),dpi=150,constrained_layout=True)
        # self.gs = gridspec.GridSpec(nrows=2,ncols=3,figure=self.fig,width_ratios=[2,1,1])
        # self.ax = self.fig.add_subplot(self.gs[:,0])
        self.ax = self.fig.add_subplot(1,1,1)
        self.ax.set_aspect('equal')
        self.ax.tick_params(axis='y', direction='in', pad=-2,width=0.0,length=0.0)
        self.ax.tick_params(axis='x', direction='in', pad=-2,width=0.0,length=0.0)
        self.ax.tick_params(axis='y', which="minor", width=0.0,length=0.0)
        self.ax.tick_params(axis='x', which="minor", width=0.0,length=0.0)
        for label in self.ax.get_yticklabels():
            label.set_horizontalalignment('left')
            label.set_verticalalignment('bottom')
        for label in self.ax.get_xticklabels():
            label.set_horizontalalignment('left')
            label.set_verticalalignment('bottom')

        self.ax.grid(visible=True,which="major",axis="both",color="k",linestyle ="-",linewidth=0.5)
        self.ax.grid(visible=True,which="minor",axis="both",color="k",alpha = 0.7,linestyle= "-",linewidth=0.1)
        
        self.updateTimer = None
        self.mapDelay = 5000
        self.retry = 0
        self.retryDelay =500
        self.interactionTimer = None
        self.lastUpdateLimits = None
        self.isUpdating = False
        self.currentZoom = 0
        self.maxCacheSize = 100
        self.tileImages = []
        self.terrain = self.UIMaster.terrain.get()
        self.mapCanvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.mapCanvas.draw()
        self.toolbar = CustomToolbar(self,self.mapCanvas, self.frame,pack_toolbar=False,MessageLog = self.MessageLog,toolbarIconPath=self.toolbarIconPath,UIMaster=self.UIMaster,ax=self.ax,NextTargetInSeq=self.UIMaster.targetCreation.NextTargetInSeq)
        self.toolbar.home = self.ResetToDefaultView
        self.toolbar.grid(row=0, column=0, sticky='ns')
        self.toolbar.update()
        self.mapCanvas.get_tk_widget().grid(row=0, column=1, sticky='nsw')
        self.frame.grid(row=0,column=0,sticky="NSW")
        self.mapCanvas.mpl_connect('draw_event', self.OnDraw)
        self.ax.callbacks.connect("xlim_changed",self.OnLimitChange)
        #self.ax.callbacks.connect("ylim_changed",self.OnLimitChange)
        #self.mapCanvas.mpl_connect('scroll_event', self.OnZoom)
        #self.mapCanvas.mpl_connect('button_release_event', self.OnMouseRelease)
        if self.terrain!= "":
            self.SetTerrain(self.terrain)
        else:
            self.absXLimit = 10000
            self.absYLimit = 10000
            self.ax.set_xlim(0,10000)
            self.ax.set_ylim(0,10000)
        self.fig.set_layout_engine(layout="none")
        self.StartMarkerUpdate()
        self.toolbar.MapUpdateQueueCheck()
        self.ResetToDefaultView()
        self.UpdateAll()

    def SetTerrain(self,terrain = None):
        if terrain == None:
            tileLocation = self.UIMaster.baseDir/"Terrains"/self.terrain
        else:
            tileLocation = self.UIMaster.baseDir/"Terrains"/terrain
        self.settingsFile = TerrainSettingsFile(terrainFolder=tileLocation,StatusMessageErrorDump=self.StatusMessageErrorDump)
        self.settings = self.settingsFile.Get()
        self.toolbar.markSettings.LoadSettings(self.settings)
        self.toolbar.markSettings.settingsFileSaveFunction = self.settingsFile.Save
        if self.settings == {}:
            try:
                self.settingsFile.Save(entry={"X Limit" : self.UIMaster.maxCol-1,
                                              "Y Limit" : self.UIMaster.maxRow-1})
            except: None
        if self.settings != {}:
            try:
                self.absXLimit = self.settings["X Limit"]
                self.absYLimit = self.settings["Y Limit"]
                self.ax.set_xlim(0,self.settings["X Limit"])
                self.ax.set_ylim(0,self.settings["Y Limit"])
                self.loadedTerrainHeightMap = True
                try:
                    self.tileManager = MapTileManager(Path.joinpath(tileLocation,tileLocation.name+".terrainimage"),self.StatusMessageErrorDump,self)
                    self.loadedTerrainImage = True
                    try:
                        self.tileManager.customScale = self.settings["mapScaleCoef"]
                    except: None
                except Exception as e:
                    self.StatusMessageErrorDump(e,errorMessage="Failed to load Map tile manager")
                    self.loadedTerrainImage = False
            except:
                self.loadedTerrainHeightMap = False
                self.absXLimit = 10000
                self.absYLimit = 10000
                self.ax.set_xlim(0,10000)
                self.ax.set_ylim(0,10000)
        else:
            self.loadedTerrainHeightMap = False
            self.absXLimit = 10000
            self.absYLimit = 10000
            self.ax.set_xlim(0,10000)
            self.ax.set_ylim(0,10000)
            

    def UpdateFigureSize(self,width,height):
        self.fig = Figure(figsize=(width,height),dpi=150,tight_layout=True)
        self.fig.set_layout_engine(None)


    def ResetToDefaultView(self):
        self.ax.set_xlim(0, self.absXLimit)
        self.ax.set_ylim(0, self.absYLimit)
        self.UpdateMap()
        self.UpdateGrid()
        self.ax.get_figure(False).canvas.draw_idle()
        self.toolbar.push_current()
        self.UpdateFigureSize(6,6)
    def OnDraw(self, event):
        currentFigSize = self.fig.get_size_inches()
        if not hasattr(self,"lastFigSize"):
            self.lastFigSize = currentFigSize
            return
        if (currentFigSize[0] != self.lastFigSize[0] or currentFigSize[1] != self.lastFigSize[1]):
            self.lastFigSize = currentFigSize
            self.UpdateAll()

    def OnLimitChange(self,ax):
        self.UpdateAll()
    def OnZoom(self,event):
        self.UpdateAll()
    def OnMouseRelease(self,event):
        if event.button in [1,3]:
            self.UpdateAll()
    def ScheduleTileUpdate(self):
        if self.updateTimer is not None:
            self.frame.after_cancel(self.updateTimer)
        self.updateTimer = self.frame.after(50,self.UpdateMap)
    def DelayedUpdate(self):
        self.retry +=1
        self.UpdateAll()
    def UpdateAll(self):
        
        if not self.isUpdating:
            self.retry = 0
            self.UpdateGrid()
            self.ScheduleTileUpdate()
        elif self.retry < 3:
            self.frame.after(self.retryDelay, self.DelayedUpdate())
        else:
            self.retry = 0

    def UpdateMap(self):
        if self.loadedTerrainImage:
            self.updateTimer = None
            self.isUpdating = True
            xLim = self.ax.get_xlim()
            yLim = self.ax.get_ylim()
            zoom = self.tileManager.GetZoomLevelFromScale(xLim,yLim,(self.absXLimit,self.absYLimit))
            tiles, tileSize = self.tileManager.GetTilesInView(xLim,yLim,zoom,(self.absXLimit,self.absYLimit))
            for image in self.tileImages:
                image.remove()
            self.tileImages.clear()
            for xTile,yTile in tiles:
                tileData = self.tileManager.GetTile(zoom,xTile,yTile)
                if tileData is not None:
                    xPos = xTile * tileSize[0]
                    yPos = yTile * tileSize[1]
                    yPos = (yTile * tileSize[1]) - (self.settings["Y Limit"]*self.settings["mapScaleCoef"]-self.settings["Y Limit"])
                    img = self.ax.imshow(tileData,extent=[xPos,xPos+tileSize[0],self.absYLimit-(yPos+tileSize[1]),self.absYLimit-yPos],aspect="equal",zorder=0,interpolation="bilinear")
                    self.tileImages.append(img)
            self.currentZoom = zoom
            self.lastUpdateLimits=(self.ax.get_xlim(),self.ax.get_ylim())
            self.ax.get_figure(False).canvas.draw_idle()
            self.isUpdating = False
    def GetTickIntervals(self, rangeSize):
        """Determine appropriate tick intervals based on range size"""
        if rangeSize > 10000:
            return 10000, 1000 # major, minor
        elif rangeSize > 2000:
            return 1000, 100
        elif rangeSize > 200:
            return 100, 10
        else: return 10,1
    def UpdateGrid(self):
        xlim = self.ax.get_xlim()
        x_range = xlim[1] - xlim[0]
        x_major, x_minor = self.GetTickIntervals(x_range)
        y_major, y_minor = self.GetTickIntervals(x_range)
        self.ax.xaxis.set_major_locator(MultipleLocator(x_major))
        self.ax.xaxis.set_minor_locator(MultipleLocator(x_minor))
        self.ax.yaxis.set_major_locator(MultipleLocator(y_major))
        self.ax.yaxis.set_minor_locator(MultipleLocator(y_minor))
        self.ax.grid(visible=True,which="major",axis="both",color="k",linestyle ="-",linewidth=0.5)
        self.ax.grid(visible=True,which="minor",axis="both",color="k",alpha = 0.7,linestyle= "-",linewidth=0.1)

class CustomToolbar(NavigationToolbar2Tk):
    toolitems=[]
    customToolItems = [
        ("Home", "Full sized map", "home","home"),
        ("Pan", "Pan axes with left mouse", "move", "pan"),
        ("Zoom", "Zoom to square", "zoom_to_rect", "zoom"),
        (None, None, None, None),
        ("FPF","Create FPF Fire Mission", "FPF", "FPF"),
        ("LR","Create LR Fire Mission", "LR", "LR"),
        ("XY","Create XY Fire Mission", "XY", "XY"),
        (None, None, None, None),
        ("Snapshot","Snapshot Fire Mission", "snapshot", "Snapshot"),
        (None, None, None, None),
        ("Reference Points", "Calibrate Map by clicking the edge of the map", "reference points", "ReferencePoints"),
        ("Marker Settings", "Configure settings for various map markers", "marker settings","MarkerSettings"),
        (None,None,None,None),
        ("Subplots", "Configure subplots", "subplots", "configure_subplots"),
        ("Save", "Save the figure", "filesave", "save_figure")
    ]
    """Text, Tootip, Image file, callback"""
    mode: Mode
    def __init__(self,mainMatplotlibWidget:MatPlotLibWidget, canvas, window=None, *, pack_toolbar,MessageLog,toolbarIconPath,UIMaster,ax,NextTargetInSeq):
        super().__init__(canvas, window, pack_toolbar=pack_toolbar)
        self.root = UIMaster.root
        self.UIMaster = UIMaster
        # self.UIMaster = CastUI(self.UIMaster)
        self.mainWidget = mainMatplotlibWidget
        self.ax = ax
        self.canvas.mpl_connect("scroll_event",self.OnScroll)
        self.squareSelector = None
        self._zoom_info = None
        self.MessageLog = MessageLog
        self.NextTargetInSeq = NextTargetInSeq
        self.zoomError = False
        self.toolBarIconPath = toolbarIconPath
        self.mapPress = self.canvas.mpl_connect("button_press_event", self.InteratctionHandler)
        self.mapRelease = self.canvas.mpl_connect("button_release_event", self.InteratctionHandler)
        self.mapMouseMotion = self.canvas.mpl_connect("motion_notify_event", self.mouse_move)
        self._buttons = {}
        self._last_cursor = Cursors.POINTER
        self.contextToplevel = None
        self.markSettings = MarkerSettings()
        self.markDictionary = {}
        for text, tooltip_text, image_file, callback in self.customToolItems:
            if text is None:
                # Add a spacer; return value is unused.
                self._Spacer()
            else:
                if text in ["Home","Pan","Zoom","Subplots","Save"]:
                    self._buttons[text] = button = self._Button(
                        text,
                        str(cbook._get_data_path(f"images/{image_file}.png")),
                        toggle=callback in ["zoom", "pan"],
                        command=getattr(self, callback),
                    )
                else:
                    self._buttons[text] = button = self._Button(
                        text,
                        str(Path.joinpath(self.toolBarIconPath,f"{image_file}.png")),
                        toggle=callback in ["zoom", "pan", "FPF","LR","XY","Snapshot","ReferencePoints","MarkerSettings"],
                        command=getattr(self, callback),
                    )
                if tooltip_text is not None:
                    add_tooltip(button, tooltip_text)
        self.mapProcessQueue = queue.Queue()

    def MapUpdateQueueCheck(self):
        try:
            while True:
                task,*args = self.mapProcessQueue.get_nowait()
                if task == "markerUpdate":
                    process,json = args
                    self.ProcessMap(process,json)
                if task == "markerClear":
                    process = args[0]
                    self.MapMarkerClear(process)
                self.ax.get_figure(False).canvas.draw_idle()
        except queue.Empty:
            pass
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to update map, queue size: {str(self.mapProcessQueue.qsize())}")
        self.root.after(50,self.MapUpdateQueueCheck)
    def ProcessMap(self,process,json):
        try:
            if "error" in process:
                self.UIMaster.StatusMessageLog(process['error'])
                return
            self.MapMarkerClear(process)
            self.SetMarkers(process,json)
        except Exception as e:
            self.UIMaster.StatusMessageErrorDump(e,errorMessage="messed up thread")

    def MapUpdate(self,marker: Mark | list | tuple | None = None):
        if marker is None:
            markerList = [Mark.IDFP,Mark.FPF,Mark.LR,Mark.XY,Mark.GROUP,Mark.NOFLY,Mark.FRIENDLY]
        elif isinstance(marker, (list,tuple)):
            markerList = marker
        else:
            markerList = [marker]
        def FetchMarker(marker):
            fetchedJson = {}
            try:
                if marker is Mark.IDFP:
                    if self.markSettings.ReturnSettings("visible_IDFP")["visible_IDFP"].get() == "1":
                        fetchedJson["IDFP"] = self.UIMaster.castJson.Load(JsonSource.IDFP)
                        if fetchedJson["IDFP"] != {}:
                            self.mapProcessQueue.put(("markerUpdate",Mark.IDFP,fetchedJson))
                        else:
                            self.mapProcessQueue.put(("markerClear",Mark.IDFP))
                    else:
                        self.mapProcessQueue.put(("markerClear",Mark.IDFP))
                elif marker in [Mark.FPF,Mark.LR,Mark.XY,Mark.GROUP,Mark.NOFLY]:
                    if self.markSettings.ReturnSettings(f"visible_{marker}")[f"visible_{marker}"].get() == "1" or self.markSettings.ReturnSettings(f"visible_{marker}Bounds")[f"visible_{marker}Bounds"].get() =="1":
                        fetchedJson["IDFP"] = self.UIMaster.castJson.Load(JsonSource.IDFP)
                        fetchedJson["TARGET"] = self.UIMaster.castJson.Load(JsonSource.TARGET)
                        fetchedJson["FIREMISSION"] = self.UIMaster.castJson.Load(JsonSource.FIREMISSION)
                        if fetchedJson["IDFP"] != {} and fetchedJson["TARGET"] != {}:
                            if self.markSettings.ReturnSettings(f"visible_{marker}")[f"visible_{marker}"].get() == "1":
                                self.mapProcessQueue.put(("markerUpdate",marker,fetchedJson))
                            else:
                                self.mapProcessQueue.put(("markerClear",marker))
                            if self.markSettings.ReturnSettings(f"visible_{marker}Bounds")[f"visible_{marker}Bounds"].get() =="1":
                                self.mapProcessQueue.put(("markerUpdate",f"{marker}Bounds",fetchedJson))
                            else:
                                self.mapProcessQueue.put(("markerClear",f"{marker}Bounds"))
                        else:
                            self.mapProcessQueue.put(("markerClear",marker))
                            self.mapProcessQueue.put(("markerClear",f"{marker}Bounds"))
                    else:
                        self.mapProcessQueue.put(("markerClear",marker))
                        self.mapProcessQueue.put(("markerClear",f"{marker}Bounds"))
                elif marker is Mark.FRIENDLY or marker == "friendly":
                    if self.markSettings.ReturnSettings("visible_friendly")["visible_friendly"].get() == "1" or self.markSettings.ReturnSettings("visible_friendlyBounds")["visible_friendlyBounds"].get() =="1":
                        fetchedJson["FRIENDLY"] = self.UIMaster.castJson.Load(JsonSource.FRIENDLY)
                        if fetchedJson["FRIENDLY"] != {}:
                            if self.markSettings.ReturnSettings("visible_friendly")["visible_friendly"].get() == "1":
                                self.mapProcessQueue.put(("markerUpdate",Mark.FRIENDLY,fetchedJson))
                            else:
                                self.mapProcessQueue.put(("markerClear",Mark.FRIENDLY))
                            if self.markSettings.ReturnSettings("visible_friendlyBounds")["visible_friendlyBounds"].get() =="1":
                                self.mapProcessQueue.put(("markerUpdate",Mark.FRIENDLY_BOUNDS,fetchedJson))
                            else:
                                self.mapProcessQueue.put(("markerClear",Mark.FRIENDLY_BOUNDS))
                        else:
                            self.mapProcessQueue.put(("markerClear",Mark.FRIENDLY))
                            self.mapProcessQueue.put(("markerClear",Mark.FRIENDLY_BOUNDS))
                    else:
                        self.mapProcessQueue.put(("markerClear",Mark.FRIENDLY))
                        self.mapProcessQueue.put(("markerClear",Mark.FRIENDLY_BOUNDS))
                elif marker in [Mark.FPF_BOUNDS,Mark.LR_BOUNDS,Mark.XY_BOUNDS,Mark.GROUP_BOUNDS,Mark.FRIENDLY_BOUNDS,Mark.NOFLY_BOUNDS]:
                    if marker in [Mark.FRIENDLY_BOUNDS]:
                        fetchedJson["FRIENDLY"] = self.UIMaster.castJson.Load(JsonSource.FRIENDLY)
                    else:
                        fetchedJson["IDFP"] = self.UIMaster.castJson.Load(JsonSource.IDFP)
                        fetchedJson["TARGET"] = self.UIMaster.castJson.Load(JsonSource.TARGET)
                        fetchedJson["FIREMISSION"] = self.UIMaster.castJson.Load(JsonSource.FIREMISSION)
                    if self.markSettings.ReturnSettings(f"visible_{marker}")[f"visible_{marker}"].get()=="1":
                        self.mapProcessQueue.put(("markerUpdate",marker,fetchedJson))
                    else:
                        self.mapProcessQueue.put(("markerClear",marker))

            except Exception as e:
                self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to load JSON: {str(e)}")
        for markInList in markerList:
            threading.Thread(target=lambda mark = markInList: FetchMarker(mark),daemon=True).start()
            # if hasattr(self,"thread"):
            #     if not self.thread.is_alive():
            #         self.thread = threading.Thread(target=lambda mark = markInList: FetchMarker(mark),daemon=True)
            #         self.thread.start()
            # else:
            #     self.thread = threading.Thread(target=lambda mark = markInList: FetchMarker(mark),daemon=True)
            #     self.thread.start()
        if marker is None:
            self.mainWidget.markerUpdateEvent = self.root.after(self.mainWidget.mapDelay,self.MapUpdate)
    def _Button(self, text, image_file, toggle, command):
        b = super()._Button(text, image_file, toggle, command)
        b.pack(side=TOP)
        return b
    def mouse_move(self, event):
        self._update_cursor(event)

    def _update_cursor(self, event):
            """
            Update the cursor after a mouse move event or a tool (de)activation.
            """
            if self.mode and event.inaxes and event.inaxes.get_navigate():
                if (self.mode in [Mode.ZOOM, Mode.REFERENCE]
                        and self._last_cursor != Cursors.SELECT_REGION):
                    self.canvas.set_cursor(Cursors.SELECT_REGION)
                    self._last_cursor = Cursors.SELECT_REGION
                elif (self.mode == Mode.PAN and self._last_cursor != Cursors.MOVE):
                    self.canvas.set_cursor(Cursors.MOVE)
                    self._last_cursor = Cursors.MOVE
                elif ((self.mode in [Mode.FPF, Mode.LR, Mode.XY, Mode.QUICK]) and self._last_cursor != Cursors.POINTER):
                    self.canvas.set_cursor(Cursors.POINTER)
                    self._last_cursor = Cursors.POINTER
            elif self._last_cursor != Cursors.POINTER:
                self.canvas.set_cursor(Cursors.POINTER)
                self._last_cursor = Cursors.POINTER

    def _Spacer(self):
        s = Frame(self,width=26,relief="ridge",bg="DarkGray",padx =2)
        s.pack(side=TOP,pady=5)
        return s
    
    def set_message(self, s):
        pass

    def InteratctionHandler(self,event):
        if self.mode != Mode.NONE:
            if event.name == "button_press_event":
                if self.mode == Mode.PAN:
                    self.press_pan(event)
                elif self.mode == Mode.ZOOM:
                    self.press_zoom(event)
                elif self.mode == Mode.FPF:
                    self.press_FPF(event)
                elif self.mode == Mode.LR:
                    self.press_LR(event)
                elif self.mode == Mode.XY:
                    self.press_XY(event)
                elif self.mode == Mode.QUICK:
                    self.press_Snapshot(event)
                elif self.mode == Mode.REFERENCE:
                    self.press_Reference(event)
            elif event.name == "button_release_event":
                if self.mode == Mode.PAN:
                    self.release_pan(event)
                elif self.mode == Mode.ZOOM:
                    self.release_zoom(event)
                elif self.mode == Mode.FPF:
                    self.release_FPF(event)
                elif self.mode == Mode.LR:
                    self.release_LR(event)
                elif self.mode == Mode.XY:
                    self.release_XY(event)
                elif self.mode == Mode.QUICK:
                    self.release_Snapshot(event)
                elif self.mode == Mode.REFERENCE:
                    self.release_Reference(event)
                else:
                    self.release_Unselected(event)
        else:
            if event.name == "button_release_event":
                self.release_Unselected(event)


    def _update_buttons_checked(self):
        # sync button checkstates to match active mode
        for text, mode in [('Zoom', Mode.ZOOM), ('Pan', Mode.PAN),("FPF",Mode.FPF),("LR",Mode.LR),("XY",Mode.XY),("Snapshot",Mode.QUICK),("Reference Points",Mode.REFERENCE),("Marker Settings",Mode.MARKER)]:
            if text in self._buttons:
                if self.mode == mode:
                    self._buttons[text].select()  # NOT .invoke()
                else:
                    self._buttons[text].deselect()
        if self.contextToplevel is None and self.mode in [Mode.FPF, Mode.LR, Mode.XY, Mode.QUICK,Mode.REFERENCE,Mode.MARKER]:
            if self.mode == Mode.FPF:
                selection = "FPF Target"
            elif self.mode == Mode.LR:
                selection = "LR Target"
            elif self.mode == Mode.XY:
                selection = "LR Target"
            elif self.mode == Mode.QUICK:
                selection = "Snapshot Target"
            elif self.mode == Mode.REFERENCE:
                selection = "Reference Points"
            elif self.mode == Mode.MARKER:
                selection = "Marker Settings"
            else: selection = ""
            def CloseContextWindow():
                self.contextToplevel.destroy()
                self.contextToplevel = None
                self.mode = Mode.NONE
                self._update_buttons_checked()
                self.canvas.widgetlock.release(self)
            self.contextToplevel = Toplevel(self.root)
            self.contextToplevel.attributes("-toolwindow",True,"-topmost",True)
            self.contextToplevel.resizable(True,True)
            self.contextToplevel.title(selection)
            self.contextToplevel.geometry("150x70+30+30")
            self.contextToplevel.protocol("WM_DELETE_WINDOW",CloseContextWindow)
            self.contextWindow = self.contextToplevel.winfo_toplevel()
            self.contextWindow.anchor("nw")
            self.contextWindow.grid_columnconfigure(0,weight=1)
            self.contextWindow.grid_rowconfigure(0,weight=1)
            self.contextFrame = ttk.Frame(self.contextWindow,padding=10,relief="groove")
            self.contextFrame.action = None
            self.toolbarContext = ToolbarContextWindow(self.contextFrame,self.toolBarIconPath,self,self.MapUpdate,self.markSettings.ReturnSettings().items())
            if self.mode == Mode.FPF: self.toolbarContext.FPF()
            elif self.mode == Mode.LR: self.toolbarContext.LR()
            elif self.mode == Mode.XY: self.toolbarContext.XY()
            elif self.mode == Mode.QUICK: self.toolbarContext.Snapshot()
            elif self.mode == Mode.REFERENCE: self.toolbarContext.Reference()
            elif self.mode == Mode.MARKER: self.toolbarContext.Marker()
        elif self.contextToplevel is not None and self.mode in [Mode.FPF, Mode.LR, Mode.XY, Mode.QUICK,Mode.REFERENCE,Mode.MARKER]:
            if self.mode == Mode.FPF:
                self.contextToplevel.title("FPF Target")
                self.toolbarContext.FPF()
            elif self.mode == Mode.LR:
                self.contextToplevel.title("LR Target")
                self.toolbarContext.LR()
            elif self.mode == Mode.XY:
                self.contextToplevel.title("LR Target")
                self.toolbarContext.XY()
            elif self.mode == Mode.QUICK:
                self.contextToplevel.title("Snapshot Target")
                self.toolbarContext.Snapshot()
            elif self.mode == Mode.REFERENCE:
                self.contextToplevel.title("Reference Points")
                self.toolbarContext.Reference()
            elif self.mode == Mode.MARKER:
                self.contextToplevel.title("Marker Settings")
                self.toolbarContext.Marker()
            else:
                selection = ""
                self.contextToplevel.title("Marker Settings")
        elif self.contextToplevel is not None and self.mode not in [Mode.FPF, Mode.LR, Mode.XY, Mode.QUICK,Mode.REFERENCE,Mode.MARKER]:
            self.contextToplevel.destroy()
            self.contextToplevel = None
            self._update_buttons_checked()
            self.canvas.widgetlock.release(self)



    def MapMarkerClear(self,marker: Mark | None = None):
        if marker is None:
            for markers in self.markDictionary.values():
                if type(markers) is list:
                    for mark in markers:
                        mark.remove()
                if type(markers) is dict:
                    for mark in markers.values():
                        for i in mark:
                            i.remove()
            self.markDictionary = {}
        else:
            for markerType,markers in self.markDictionary.items():
                if markerType == marker:
                    if type(markers) is list:
                        for mark in markers:
                            mark.remove()
                        self.markDictionary[markerType] = []
                    if type(markers) is dict:
                        for mark in markers.values():
                            for i in mark:
                                i.remove()
                        self.markDictionary[markerType] = {}
    
    def SetMarkers(self,markerType: Mark | list,fetchedJson):
        def IDFPS(idfp):
            for idfp, details in idfp.items():
                x = int(details["GridX"]) if len(details["GridX"]) == 5 else int(details["GridX"] + "0")
                y = int(details["GridY"]) if len(details["GridY"]) == 5 else int(details["GridY"] + "0")
                size = self.markSettings.ReturnSettings("size_IDFP")["size_IDFP"].get()
                marking = MapMarking((x,y),self.ax,size=size)
                if self.markSettings.ReturnSettings("declutter_IDFP")["declutter_IDFP"].get() == "0":
                    axFlag = marking.Flag(colour="#0084FF",text=idfp.upper())
                else:
                    axFlag = marking.Flag(colour="#0084FF")
                if Mark.IDFP not in self.markDictionary:
                    self.markDictionary[Mark.IDFP] = []
                self.markDictionary[Mark.IDFP].append(axFlag)

        def Targets(targetType: Literal["FPF","XY","LR"],targets,size):
            if targetType in targets:
                for target,details in targets[targetType].items():
                    x = int(details["GridX"]) if len(details["GridX"]) == 5 else int(details["GridX"] + "0")
                    y = int(details["GridY"]) if len(details["GridY"]) == 5 else int(details["GridY"] + "0")
                    marking = MapMarking((x,y),self.ax,size=size)
                    axCross = marking.Cross(colour="#FF9100",text=f"{targetType}-{target}")
                    if str(targetType) not in self.markDictionary:
                        self.markDictionary[targetType] = []
                    self.markDictionary[targetType].append(axCross)
        def Friendlies(friendlies,bounds=False):
            for friendly, details in friendlies.items():
                x = int(details["GridX"]) if len(details["GridX"]) == 5 else int(details["GridX"] + "0")
                y = int(details["GridY"]) if len(details["GridY"]) == 5 else int(details["GridY"] + "0")
                
                if bounds and float(details["Dispersion"]) > 0.0:
                    marking = MapMarking((x,y),self.ax,size=self.markSettings.ReturnSettings("size_friendlyBounds")["size_friendlyBounds"].get())
                    axBound = marking.Bounds(orientation="grid",distance=details["Dispersion"],style=self.markSettings.ReturnSettings("linestyle_friendlyBounds")["linestyle_friendlyBounds"].get(),colour="#0084FF",doubleStyle=self.markSettings.ReturnSettings("double_linestyle_friendlyBounds")["double_linestyle_friendlyBounds"].get(),doubleSide=self.markSettings.ReturnSettings("double_side_friendlyBounds")["double_side_friendlyBounds"].get())
                    if Mark.FRIENDLY_BOUNDS not in self.markDictionary:
                        self.markDictionary[Mark.FRIENDLY_BOUNDS] = []
                    self.markDictionary[Mark.FRIENDLY_BOUNDS].append(axBound)
                elif bounds == False:
                    marking = MapMarking((x,y),self.ax,size=self.markSettings.ReturnSettings("size_friendly")["size_friendly"].get())
                    if self.markSettings.ReturnSettings("declutter_friendly")["declutter_friendly"].get() == "0":
                        axExclamation = marking.Exclamation(colour="#0084FF",text=f"{friendly.upper()}")
                    else:
                        axExclamation = marking.Exclamation(colour="#0084FF")
                    if Mark.FRIENDLY not in self.markDictionary:
                        self.markDictionary[Mark.FRIENDLY] = []
                    self.markDictionary[Mark.FRIENDLY].append(axExclamation)
        def TargetBounds(targetType: Literal["FPF","XY","LR"],targets,idfpDetails,fireMissions):
            size = "size_"+targetType+"Bounds"
            style = "linestyle_"+targetType+"Bounds"
            doubleStyle = "double_linestyle_"+targetType+"Bounds"
            side = "double_side_"+targetType+"Bounds"
            settings = self.markSettings.ReturnSettings(size,style,doubleStyle,side)
            if targetType in targets:
                for target,details in targets[targetType].items():
                    if details["Width"] > 0.0 or details["Depth"] > 0.0:
                        x = int(details["GridX"]) if len(details["GridX"]) == 5 else int(details["GridX"] + "0")
                        y = int(details["GridY"]) if len(details["GridY"]) == 5 else int(details["GridY"] + "0")
                        marking = MapMarking((x,y),self.ax,size=settings[size].get())
                        idfpsTemp = []
                        idfps = []
                        for idfp,missions in fireMissions.items():
                            gridX = int(idfpDetails[idfp]["GridX"]) if len(idfpDetails[idfp]["GridX"]) == 5 else int(idfpDetails[idfp]["GridX"]+"0")
                            gridY = int(idfpDetails[idfp]["GridY"]) if len(idfpDetails[idfp]["GridY"]) == 5 else int(idfpDetails[idfp]["GridY"]+"0")
                            if f"{targetType}-{target}" in missions.keys():
                                width = missions[f"{targetType}-{target}"]["DeviationWidth"] if "DeviationWidth" in missions[f"{targetType}-{target}"] else 5
                                depth = missions[f"{targetType}-{target}"]["DeviationLength"] if "DeviationLength" in missions[f"{targetType}-{target}"] else 5
                                idfpsTemp.append(((gridX,gridY),width,depth))
                                if idfp in self.UIMaster.idfpCreation.idfpListBoxContents.get():
                                    idfps.append(((gridX,gridY),width,depth))
                            if idfps == []:
                                idfps = idfpsTemp
                        if idfps == []:
                            axBound = marking.Bounds(orientation="circle",distance=max(float(details["Width"]),float(details["Depth"])),style=settings[style].get(),colour="#FF9100",doubleStyle=settings[doubleStyle].get(),doubleSide=settings[side].get())
                        else:
                            for idfpPos in idfps:
                                if type(idfpPos) is tuple:
                                    axBound = marking.Bounds(orientation="orthogonal",distance={"Width":float(idfpPos[1]),"Depth":float(idfpPos[2]),"Origin":idfpPos[0]},style=settings[style].get(),colour="#FF9100",doubleStyle=settings[doubleStyle].get(),doubleSide=settings[side].get())
                                else:
                                    print("list error")
                        if targetType+"Bounds" not in self.markDictionary:
                            self.markDictionary[targetType+"Bounds"] = []
                        self.markDictionary[targetType+"Bounds"].append(axBound)
        def NoFlyZones(fireMissions,targets,idfpDetails,IDFP: str | None = None,target: str | None = None,bounds = False):
            if bounds:
                idfpList = []
                if IDFP is None:
                    for key in fireMissions.keys():
                        idfpList.append(key)
                else:
                    idfpList = [IDFP]
                for idfp in idfpList:
                    gridX = int(idfpDetails[idfp]["GridX"]) if len(idfpDetails[idfp]["GridX"]) == 5 else int(idfpDetails[idfp]["GridX"] + "0")
                    gridY = int(idfpDetails[idfp]["GridY"]) if len(idfpDetails[idfp]["GridY"]) == 5 else int(idfpDetails[idfp]["GridY"] + "0")
                    if target is None:
                        for targetName,details in fireMissions[idfp].items():
                            targetName = targetName.split("-")
                            x = int(targets[targetName[0]][targetName[1]]["GridX"]) if len(targets[targetName[0]][targetName[1]]["GridX"]) == 5 else int(targets[targetName[0]][targetName[1]]["GridX"] + "0")
                            y = int(targets[targetName[0]][targetName[1]]["GridY"]) if len(targets[targetName[0]][targetName[1]]["GridY"]) == 5 else int(targets[targetName[0]][targetName[1]]["GridY"] + "0")
                            marking = MapMarking((x,y),self.ax,self.markSettings.ReturnSettings("size_noflyBounds")["size_noflyBounds"].get())
                            width = float(details["DeviationWidth"])+25 if "DeviationWidth" in details.keys() else 25
                            depth = float(details["DeviationLength"])+25 if "DeviationLength" in details.keys() else 25
                            axBound = marking.Bounds("orthogonal",{"Width":width,"Depth":depth,"Origin":(gridX,gridY)},self.markSettings.ReturnSettings("linestyle_noflyBounds")["linestyle_noflyBounds"].get(),"#BB0000",self.markSettings.ReturnSettings("double_linestyle_noflyBounds")["double_linestyle_noflyBounds"].get(),self.markSettings.ReturnSettings("double_side_noflyBounds")["double_side_noflyBounds"].get(),noflyZone=True)
                            if Mark.NOFLY_BOUNDS not in self.markDictionary:
                                self.markDictionary[Mark.NOFLY_BOUNDS] = []
                            self.markDictionary[Mark.NOFLY_BOUNDS].append(axBound)
            else:
                for missions in fireMissions.values():
                    for mission, details in missions.items():
                        x = int(details["Vertex"][0]) if len(details["Vertex"][0]) == 5 else int(details["Vertex"][0] + "0")
                        y = int(details["Vertex"][1]) if len(details["Vertex"][1]) == 5 else int(details["Vertex"][1] + "0")
                        marking = MapMarking((x,y),self.ax,self.markSettings.ReturnSettings("size_nofly")["size_nofly"].get())
                        if self.markSettings.ReturnSettings("declutter_nofly")["declutter_nofly"].get()=="1":
                            axExclamation = marking.Exclamation(colour="#BB0000",text=f"{int(np.ceil(round(float(details['Vertex'][2]))/5)*5)}")
                        else:
                            axExclamation = marking.Exclamation(colour="#BB0000",text=f"NO FLY Ceiling FL {int(np.ceil(round(float(details['Vertex'][2]))/5)*5)}")
                        if "nofly" not in self.markDictionary:
                            self.markDictionary["nofly"] = {}
                        if mission.split("-")[0] not in self.markDictionary["nofly"]:
                            self.markDictionary["nofly"][mission.split('-')[0]] = []
                        self.markDictionary["nofly"][mission.split("-")[0]].append(axExclamation)


        if type(markerType) is not list:
            markerType = [markerType]
        if any(x in set(markerType) for x in ("all",Mark.IDFP,Mark.FPF,Mark.FPF,Mark.FPF_BOUNDS,Mark.LR,Mark.LR_BOUNDS,Mark.XY,Mark.XY_BOUNDS,Mark.GROUP,Mark.GROUP_BOUNDS,Mark.NOFLY,Mark.NOFLY_BOUNDS)):
            idfps = fetchedJson["IDFP"]
        if any(x in set(markerType) for x in ("all","FPF","FPFBounds","LR","LRBounds","XY","XYBounds","Group","GroupBounds","nofly","noflyBounds")):
            targets = fetchedJson["TARGET"]
        if any(x in set(markerType) for x in ("all","FPF","FPFBounds","LR","LRBounds","XY","XYBounds","Group","GroupBounds","nofly","noflyBounds")):
            fireMissions = fetchedJson["FIREMISSION"]
        if any(x in set(markerType) for x in ("all","friendly","friendlyBounds")):
            friendlies = fetchedJson["FRIENDLY"]
        for marker in markerType:
            if marker in ("all",Mark.IDFP):
                IDFPS(idfps)
            elif marker in ("all",Mark.FPF,Mark.XY,Mark.LR):
                marker = [Mark.FPF,Mark.XY,Mark.LR] if marker == "all" else [marker]
                for index in marker:
                    if index == Mark.FPF:
                        Targets(index,targets=targets,size=self.markSettings.ReturnSettings("size_FPF")["size_FPF"].get())
                    if index == Mark.XY:
                        Targets(index,targets=targets,size=self.markSettings.ReturnSettings("size_XY")["size_XY"].get())
                    if index == Mark.LR:
                        Targets(index,targets=targets,size=self.markSettings.ReturnSettings("size_LR")["size_LR"].get())
                if marker == [Mark.FPF,Mark.XY,Mark.LR]:
                    marker = "all"
            
            elif marker in ("all",Mark.FPF_BOUNDS,Mark.XY_BOUNDS,Mark.LR_BOUNDS):
                marker = [Mark.FPF,Mark.XY,Mark.LR] if marker == "all" else [marker]
                for index in marker:
                    if index == Mark.FPF_BOUNDS.__str__():
                        TargetBounds(Mark.FPF,targets=targets,idfpDetails = idfps,fireMissions=fireMissions)
                    if index == Mark.LR_BOUNDS.__str__():
                        TargetBounds(Mark.LR,targets=targets,idfpDetails = idfps,fireMissions=fireMissions)
                    if index == Mark.XY_BOUNDS.__str__():
                        TargetBounds(Mark.XY,targets=targets,idfpDetails = idfps,fireMissions=fireMissions)
                if marker == [Mark.FPF,Mark.XY,Mark.LR]:
                    marker = "all"
            elif marker in ("all",Mark.NOFLY):
                NoFlyZones(fireMissions,targets,idfps)
            elif marker in ("all",Mark.NOFLY_BOUNDS):
                NoFlyZones(fireMissions,targets,idfps,bounds= True)
            elif marker in ("all",Mark.FRIENDLY):
                Friendlies(friendlies)
            elif marker in ("all",Mark.FRIENDLY_BOUNDS):
                Friendlies(friendlies,bounds=True)
            # elif marker in ("FPF","XY","LR"):
            #     for target,details in targets[type].items():
            #         Targets(targetType=type,targets=targets)

    def OnScroll(self,event):
        currentAxes = event.inaxes
        if currentAxes is None:
            return None
        zoomFactor = 1.2 if event.button == "up" else 0.8
        currentXLim,currentYLim = currentAxes.get_xlim(),currentAxes.get_ylim()
        xPos, yPos = event.xdata, event.ydata
        newWidth = (currentXLim[1]-currentXLim[0])/zoomFactor
        newHeight = (currentYLim[1]-currentYLim[0])/zoomFactor

        weightX = (currentXLim[1]-xPos)/(currentXLim[1]-currentXLim[0])
        weightY = (currentYLim[1]-yPos)/(currentYLim[1]-currentYLim[0])

        currentAxes.set_xlim([xPos-newWidth*(1-weightX),xPos+newWidth*weightX])
        currentAxes.set_ylim([yPos-newHeight*(1-weightY),yPos+newHeight*weightY])
        self.canvas.draw_idle()

    _ZoomInfoCustom = namedtuple("_ZoomInfoCustom", "direction start_xy axes cid cbar start_xydata")

    def press_zoom(self, event):
        """Callback for mouse button press in zoom to rect mode."""
        if (event.button not in [MouseButton.LEFT, MouseButton.RIGHT]
                or event.x is None or event.y is None):
            return

        axes = self._start_event_axes_interaction(event, method="zoom")
        if not axes:
            return

        id_zoom = self.canvas.mpl_connect(
            "motion_notify_event", self.drag_zoom)

        # A colorbar is one-dimensional, so we extend the zoom rectangle out
        # to the edge of the Axes bbox in the other dimension. To do that we
        # store the orientation of the colorbar for later.
        parent_ax = axes[0]
        if hasattr(parent_ax, "_colorbar"):
            cbar = parent_ax._colorbar.orientation
        else:
            cbar = None

        self._zoom_info = self._ZoomInfoCustom(
            direction="in" if event.button == 1 else "out",
            start_xy=(event.x, event.y), axes=axes, cid=id_zoom, cbar=cbar,start_xydata=(event.xdata,event.ydata))

    def drag_zoom(self, event): 
        """Callback for dragging in zoom mode. Edited From backend_bases.py for CAST"""
        start_xy = self._zoom_info.start_xy
        extent = max(abs(start_xy[0]-event.x),abs(start_xy[1]-event.y))
        x = [start_xy[0]-extent,start_xy[0]+extent]
        y = [start_xy[1]-extent,start_xy[1]+extent]
        ax = self._zoom_info.axes[0]

        # (x1, y1), (x2, y2) = np.clip(
        #     [[x[0],y[0]], [x[1],y[1]]], ax.bbox.min, ax.bbox.max)
        # key = event.key
        # # Force the key on colorbars to extend the short-axis bbox
        # if self._zoom_info.cbar == "horizontal":
        #     key = "x"
        # elif self._zoom_info.cbar == "vertical":
        #     key = "y"
        # if key == "x":
        #     y1, y2 = ax.bbox.intervaly
        # elif key == "y":
        #     x1, x2 = ax.bbox.intervalx

        #self.draw_rubberband(event, x1, y1, x2, y2)
        if event.xdata != None and event.ydata != None:
            self.draw_rubberband(event, x[0], y[0], x[1], y[1])

    def release_zoom(self, event):
        """Callback for mouse button release in zoom to rect mode. Edited From backend_bases.py for CAST"""
        if self._zoom_info is None:
            return

        # We don't check the event button here, so that zooms can be cancelled
        # by (pressing and) releasing another mouse button.
        self.canvas.mpl_disconnect(self._zoom_info.cid)
        self.remove_rubberband()

        start_x, start_y = self._zoom_info.start_xy
        start_xData, start_yData = self._zoom_info.start_xydata
        if None in (event.xdata, event.ydata):
            self.MessageLog(privateMessage="Mouse was out of the map when zooming")
            if not self.zoomError:
                self.zoomError = True
            return
        else:
            extent = max(abs(start_xData-event.xdata),abs(start_yData-event.ydata))
            if self.zoomError:
                self.MessageLog(privateMessage="That's better, good job")
                self.zoomError = False
        x = [start_xData-extent,start_xData+extent]
        y = [start_yData-extent,start_yData+extent]
        key = event.key
        # Force the key on colorbars to ignore the zoom-cancel on the
        # short-axis side
        if self._zoom_info.cbar == "horizontal":
            key = "x"
        elif self._zoom_info.cbar == "vertical":
            key = "y"
        # Ignore single clicks: 5 pixels is a threshold that allows the user to
        # "cancel" a zoom action by zooming by less than 5 pixels.
        if ((abs(event.x - start_x) < 5 and key != "y") or
                (abs(event.y - start_y) < 5 and key != "x")):
            self.canvas.draw_idle()
            self._zoom_info = None
            return
        if event.button == MouseButton.RIGHT:
                oldXLim, oldYLim = self._zoom_info.axes[0].get_xlim(),self._zoom_info.axes[0].get_ylim()
                oldWidth = oldXLim[1] - oldXLim[0]
                boxWidth = x[1] - x[0]
                centerOldX = (oldXLim[0] + oldXLim[1]) / 2
                centerOldY = (oldYLim[0] + oldYLim[1]) / 2
                scale = oldWidth / boxWidth   # linear inverse scale
                newCenterX = start_xData + scale * (centerOldX - start_xData)
                newCenterY = start_yData + scale * (centerOldY - start_yData)
                newHalf = oldWidth / 2 * scale

                x = [newCenterX - newHalf, newCenterX + newHalf]
                y = [newCenterY - newHalf, newCenterY + newHalf]
                # centerOldX,centerOldY = (oldXLim[0] + oldXLim[1])/2,(oldYLim[0] + oldYLim[1])/2
                # centerNewX,centerNewY =start_xData,start_yData
                # scale = (x[1]-x[0])/(oldXLim[1]-oldXLim[0])
                # newCenter = [centerOldX+scale*(centerOldX-centerNewX),centerOldY+scale*(centerOldY-centerNewY)]
                # newSize = (oldXLim[1]-oldXLim[0])*(oldXLim[1]-oldXLim[0])/(2*(x[1]-x[0]))
                # print(newSize)
                # x = [newCenter[0]-newSize,newCenter[0]+newSize]
                # y = [newCenter[1]-newSize,newCenter[1]+newSize]
        for i, ax in enumerate(self._zoom_info.axes):
            # Detect whether this Axes is twinned with an earlier Axes in the
            # list of zoomed Axes, to avoid double zooming.
            twinx = any(ax.get_shared_x_axes().joined(ax, prev)
                        for prev in self._zoom_info.axes[:i])
            twiny = any(ax.get_shared_y_axes().joined(ax, prev)
                        for prev in self._zoom_info.axes[:i])

            ax.set_xlim(x[0],x[1])
            ax.set_ylim(y[0],y[1])
            # ax._set_view_from_bbox(
            #     (x[0], y[0], x[1], y[1]),
            #     self._zoom_info.direction, key, twinx, twiny)

        self.ax.get_figure(False).canvas.draw_idle()
        self._zoom_info = None
        self.push_current()
        
    def RemoveTempMarker(self,marker):
        if marker in self.markDictionary: self.markDictionary.pop(marker,None)[0].remove()
        self.ax.get_figure(False).canvas.draw_idle()
    def press_FPF(self,event):
        if self.contextFrame.action:
            if event.button == MouseButton.LEFT:
                self.canvas.set_cursor(Cursors.SELECT_REGION)

    def release_FPF(self,event):
        if self.contextFrame.action:
            if event.button == MouseButton.LEFT:
                self.canvas.set_cursor(Cursors.HAND)
                self.UIMaster.targetCreation.targetPosX.set("{:05d}".format(round(event.xdata)))
                self.UIMaster.targetCreation.targetPosY.set("{:05d}".format(round(event.ydata)))
                self.UIMaster.HeightAutoFill(None,self.UIMaster.targetCreation.targetPosX.get(),self.UIMaster.targetCreation.targetPosY.get(),self.UIMaster.targetCreation.targetHeight,noEvent = True)
                marking = MapMarking((event.xdata,event.ydata),self.ax,size=self.markSettings.ReturnSettings("size_FPF")["size_FPF"].get())
                axCross = marking.Cross(colour="#FF0080",text="FPF")
                if "tempMarker" in self.markDictionary: self.markDictionary.pop("tempMarker")[0].remove()
                self.markDictionary["tempMarker"] = [axCross]
                self.ax.get_figure(False).canvas.draw_idle()
                self.contextFrame.after(5000,lambda marker = "tempMarker": self.RemoveTempMarker(marker))
                self.toolbarContext.markButton.config(default="normal",text="Mark")
                self.contextFrame.action = False
    
    def press_LR(self,event):
        if self.contextFrame.action:
            if event.button == MouseButton.LEFT:
                self.canvas.set_cursor(Cursors.SELECT_REGION)

    def release_LR(self,event):
        if self.contextFrame.action:
            if event.button == MouseButton.LEFT:
                self.canvas.set_cursor(Cursors.HAND)
                self.UIMaster.targetCreation.targetPosX.set("{:05d}".format(round(event.xdata)))
                self.UIMaster.targetCreation.targetPosY.set("{:05d}".format(round(event.ydata)))
                self.UIMaster.HeightAutoFill(None,self.UIMaster.targetCreation.targetPosX.get(),self.UIMaster.targetCreation.targetPosY.get(),self.UIMaster.targetCreation.targetHeight,noEvent = True)
                marking = MapMarking((event.xdata,event.ydata),self.ax,size=self.markSettings.ReturnSettings("size_LR")["size_LR"].get())
                axCross = marking.Cross(colour="#FF0080",text="LR")
                if "tempMarker" in self.markDictionary: self.markDictionary.pop("tempMarker",None)[0].remove()
                self.markDictionary["tempMarker"] = [axCross]
                self.ax.get_figure(False).canvas.draw_idle()
                self.contextFrame.after(5000,lambda marker = "tempMarker": self.RemoveTempMarker(marker))
                self.toolbarContext.markButton.config(default="normal",text="Mark")
                self.contextFrame.action = False

    def press_XY(self,event):
        if self.contextFrame.action:
            if event.button == MouseButton.LEFT:
                self.canvas.set_cursor(Cursors.SELECT_REGION)

    def release_XY(self,event):
        if self.contextFrame.action:
            if event.button == MouseButton.LEFT:
                self.canvas.set_cursor(Cursors.HAND)
                self.UIMaster.targetCreation.targetPosX.set("{:05d}".format(round(event.xdata)))
                self.UIMaster.targetCreation.targetPosY.set("{:05d}".format(round(event.ydata)))
                self.UIMaster.HeightAutoFill(None,self.UIMaster.targetCreation.targetPosX.get(),self.UIMaster.targetCreation.targetPosY.get(),self.UIMaster.targetCreation.targetHeight,noEvent = True)
                marking = MapMarking((event.xdata,event.ydata),self.ax,size=self.markSettings.ReturnSettings("size_XY")["size_XY"].get())
                axCross = marking.Cross(colour="#FF0080",text="XY")
                if "tempMarker" in self.markDictionary: self.markDictionary.pop("tempMarker")[0].remove()
                self.markDictionary["tempMarker"] = [axCross]
                self.ax.get_figure(False).canvas.draw_idle()
                self.contextFrame.after(5000,lambda marker = "tempMarker": self.RemoveTempMarker(marker))
                self.toolbarContext.markButton.config(default="normal",text="Mark")
                self.contextFrame.action = False

    def press_Snapshot(self,event):
        if self.contextFrame.action:
            if event.button == MouseButton.LEFT:
                self.canvas.set_cursor(Cursors.SELECT_REGION)

    def release_Snapshot(self,event):
        if self.contextFrame.action:
            if event.button == MouseButton.LEFT:
                self.canvas.set_cursor(Cursors.POINTER)
            # try:
                self.toolbarContext.snapPosX.set("{:05d}".format(round(event.xdata)))
                self.toolbarContext.snapPosY.set("{:05d}".format(round(event.ydata)))
                marking = MapMarking((event.xdata,event.ydata),self.ax,size=self.markSettings.ReturnSettings("size_snapshot")["size_snapshot"].get())
                axCross = marking.Cross(colour="#FF0080",text="Snapshot")
                if "snapshot" in self.markDictionary: self.markDictionary.pop("snapshot",None)[0].remove()
                self.markDictionary["snapshot"] = [axCross]
                self.contextFrame.action = False
                self.ax.get_figure(False).canvas.draw_idle()

            # except:
            #     None       

    def press_Reference(self,event):
        if self.contextFrame.action is not None:
            if event.button == MouseButton.LEFT:
                self.canvas.set_cursor(Cursors.SELECT_REGION)
    
    def release_Reference(self,event):
        if self.contextFrame.action is not None and self.mainWidget.loadedTerrainImage:
            if event.button == MouseButton.LEFT:
                self.canvas.set_cursor(Cursors.SELECT_REGION)
            oldScaleCoef = self.mainWidget.settingsFile.Get("mapScaleCoef")
            if oldScaleCoef == {}:
                oldScaleCoef = 1.0
            newScaleCoef = oldScaleCoef * max(self.mainWidget.absXLimit,self.mainWidget.absYLimit)/max(abs(event.xdata),abs(event.ydata))
            self.mainWidget.settingsFile.Save("mapScaleCoef",newScaleCoef)
            self.mainWidget.tileManager.customScale = newScaleCoef
            self.toolbarContext.customScale.set(round(newScaleCoef,3))
            self.contextFrame.action = None

    def release_Unselected(self,event):
        for map in self.mainWidget.activeMaps.values():
            try:
                if map.toolbar.contextFrame.action is not None and map.toolbar.contextFrame.action:
                    if event.button == MouseButton.LEFT:
                        if map.toolbar.mode in (Mode.FPF,Mode.LR,Mode.XY,Mode):
                            self.UIMaster.targetCreation.targetPosX.set("{:05d}".format(round(event.xdata)))
                            self.UIMaster.targetCreation.targetPosY.set("{:05d}".format(round(event.ydata)))
                            self.UIMaster.HeightAutoFill(None,self.UIMaster.targetCreation.targetPosX.get(),self.UIMaster.targetCreation.targetPosY.get(),self.UIMaster.targetCreation.targetHeight,noEvent = True)
                            marking = MapMarking((event.xdata,event.ydata),self.ax,size=self.markSettings.ReturnSettings("size_LR")["size_LR"].get())
                            mark = {Mode.FPF: "FPF", Mode.LR: "LR", Mode.XY: "XY"}
                            axCross = marking.Cross(colour="#FF0080",text=mark[map.toolbar.mode])
                            if "tempMarker" in self.markDictionary: self.markDictionary.pop("tempMarker",None)[0].remove()
                            self.markDictionary["tempMarker"] = [axCross]
                            self.ax.get_figure(False).canvas.draw_idle()
                            map.toolbar.contextFrame.after(5000,lambda marker = "tempMarker": self.RemoveTempMarker(marker))
                            map.toolbar.toolbarContext.markButton.config(default="normal",text="Mark")
                            map.toolbar.contextFrame.action = False
                        elif map.toolbar.mode is Mode.QUICK:
                            map.toolbar.toolbarContext.snapPosX
                            map.toolbar.toolbarContext.snapPosX.set("{:05d}".format(round(event.xdata)))
                            map.toolbar.toolbarContext.snapPosY.set("{:05d}".format(round(event.ydata)))
                            marking = MapMarking((event.xdata,event.ydata),self.ax,size=self.markSettings.ReturnSettings("size_snapshot")["size_snapshot"].get())
                            axCross = marking.Cross(colour="#FF0080",text="Snapshot")
                            for map in self.mainWidget.activeMaps.values():
                                if "snapshot" in map.toolbar.markDictionary:
                                    map.toolbar.markDictionary.pop("snapshot",None)[0].remove()
                                    map.ax.get_figure(False).canvas.draw_idle()
                            self.markDictionary["snapshot"] = [axCross]
                            map.toolbar.contextFrame.action = False
                            self.ax.get_figure(False).canvas.draw_idle()
            except: None


    def FPF(self):
        if not self.canvas.widgetlock.available(self):
            self.set_message("Mission selection unavailable")
            return
        if self.mode == Mode.FPF:
            self.mode = Mode.NONE
            self.canvas.widgetlock.release(self)
        else:
            self.mode = Mode.FPF
            self.canvas.widgetlock(self)
        self._update_buttons_checked()
    def LR(self):
        if not self.canvas.widgetlock.available(self):
            self.set_message("Mission selection unavailable")
            return
        if self.mode == Mode.LR:
            self.mode = Mode.NONE
            self.canvas.widgetlock.release(self)
        else:
            self.mode = Mode.LR
            self.canvas.widgetlock(self)
        self._update_buttons_checked()
    def XY(self):
        if not self.canvas.widgetlock.available(self):
            self.set_message("Mission selection unavailable")
            return
        if self.mode == Mode.XY:
            self.mode = Mode.NONE
            self.canvas.widgetlock.release(self)
        else:
            self.mode = Mode.XY
            self.canvas.widgetlock(self)
        self._update_buttons_checked()
    def Snapshot(self):
        if not self.canvas.widgetlock.available(self):
            self.set_message("Snapshot selection unavailable")
            return
        if self.mode == Mode.QUICK:
            self.mode = Mode.NONE
            self.canvas.widgetlock.release(self)
        else:
            self.mode = Mode.QUICK
            self.canvas.widgetlock(self)
        self._update_buttons_checked()
    def ReferencePoints(self):
        if not self.canvas.widgetlock.available(self):
            self.set_message("Reference point selection unavailable")
            return
        if self.mode == Mode.REFERENCE:
            self.mode = Mode.NONE
            self.canvas.widgetlock.release(self)
        else:
            self.mode = Mode.REFERENCE
            self.canvas.widgetlock(self)
        self._update_buttons_checked()
    
    def MarkerSettings(self):
        self.mode = Mode.MARKER
        self._update_buttons_checked()
        if self.mode is not Mode.NONE:
            self.mode = Mode.NONE

class ToolbarContextWindow():
    def __init__(self,frame:ttk.Frame,toolBarIconPath,toolbar:CustomToolbar,MapUpdateFunction,*args):
        self.frame = frame
        self.toolBarIconPath = toolBarIconPath
        self.toolbar = toolbar
        self.frame.action = None

        self.customScale = StringVar(value="1.0")
        for stringVarName,stringVar in args[0]:
            setattr(self,stringVarName,stringVar)
        self.frame.marker = {}
        self.MapUpdate = MapUpdateFunction
        self.markerDefinitions = {"IDFP": Mark.IDFP,
                                  "Friendly": Mark.FRIENDLY,
                                  "FPF": Mark.FPF,
                                  "LR": Mark.LR,
                                  "XY": Mark.XY,
                                  "Group": Mark.FPF,
                                  "No fly": Mark.NOFLY,
                                  "Snapshot": Mark.SNAPSHOT
                                  }
        self.borderDefinitions = {"Friendly":Mark.FRIENDLY_BOUNDS,
                                  "FPF": Mark.FPF_BOUNDS,
                                  "LR": Mark.LR_BOUNDS,
                                  "XY": Mark.XY_BOUNDS,
                                  "Group": Mark.FPF_BOUNDS,
                                  "No Fly": Mark.NOFLY_BOUNDS,
                                  "Snapshot": Mark.SNAPSHOT
                                  }
    def FPF(self):################################ADD MARK BUTTON
        def MarkPressed():
            if self.frame.action:
                self.frame.action = False
                self.markButton.config(default="normal",text="Mark")
            else:
                self.frame.action = True
                self.markButton.config(default="active",text="Marking")
        self.frame.action = False
        self.frame.grid_rowconfigure((0,1,2),weight=0)
        self.frame.grid_columnconfigure(0,weight=1)
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.winfo_toplevel().geometry("425x270")
        self.frame.winfo_toplevel().anchor("nw")
        targetCreationFrame = ttk.Frame(self.frame)
        targetCreationFrame.grid_columnconfigure(0,weight=1)
        targetCreationFrame.grid_rowconfigure(0,weight=1)
        targetCreationItems = self.toolbar.UIMaster.targetCreation.Initialise(targetCreationFrame,mapWindow = True,targetType="FPF")
        targetCreationItems[5].config(command = lambda *args: self.toolbar.UIMaster.targetCreation.TargetAdd("FPF"))
        self.markButton = ttk.Button(targetCreationItems[1],text="Mark",command=lambda: MarkPressed())
        self.markButton.grid(column=4,row=3,sticky="NESW")
        targetDetailFrame = ttk.Frame(self.frame)
        targetDetailFrame.grid_columnconfigure(0,weight=1)
        targetDetailFrame.grid_rowconfigure(0,weight=1)
        targetDetailItems = self.toolbar.UIMaster.targetDetail.Initialise(targetDetailFrame,mapWindow = True,targetType="FPF")
        for mode, traceID in self.toolbar.UIMaster.targetDetail.fireMissionLength.trace_info():
            if traceID != targetDetailItems[0] and traceID != self.toolbar.UIMaster.targetDetail.lengthTrace:
                self.toolbar.UIMaster.targetDetail.fireMissionLength.trace_remove(mode,traceID)

        for mode, traceID in self.toolbar.UIMaster.targetDetail.fireMissionCondition.trace_info():
            if traceID != targetDetailItems[1] and traceID != self.toolbar.UIMaster.targetDetail.conditionTrace:
                self.toolbar.UIMaster.targetDetail.fireMissionCondition.trace_remove(mode,traceID)
        self.frame.grid(column=0,row=0,sticky="NEWS")
        targetCreationFrame.grid(column="0",row="0",sticky="NESW")
        targetDetailFrame.grid(column="0",row="1",sticky="NESW")
    def LR(self):
        def MarkPressed():
            if self.frame.action:
                self.frame.action = False
                self.markButton.config(default="normal",text="Mark")
            else:
                self.frame.action = True
                self.markButton.config(default="active",text="Marking")
        self.frame.action = False
        self.frame.grid_rowconfigure((0,1,2),weight=0)
        self.frame.grid_columnconfigure(0,weight=1)
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.winfo_toplevel().geometry("425x340")
        self.frame.winfo_toplevel().anchor("nw")
        targetCreationFrame = ttk.Frame(self.frame)
        targetCreationFrame.grid_columnconfigure(0,weight=1)
        targetCreationFrame.grid_rowconfigure(0,weight=1)
        targetCreationItems = self.toolbar.UIMaster.targetCreation.Initialise(targetCreationFrame,mapWindow = True,targetType="LR")
        targetCreationItems[5].config(command = lambda *args: self.toolbar.UIMaster.targetCreation.TargetAdd("LR"))
        self.markButton = ttk.Button(targetCreationItems[1],text="Mark",command=lambda: MarkPressed())
        self.markButton.grid(column=4,row=3,sticky="NESW")
        targetDetailFrame = ttk.Frame(self.frame)
        targetDetailFrame.grid_columnconfigure(0,weight=1)
        targetDetailFrame.grid_rowconfigure(0,weight=1)
        targetDetailItems = self.toolbar.UIMaster.targetDetail.Initialise(targetDetailFrame,mapWindow = True,targetType="LR")
        for mode, traceID in self.toolbar.UIMaster.targetDetail.fireMissionLength.trace_info():
            if traceID != targetDetailItems[0] and traceID != self.toolbar.UIMaster.targetDetail.lengthTrace:
                self.toolbar.UIMaster.targetDetail.fireMissionLength.trace_remove(mode,traceID)

        for mode, traceID in self.toolbar.UIMaster.targetDetail.fireMissionCondition.trace_info():
            if traceID != targetDetailItems[1] and traceID != self.toolbar.UIMaster.targetDetail.conditionTrace:
                self.toolbar.UIMaster.targetDetail.fireMissionCondition.trace_remove(mode,traceID)
        self.frame.grid(column=0,row=0,sticky="NEWS")
        targetCreationFrame.grid(column="0",row="0",sticky="NESW")
        targetDetailFrame.grid(column="0",row="1",sticky="NESW")
    def XY(self):
        def MarkPressed():
            if self.frame.action:
                self.frame.action = False
                self.markButton.config(default="normal",text="Mark")
            else:
                self.frame.action = True
                self.markButton.config(default="active",text="Marking")
        self.frame.action = False
        self.frame.grid_rowconfigure((0,1,2),weight=0)
        self.frame.grid_columnconfigure(0,weight=1)
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.winfo_toplevel().geometry("425x340")
        self.frame.winfo_toplevel().anchor("nw")
        targetCreationFrame = ttk.Frame(self.frame)
        targetCreationFrame.grid_columnconfigure(0,weight=1)
        targetCreationFrame.grid_rowconfigure(0,weight=1)
        targetCreationItems = self.toolbar.UIMaster.targetCreation.Initialise(targetCreationFrame,mapWindow = True,targetType="XY")
        targetCreationItems[5].config(command = lambda *args: self.toolbar.UIMaster.targetCreation.TargetAdd("XY"))
        self.markButton = ttk.Button(targetCreationItems[1],text="Mark",command=lambda: MarkPressed())
        self.markButton.grid(column=4,row=3,sticky="NESW")
        targetDetailFrame = ttk.Frame(self.frame)
        targetDetailFrame.grid_columnconfigure(0,weight=1)
        targetDetailFrame.grid_rowconfigure(0,weight=1)
        targetDetailItems = self.toolbar.UIMaster.targetDetail.Initialise(targetDetailFrame,mapWindow = True,targetType="XY")
        for mode, traceID in self.toolbar.UIMaster.targetDetail.fireMissionLength.trace_info():
            if traceID != targetDetailItems[0] and traceID != self.toolbar.UIMaster.targetDetail.lengthTrace:
                self.toolbar.UIMaster.targetDetail.fireMissionLength.trace_remove(mode,traceID)

        for mode, traceID in self.toolbar.UIMaster.targetDetail.fireMissionCondition.trace_info():
            if traceID != targetDetailItems[1] and traceID != self.toolbar.UIMaster.targetDetail.conditionTrace:
                self.toolbar.UIMaster.targetDetail.fireMissionCondition.trace_remove(mode,traceID)
        self.frame.grid(column=0,row=0,sticky="NEWS")
        targetCreationFrame.grid(column="0",row="0",sticky="NESW")
        targetDetailFrame.grid(column="0",row="1",sticky="NESW")
    def Snapshot(self):
        self.frame.action = False
        self.frame.grid_rowconfigure((2),weight=1)
        self.frame.grid_columnconfigure(0,weight=1)
        self.snapPosX = StringVar(value="00000")
        self.snapPosY =StringVar(value="00000")
        self.snapHeight = StringVar(value="0")
        self.airTemperature = StringVar(value=self.toolbar.UIMaster.atmospheric.airTemperature.get())
        self.airHumidity = StringVar(value=self.toolbar.UIMaster.atmospheric.airHumidity.get())
        self.airPressure = StringVar(value=self.toolbar.UIMaster.atmospheric.airPressure.get())
        self.windDirection = StringVar(value=self.toolbar.UIMaster.atmospheric.windDirection.get())
        self.windMagnitude = StringVar(value=self.toolbar.UIMaster.atmospheric.windMagnitude.get())
        self.windDynamic = StringVar(value=self.toolbar.UIMaster.atmospheric.windDynamic.get())
        self.fireMissionWidth = StringVar(value=self.toolbar.UIMaster.targetDetail.fireMissionWidth.get())
        self.fireMissionDepth = StringVar(value=self.toolbar.UIMaster.targetDetail.fireMissionDepth.get())
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.winfo_toplevel().geometry("300x720")
        self.frame.winfo_toplevel().anchor("nw")
        self.frame.winfo_toplevel().grid_columnconfigure(0,weight=1)
        self.frame.winfo_toplevel().grid_rowconfigure(0,weight=1)
        def MarkPressed():
            if self.frame.action:
                self.frame.action = False
                markButton.config(default="normal",text="Mark")
                
            else:
                self.frame.action = True
                markButton.config(default="active",text="Marking")
        def GridChanged(*args):
            self.frame.action = False
            markButton.config(default="normal",text="Mark")
            self.toolbar.UIMaster.HeightAutoFill(None,self.snapPosX.get(),self.snapPosY.get(),self.snapHeight,noEvent= True)

        self.snapPosX.trace_add(mode="write",callback=GridChanged)
        self.snapPosY.trace_add(mode="write",callback=GridChanged)

        def CalculatePressed():
            if len(snapshotIDFPCreation.idfpListbox.curselection()) != 0:
                try:
                    calculateButton.config(state="disabled")
                    IDFPDict = self.toolbar.UIMaster.castJson.Load(source=JsonSource.IDFP)
                    IDFP = list(IDFPDict.keys())[snapshotIDFPCreation.idfpListbox.curselection()[0]]
                    solution = self.toolbar.UIMaster.target.CalculateSnapshot(IDFPDict,IDFP,np.ceil(float(self.fireMissionWidth.get())), np.ceil(float(self.fireMissionDepth.get())),self.snapPosX.get(),self.snapPosY.get(),float(self.snapHeight.get()),float(self.airTemperature.get()),float(self.airHumidity.get()),float(self.airPressure.get()),float(self.windDirection.get()),float(self.windMagnitude.get()),int(self.windDynamic.get()))
                    try:
                        if int(np.round(float(self.fireMissionDepth))) >= 1:
                            range = "{:04d} ± {} m".format(int(solution["Range"]), int(np.round(float(self.fireMissionDepth))))
                    except:
                        range = "{:04d} m".format(int(solution["Range"]))
                    try:vertex = int(np.ceil(list(solution["Vertex"])[2]/5)*5)
                    except:vertex = solution["Vertex"]
                    if self.windDynamic.get() == "1":
                        windCorrections = "± {} mils\n± {} mils".format(int(np.round(float(solution["PerpendicularCorrection"]))),int(np.round(float(solution["ParallelCorrection"]))))
                    else:
                        windCorrections = "\n"
                    try:
                        if float(self.fireMissionWidth.get()) >=1:
                            azimuthDeviation = solution["Azimuth"]-solution["Left"] if (solution["Azimuth"]-solution["Left"]) > 0 else (solution["Azimuth"]-solution["Left"])+2*np.pi
                            azimuth = "{:06.1f} ± {} mils\n\t⇐ {:04d} | {:04d} ⇒".format(solution["Azimuth"]*3200/np.pi,np.round(azimuthDeviation*3200/np.pi),int(np.round(solution["Left"]*3200/np.pi)),int(np.round(solution["Right"]*3200/np.pi)))
                        else:
                            azimuth = "{:06.1f} mils\n".format(solution["Azimuth"]*3200/np.pi)
                    except:
                        azimuth = "{:06.1f} mils\n".format(solution["Azimuth"]*3200/np.pi)
                    try:
                        if float(self.fireMissionDepth.get()) >=1:
                            elevation = "{:06.1f} ± {} mils\n⇓ {:04d} | {:04d} ⇑".format(solution["Elevation"],int(np.round(solution["Near"])),int(np.round(solution["Far"])))
                        else:
                            elevation = "{:06.1f} mils\n".format(solution["Elevation"])
                    except:
                        elevation = "{:06.1f} mils\n".format(solution["Elevation"])
                        print("{}\n{}\n{}\n{}\n{:0.1f}\nFL {}\n{:0.1f}° {:0.1f} m/s\n{}\n{}\n{}".format(solution["System"],IDFPDict[IDFP]["Trajectory"],range,solution["Charge"],float(solution["TOF"]),vertex,solution["ImpactAngle"],solution["ImpactSpeed"],windCorrections,azimuth,elevation))
                    outputSolution.config(text="{}\n{}\n{}\n{}\n{:0.1f}\nFL {}\n{:0.1f}° {:0.1f} m/s\n{}\n{}\n{}".format(solution["System"],IDFPDict[IDFP]["Trajectory"],range,solution["Charge"],float(solution["TOF"]),vertex,solution["ImpactAngle"],solution["ImpactSpeed"],windCorrections,azimuth,elevation))
                except Exception as e: self.toolbar.UIMaster.StatusMessageErrorDump(e,errorMessage="Failed to calculate snapshot")
                finally:
                    calculateButton.config(state="normal")
                    self.frame.bell()
        inputLabelframe = ttk.LabelFrame(self.frame,text="Snapshot settings",padding=5)
        inputLabelframe.grid_columnconfigure((0),weight=1)
        outputLabelframe = ttk.LabelFrame(self.frame,text="Firing solution",padding=5)
        inputSeparator2 = ttk.Separator(inputLabelframe,orient="vertical")
        outputSeparator = ttk.Separator(outputLabelframe,orient="vertical")
        outputLabels = ttk.Label(outputLabelframe,text="System\nTrajectory\nRange\nCharge\nTOF\nVertex\nImpact\nCrosswind\nHead/Tailwind\nAzimuth\n\nElevation\n\n",justify="right",padding=3)
        outputSolution = ttk.Label(outputLabelframe,justify="left",padding=3)
        idfpLabelframe = ttk.Labelframe(inputLabelframe,text="IDFP")
        idfpLabelframe.columnconfigure(0,weight=1)
        snapshotIDFPCreation = IDFPCreation(self.toolbar.UIMaster)
        snapshotIDFPCreation.InitialiseIDFP(idfpLabelframe,True,self.toolbar.UIMaster.idfpCreation.idfpListBoxContents)
        
        airLabelframe = ttk.Labelframe(inputLabelframe,text="Air",padding=3)
        temperatureEntry = ttk.Entry(airLabelframe,width="5",textvariable=self.airTemperature,justify="right")
        degreeCLabel = ttk.Label(airLabelframe,text="°C",justify="left")
        humidityEntry = ttk.Entry(airLabelframe,width="5",textvariable=self.airHumidity,justify="right")
        percentLabel = ttk.Label(airLabelframe,text="%",justify="left")
        pressureEntry = ttk.Entry(airLabelframe,width="7",textvariable=self.airPressure,justify="right")
        hPaLabel = ttk.Label(airLabelframe,text="hPa",justify="left")
        windLabelframe = ttk.Labelframe(inputLabelframe,text="Wind",padding=3)
        directionEntry = ttk.Entry(windLabelframe,width="3",textvariable=self.windDirection,justify="right")
        degreeLabel = ttk.Label(windLabelframe,text="°",justify="left")
        magnitudeEntry = ttk.Entry(windLabelframe,width="5",textvariable=self.windMagnitude,justify="right")
        metrespersecLabel = ttk.Label(windLabelframe,text="m/s",justify="left")
        dynamicCheckBox = ttk.Checkbutton(windLabelframe,variable=self.windDynamic,onvalue=1,offvalue=0,padding=4)
        dynamicLabel = ttk.Label(windLabelframe,text="dynamic",justify="left")
        dispersionLabelframe = ttk.Labelframe(inputLabelframe,text="Wid | Dep",padding=3)
        widthLabel = ttk.Label(dispersionLabelframe,text="wid")
        widthCombobox = ttk.Combobox(dispersionLabelframe,textvariable=self.fireMissionWidth,justify="right",width=4,values=("0","10","20","40","50","100","150","200","250"))
        depthLabel = ttk.Label(dispersionLabelframe,text="dep")
        depthCombobox = ttk.Combobox(dispersionLabelframe,textvariable=self.fireMissionDepth,justify="right",width=4,values=("0","10","20","40","50","100","150","200","250"))
        positionLabelframe = ttk.Labelframe(inputLabelframe,text="Position",padding=3)
        positionLabelframe.grid_columnconfigure((1,2),weight=1)
        positionLabelframe.grid_rowconfigure((0,1),weight=1)
        gridLabel = ttk.Label(positionLabelframe,text="Grid")
        heightLabel = ttk.Label(positionLabelframe,text="Height")
        gridFrame = ttk.Frame(positionLabelframe)
        gridFrame.columnconfigure((0,1),weight=1)
        gridXLabel = ttk.Label(gridFrame,textvariable=self.snapPosX)
        gridYLabel = ttk.Label(gridFrame,textvariable=self.snapPosY)
        heightLabelValue = ttk.Entry(positionLabelframe,textvariable=self.snapHeight)
        actionFrame = ttk.Frame(self.frame,padding=3)
        actionFrame.grid_columnconfigure((0,1),weight=1)
        markButton = ttk.Button(actionFrame,text="Mark",command=MarkPressed)
        calculateButton = ttk.Button(actionFrame,text="Calculate",command=CalculatePressed)
        self.frame.grid(column=0,row=0,sticky="NEWS")
        inputLabelframe.grid(row="0",column="0",sticky="NEW")
        inputSeparator2.grid(row=5,column=1,rowspan=2,sticky="NS")
        idfpLabelframe.grid(row=0,column=0,sticky="NSEW")
        airLabelframe.grid(row=1,column=0,sticky="NEW")
        airLabelframe.grid_columnconfigure((0,2,4),weight=1)
        temperatureEntry.grid(row=0,column=0,sticky="NESW")
        degreeCLabel.grid(row=0,column=1,sticky="NESW")
        humidityEntry.grid(row=0,column=2,sticky="NESW")
        percentLabel.grid(row=0,column=3,sticky="NESW")
        pressureEntry.grid(row=0,column=4,sticky="NESW")
        hPaLabel.grid(row=0,column=5,sticky="NESW")
        directionEntry.grid(row=0,column=0,sticky="NESW")
        degreeLabel.grid(row=0,column=1,sticky="NSEW")
        magnitudeEntry.grid(row=0,column=2,sticky="NSEW")
        metrespersecLabel.grid(row=0,column=3,sticky="NESW")
        dynamicCheckBox.grid(row=0,column=4,sticky="NSEW")
        dynamicLabel.grid(row=0,column=5,sticky="NSEW")
        windLabelframe.grid(row=2,column=0,sticky="NEW")
        windLabelframe.grid_columnconfigure((0,2,5),weight=1)
        dispersionLabelframe.grid(row=3,column=0,sticky="NEW")
        dispersionLabelframe.grid_columnconfigure((1,3),weight=1)
        widthLabel.grid(row=0,column=0,sticky="NSEW")
        widthCombobox.grid(row=0,column=1,sticky="NSEW")
        depthLabel.grid(row=0,column=2,sticky="NSEW")
        depthCombobox.grid(row=0,column=3,sticky="NSEW")
        positionLabelframe.grid(row=4,column=0,sticky="NESW")
        gridLabel.grid(row=0,column=0,sticky="NSW")
        heightLabel.grid(row=1,column=0,sticky="NSW")
        gridFrame.grid(row=0,column=2,sticky="NESW",padx=5)
        gridXLabel.grid(row=0,column=0,sticky="NESW")
        gridYLabel.grid(row=0,column=1,sticky="NESW")
        heightLabelValue.grid(row=1,column=2,sticky="NESW",padx=5)
        actionFrame.grid(row=1,column=0,sticky="NEW")
        markButton.grid(row=0,column=0,sticky="NEW")
        calculateButton.grid(row=0,column=1,sticky="NEW")
        outputLabelframe.grid(row="2",column="0",sticky="NESW")
        outputLabels.grid(row=0,column=0,rowspan=12,sticky="NE")
        outputSolution.grid(row=0,column=2,rowspan=12,sticky="NW")
        outputSeparator.grid(row=0,column=1,rowspan=12,sticky="NS")
        
    def Reference(self):
        
        def ReferenceButtonPressed():
            self.frame.action = True
            if self.toolbar.mode is not Mode.REFERENCE:
                self.toolbar.mode = Mode.REFERENCE
                self.toolbar._update_buttons_checked()
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.winfo_toplevel().geometry("85x150")
        gridLabelframe = ttk.Labelframe(self.frame,text="Map Edge")
        image = Image.open(self.toolBarIconPath/"reference points.png")
        image = image.crop([4,4,44,44]).resize([12,12],Image.Resampling.BILINEAR)
        referenceImage = ImageTk.PhotoImage(image)
        mapEdgeSelect = ttk.Button(gridLabelframe,image=referenceImage,width=5,command=lambda: ReferenceButtonPressed())
        mapEdgeSelect.image = referenceImage
        mapEdgeCoef = ttk.Label(gridLabelframe,width=5,textvariable=self.customScale)
        try:
            coef = self.toolbar.mainWidget.settingsFile.Get("mapScaleCoef")
            if coef != {}:
                self.customScale.set(round(coef,3))
            else:
                None
        except:
            None
        self.frame.grid(column=0,row=0,sticky="NEWS")
        gridLabelframe.grid(column=0,row=0)
        mapEdgeSelect.grid(column=0,row=0)
        mapEdgeCoef.grid(column=1,row=0)
    def Marker(self):
        def SliderMoved(strvar,label,*args):
            label.set(str(round(float(label.get()))))
            strvar.set(int(label.get())/4)
        def SliderVisibility(name:str,visibleVar:StringVar,sizeVar:StringVar,slider:ttk.Scale,slideValue):
            if visibleVar.get() == "0":
                try:
                    slider.config(state="disabled")
                    try:
                        slideValue.trace_remove(mode="write",cbname=getattr(self,f"{name.replace(' ','')}SizeTrace"))
                    except: print("trace remove error: ", f"{name.replace(' ','')}SizeTrace")
                except:
                    for allTraces in visibleVar.trace_info():
                        mode,traceID = allTraces
                        if traceID != visibleVar.newTrace and traceID != visibleVar.changeTrace and traceID != visibleVar.saveTrace:
                            visibleVar.trace_remove(mode,traceID)
            else:
                try:
                    slider.config(state="normal")
                    sizeTrace = slideValue.trace_add(mode="write",callback=lambda *args: SliderMoved(sizeVar,slideValue))
                    setattr(self,f"{name.replace(' ','')}SizeTrace",sizeTrace)
                except:
                    for allTraces in visibleVar.trace_info():
                        mode,traceID = allTraces
                        if traceID != visibleVar.newTrace and traceID != visibleVar.changeTrace and traceID != visibleVar.saveTrace:
                            visibleVar.trace_remove(mode,traceID)
        def SliderSetup(name:str,visibleVar:StringVar|None,sizeVar:StringVar,row,declutter = False,declutterVar: StringVar | None = None):
            slideValue = StringVar(value=int(float(sizeVar.get())*4))
            if name != "Snapshot":
                if len(visibleVar.trace_info()) == 1:
                    changeTrace = visibleVar.trace_add("write",callback=lambda *args, n = name:self.MapUpdate(self.markerDefinitions[n]))
                    visibleVar.changeTrace = changeTrace
            # if slideValue.trace_info() == []:
            #     changeTrace = slideValue.trace_add("write",callback=lambda *args:self.MapUpdate(self.markerDefinitions[name]))
            markerSizeLabel = ttk.Label(markerLabelframe,text=name,justify="right")
            if visibleVar is not None:
                markerCheckbutton = ttk.Checkbutton(markerLabelframe,variable=visibleVar,offvalue="0",onvalue="1")
                newTrace = visibleVar.trace_add(mode="write",callback=lambda *args: SliderVisibility(name,visibleVar,sizeVar,markerSizeSlider,slideValue))
                visibleVar.newTrace = newTrace
            markerSizeSlider = ttk.Scale(markerLabelframe,variable=slideValue,orient="horizontal",from_=1,to=10,length="170")
            markerSizeEntry = ttk.Label(markerLabelframe,textvariable=slideValue,justify="left")
            if declutter:
                def Declutter():
                    if declutterVar.get() == "0":
                        declutterVar.set("1")
                        markerDeclutterLabel.config(background="lightgreen")
                        self.MapUpdate(self.markerDefinitions[name])
                    elif declutterVar.get() == "1":
                        declutterVar.set("0")
                        markerDeclutterLabel.config(background=normalDeclutterBackground)
                        self.MapUpdate(self.markerDefinitions[name])
                markerDeclutterLabel = ttk.Label(markerLabelframe,text="DCLTR",relief="groove",padding=3)
                normalDeclutterBackground = markerDeclutterLabel.cget("background")
                markerDeclutterLabel.bind("<Button-1>",lambda *args:Declutter())
                if declutterVar.get() == "1":
                    declutterVar.set("0")
                    Declutter()
                markerDeclutterLabel.grid(row=row,column=4,sticky="EW")
            sizeTrace = slideValue.trace_add(mode="write",callback=lambda *args: SliderMoved(sizeVar,slideValue))
            setattr(self,f"{name.replace(' ','')}SizeTrace",sizeTrace)
            markerSizeLabel.grid(row=row,column=0,sticky="NESW")
            if visibleVar is None:
                markerSizeSlider.grid(row=row,column=2,sticky="NESW")
                markerSizeEntry.grid(row=row,column=3,sticky="NESW")
            else:
                markerCheckbutton.grid(row=row,column=1,sticky="NESW")
                markerSizeSlider.grid(row=row,column=2,sticky="NESW")
                markerSizeEntry.grid(row=row,column=3,sticky="NESW")
                
        def BorderSetup(name:str,visibleVar:StringVar,sizeVar:StringVar,linestyleVar:StringVar,doubleLineStyleVar:StringVar,doubleLineSideVar:StringVar,row):
            slideValue = StringVar(value=int(float(sizeVar.get())*4))
            if visibleVar.trace_info() == []:
                changeTrace = visibleVar.trace_add("write",callback=lambda *args:self.MapUpdate(self.borderDefinitions[name]))
                visibleVar.changeTrace = changeTrace
            # if slideValue.trace_info() == []:
            #     slideValue.trace_add("write",callback=lambda *args:self.MapUpdate(self.borderDefinitions[name]))
            menu = Menu(self.toolbar.UIMaster.root,tearoff=False)
            def DropdownMenu(label:ttk.Label,menuType:Literal["linestyle","double"],stringVar,double = False):
                def SetLabels(value):
                    label.config(text=value)
                if menuType == "linestyle":
                    menu.delete(0,END)
                    if double:
                        menu.add_radiobutton(label="No",value="None",variable=stringVar,command=lambda *args:SetLabels("No"))
                        menu.add_radiobutton(label="Same",value="same",variable=stringVar,command=lambda *args:SetLabels("Same"))
                    menu.add_radiobutton(label="━━━━",value="solid",variable=stringVar,command=lambda *args:SetLabels("━━━━"))
                    menu.add_radiobutton(label="━  ━  ━",value="denseDash",variable=stringVar,command=lambda *args:SetLabels("━  ━  ━"))
                    menu.add_radiobutton(label="━   ━   ━",value="dashed",variable=stringVar,command=lambda *args:SetLabels("━   ━   ━"))
                    menu.add_radiobutton(label="━     ━",value="sparseDash",variable=stringVar,command=lambda *args:SetLabels("━     ━"))
                    menu.add_radiobutton(label="━         ━",value="sparsestDash",variable=stringVar,command=lambda *args:SetLabels("━         ━"))
                    menu.add_radiobutton(label="━ • ━ •",value="dashdot",variable=stringVar,command=lambda *args:SetLabels("━ • ━ •"))
                    menu.add_radiobutton(label="• • • • • •",value="dotted",variable=stringVar,command=lambda *args:SetLabels("• • • • • •"))
                    menu.add_radiobutton(label="•  •  •  •  •  •",value="sparseDot",variable=stringVar,command=lambda *args:SetLabels("•  •  •  •  •  •"))
                    menu.add_radiobutton(label="•    •    •    •",value="sparsestDot",variable=stringVar,command=lambda *args:SetLabels("•    •    •    •"))
                else:
                    menu.delete(0,END)
                    menu.add_radiobutton(label="Inside",value="inner",variable=stringVar,command=lambda *args:SetLabels("Inside"))
                    menu.add_radiobutton(label="Outside",value="outer",variable=stringVar,command=lambda *args:SetLabels("Outside"))
                menu.post(label.winfo_rootx(),label.winfo_rooty()+label.winfo_height())
            markerBorderLabelframe = ttk.Labelframe(borderLabelframe,text=name,padding=5)
            borderCheckbutton = ttk.Checkbutton(markerBorderLabelframe,variable=visibleVar,offvalue="0",onvalue="1")
            borderSizeLabel = ttk.Label(markerBorderLabelframe,text="Size",justify="left")
            borderSizeSlider = ttk.Scale(markerBorderLabelframe,variable=slideValue,orient="horizontal",from_=1,to=10,length="200")
            borderSizeEntry = ttk.Label(markerBorderLabelframe,textvariable=slideValue,justify="center")
            borderStyleFrame = ttk.Frame(markerBorderLabelframe)
            borderStyleFrame.columnconfigure((0,1,2,3,4),weight=1)
            borderStyleLabel = ttk.Label(borderStyleFrame,text="Style :",justify="right")
            borderStyleDynamicLabel = ttk.Label(borderStyleFrame,text="Style",relief="groove",justify="right",compound="right")
            borderStyleDynamicLabel.bind("<Button-1>",lambda event,label = borderStyleDynamicLabel: DropdownMenu(label,"linestyle",linestyleVar))
            borderStyleDynamicLabel.image = ImageTk.PhotoImage(Image.open(self.toolBarIconPath/"dropdown.png"))
            borderStyleDynamicLabel.config(image=borderStyleDynamicLabel.image)
            borderDoubleLabel = ttk.Label(borderStyleFrame,text="Doubled :",justify="center")
            borderDoubleStyleDynamicLabel = ttk.Label(borderStyleFrame,text="Style",justify="center",relief="groove",image=borderStyleDynamicLabel.image,compound="right")
            borderDoubleStyleDynamicLabel.bind("<Button-1>",lambda event, label = borderDoubleStyleDynamicLabel: DropdownMenu(label,"linestyle",doubleLineStyleVar,double=True))
            borderDoubleSideDynamicLabel = ttk.Label(borderStyleFrame,text="Side",justify="center",relief="groove",image=borderStyleDynamicLabel.image,compound="right")
            borderDoubleSideDynamicLabel.bind("<Button-1>",lambda event,label = borderDoubleSideDynamicLabel: DropdownMenu(label,"double",doubleLineSideVar))
            sizeTrace = slideValue.trace_add(mode="write",callback=lambda *args: SliderMoved(sizeVar,slideValue))
            newTrace = visibleVar.trace_add(mode="write",callback=lambda *args: SliderVisibility(name,visibleVar,sizeVar,borderSizeSlider,slideValue))
            visibleVar.newTrace = newTrace
            
            setattr(self,f"{name.replace(' ','')}SizeTrace",sizeTrace)
            
            markerBorderLabelframe.grid(row=row,column=0,sticky="NESW")
            borderCheckbutton.grid(row=0,column=0,sticky="NESW")
            borderSizeLabel.grid(row=0,column=1,sticky="NESW")
            borderSizeSlider.grid(row=0,column=2,sticky="NESW")
            borderSizeEntry.grid(row=0,column=3,sticky="NESW")
            borderStyleFrame.grid(row=1,column=0,columnspan=4,sticky="NESW")
            borderStyleLabel.grid(row=0,column=0,sticky="NESW")
            borderStyleDynamicLabel.grid(row=0,column=1,sticky="NES")
            borderDoubleLabel.grid(row=0,column=2,sticky="NESW")
            borderDoubleStyleDynamicLabel.grid(row=0,column=3,sticky="NES")
            borderDoubleSideDynamicLabel.grid(row=0,column=4,sticky="NES")
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.winfo_toplevel().geometry("320x810")
        markerLabelframe = ttk.Labelframe(self.frame,text="Markers")
        markerLabelframe.grid_rowconfigure((0,1,2,3,4,5,6,7),weight=1)
        self.frame.grid(column=0,row=0,sticky="NEWS")
        markerLabelframe.grid(row=0,column=0,sticky="NESW")
        SliderSetup("IDFP",self.visible_IDFP,self.size_IDFP,0,True,self.declutter_IDFP)
        SliderSetup("Friendly",self.visible_friendly,self.size_friendly,1,True,self.declutter_friendly)
        SliderSetup("FPF",self.visible_FPF,self.size_FPF,2)
        SliderSetup("LR",self.visible_LR,self.size_LR,3)
        SliderSetup("XY",self.visible_XY,self.size_XY,4)
        SliderSetup("Group",self.visible_Group,self.size_Group,5)
        SliderSetup("No fly",self.visible_nofly,self.size_nofly,6,True,self.declutter_nofly)
        SliderSetup("Snapshot",None,self.size_snapshot,7)

        borderLabelframe = ttk.Labelframe(self.frame,text="Borders",padding=5)
        borderLabelframe.grid_rowconfigure((0,1,2,3,4,5,6),weight=1)
        borderLabelframe.grid(row=1,column=0,sticky="NESW")
        row = 0
        for [name,mark] in [["Friendly","friendly"],["FPF","FPF"],["LR","LR"],["XY","XY"],["Group","Group"],["No Fly","nofly"],["Snapshot","snapshot"]]:
            BorderSetup(name,getattr(self,"visible_"+mark+"Bounds"),getattr(self,"size_"+mark+"Bounds"),getattr(self,"linestyle_"+mark+"Bounds"),getattr(self,"double_linestyle_"+mark+"Bounds"),getattr(self,"double_side_"+mark+"Bounds"),row)
            row += 1
            
        # BorderSetup("Friendly",self.visible_friendlyBounds,self.size_friendlyBounds,self.linestyle_friendlyBounds,self.double_linestyle_friendlyBounds,self.double_side_friendlyBounds,0)
        # BorderSetup("FPF",self.visible_FPFBounds,self.size_FPFBounds,self.linestyle_FPFBounds,self.double_linestyle_FPFBounds,self.double_side_FPFBounds,1)
        # BorderSetup("LR",self.visible_LRBounds,self.size_LRBounds,self.linestyle_LRBounds,self.double_linestyle_LRBounds,self.double_side_LRBounds,2)
        # BorderSetup("XY",self.visible_XYBounds,self.size_XYBounds,self.linestyle_XYBounds,self.double_linestyle_XYBounds,self.double_side_XYBounds,3)
        # BorderSetup("Group",self.visible_GroupBounds,self.size_GroupBounds,self.linestyle_GroupBounds,self.double_linestyle_GroupBounds,self.double_side_GroupBounds,4)
        # BorderSetup("No Fly",self.visible_noflyBounds,self.size_noflyBounds,self.linestyle_noflyBounds,self.double_linestyle_noflyBounds,self.double_side_noflyBounds,5)
        # BorderSetup("Snapshot",self.visible_snapshotBounds,self.size_snapshotBounds,self.linestyle_snapshotBounds,self.double_linestyle_snapshotBounds,self.double_side_snapshotBounds,6)