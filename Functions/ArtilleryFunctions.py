#All the velocities of individual charges (m/s)
#Charge 0 -> 153.9
#Charge 1 -> 243
#Charge 2 -> 388.8
#Charge 3 -> 648
#Charge 4 -> 810
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
global g #gravit. accel. @ sea level
global deltaT #calc time interval
global accuracy

g=9.80665
deltaT = 0.00025
accuracy = 0.1

#Wx = 0#tailwind speed (-ve for headwind)
#Wz = 0#crosswind speed

class SystemInfo:
    """
    Class defining weapon system characteristics

    **SytemInfo**(*variables*):
            *systems* = "Sholef", "L16"
            *info* = "dragCoef", "crossArea", "mass", "charge"
    
    coefficients and constants are pulled from the inbuilt dictionary *"systemInfo"*

    the **get()** function is used for this purpose
    
        Drag coefficient : dimensionless coefficient
        Cross-sectional area : metres squared
        Mass : kilograms
        Charge : muzzle velocity in metres per second
    """
    def __init__(self, system, info = "all"):
        self.system = system
        self.info = info

    systemInfo = {
        "Sholef" : {
            "dragCoef" : 0.24442,
            "crossArea" : 1.886920e-2,
            "mass" : 47,
            "charge" : {
                "1" : 153.9,
                "2" : 243,
                "3" : 388.8,
                "4" : 648,
                "5" : 810
                }
        },
        "L16" :{
            "dragCoef" : 0.133,
            "crossArea": 5.152997e-3,
            "mass" : 4.2,
            "charge" : {
                "0":70,
                "1":140,
                "2":200,
                "3":230,
                "4":255,
                "5":280,
                "6":305
                }
        },
        "L119" :{
            "dragCoef" :0.246,#0.2455 #0.2485
            "crossArea" : 8.65901475e-3,
            "mass" :13,#13
            "charge" : {
                "1" :100,
                "2" :165,
                "3" :225,
                "4" :280,
                "5" :330,
                "6" :370,
                "7" :440
            }
        },
        "M6" :{
            "dragCoef" : 0.088,
            "crossArea" : 2.82743338e-3,
            "mass" : 1.56,
            "charge" : {
                "0" : 88.74,
                "1" : 110.16,
                "2" : 130.05,
                "3" : 153
            }
        }
    }
    def get(self,charge="0"):
        """
        Retrieve contants/coefficients using this function.

        If class *info* specifies "charge" then the **get(*charge*)** must be given.

            if charge is not specified, it's assumed "0"

            if charge is specified then *charge* = "0","1","2",...

            return self.systemInfo[self.system]["charge"][charge]
        """
        if self.info == "all":
            return self.systemInfo[self.system]
        if self.info == "charge":
            return self.systemInfo[self.system]["charge"][str(charge)]
        else:
            return self.systemInfo[self.system][self.info]

def AirDensityRatio(height,Rho):
    return Rho*np.exp(-height/8400)


def delta(deltaT,Vx,Vy,Vz,x,y,z,t,Rho,Wx,Wz,m,Cd,A): #return the changed variables(acceleration of coords,velcity of coords, coords and the time) over time detlaT
    Vx = Vx - Wx*1.4
    Vz = Vz - Wz*1.4
    ay = -g-((Cd*Rho*A)/(2*m))*np.sin(np.arctan(Vy/Vx))*np.cos(np.arctan(Vz/np.sqrt(Vx*Vx+Vy*Vy)))*(Vx*Vx+Vy*Vy+Vz*Vz)
    ax = (Rho/m)*(-((Cd*A)/2)*np.cos(np.arctan(Vy/Vx))*np.cos(np.arctan(Vz/np.sqrt(Vx*Vx+Vy*Vy)))*(Vx*Vx+Vy*Vy+Vz*Vz))
    az = (Rho/m)*-(((Cd*A)/2)*np.sin(np.arctan(Vz/np.sqrt(Vx*Vx+Vy*Vy)))*(Vx*Vx+Vy*Vy+Vz*Vz))
    Vx = Vx + Wx*1.4
    Vz = Vz + Wz*1.4
    Vx = Vx + ax * deltaT
    Vy = Vy + ay * deltaT
    Vz = Vz + az * deltaT
    x = x + Vx * deltaT
    y = y + Vy * deltaT
    z = z + Vz * deltaT
    t = t + deltaT
    return (ax,ay,az,Vx,Vy,Vz,x,y,z,t)

def Trajectory(velocity,elevation,Rho,Wx,Wz,targetH,artyHeight,fireAngle,mass,dragCoef,crossArea): #takes the  initial speed of the round out the tube, the elevation angle (mils), air density, (arma default:1.22498)
    #crosswind (m/s), tailwind (m/s), Height of target (+ve when target is above)
    Vx,Vy,Vz = velocity*np.cos(elevation*2*np.pi/6400),velocity*np.sin(elevation*2*np.pi/6400),0
    #print(Vx,Vy,Vz)
    x,y,z=0,artyHeight,0 #initial position
    t=0 #initial time
    dataSet = [] #empty list
    data = []
    if fireAngle == "High" or fireAngle == "Low":
        while (Vy>0 or y>targetH): #while round is still above the target...
            data = delta(deltaT,Vx,Vy,Vz,x,y,z,t,Rho,Wx,Wz,mass,dragCoef,crossArea) #calling a new step to be made
            dataSet.append(data) #appending the new line of data to the list
            Vx,Vy,Vz,x,y,z,t = data[3],data[4],data[5],data[6],data[7],data[8],data[9] #reasigning old variables to the new set
    elif fireAngle == "Direct":
        while (Vy>0 or y>targetH): #while round is below the target
            data = delta(deltaT,Vx,Vy,Vz,x,y,z,t,Rho,Wx,Wz,mass,dragCoef,crossArea) #calling a new step to be made
            dataSet.append(data) #appending the new line of data to the list
            Vx,Vy,Vz,x,y,z,t = data[3],data[4],data[5],data[6],data[7],data[8],data[9] #reasigning old variables to the new set
    dataSet = np.array(dataSet).T #transposed to make each row a new instance
    return(dataSet) #Returns all accelerations, velocites, positions and times the round has achieved

def AirDensity(humidity: float,temp:float,pressure:float):
    pV = (humidity * 0.61078 * np.exp(((17.27 * temp) / (temp + 237.3)))) * 10
    pD = pressure * 100 - pV
    return ((pD * 0.0289654 + pV * 0.018016) / (8.31446261815324 * (temp + 273.15)))

def SeaLevelAirDensity(Rho,RhoHeight): return Rho*np.exp(RhoHeight/8400)
#print(Trajectory(SystemInfo(system="L119",info="charge").get(charge=3),370,AirDensity(80.3,16.1,991),0,0,0,"Low",SystemInfo(system="L119",info="mass").get(),SystemInfo(system="L119",info="dragCoef").get(),SystemInfo(system="L119",info="crossArea").get())[6][-1])

def Pythag(artyX: str,artyY: str,tgtX: str,tgtY: str,grids = True,) -> float:
    if grids:
        def IntegeriseOrdinate(ordinate:str) -> int:
            if (len(ordinate) == 4): return int(ordinate)*10
            elif (len(ordinate) == 5): return int(ordinate)
        try:
            artyX = IntegeriseOrdinate(artyX)
            artyY = IntegeriseOrdinate(artyY)
            tgtX = IntegeriseOrdinate(tgtX)
            tgtY = IntegeriseOrdinate(tgtY)
        except:
            return "Error Handler: Incorrect Ordinate"
        return np.sqrt((int(artyX)-int(tgtX))*(int(artyX)-int(tgtX))+(int(artyY)-int(tgtY))*(int(artyY)-int(tgtY)))
    else:
        return np.sqrt(float(tgtX)*float(tgtX)+int(tgtY)*int(tgtY))

def Bearing(artyX: str,artyY: str, tgtX: str,tgtY: str, xFlip = False, yFlip = False) -> float:
    if (len(tgtX) == 4):
        tgtX = int(tgtX)*10
    elif len(tgtX) == 5:
        None
    else:
        return "Error Handler: Incorrect X ordinate"
    if (len(tgtY) == 4):
        tgtY = int(tgtY)*10
    elif len(tgtY) == 5:
        None
    else:
        return "Error Handler: Incorrect Y ordinate"
    if xFlip == True:
        artyX = -int(artyX)
        tgtX = -int(tgtX)
    if yFlip == True:
        artyY = -int(artyY)
        tgtY = -int(tgtY)
    tangent = np.arctan2((int(tgtY) - int(artyY)), (int(tgtX) - int(artyX)))
    if (tangent < 0):
        return (np.absolute(tangent) + np.pi / 2)
    elif (tangent <= np.pi / 2):
        return (np.pi / 2 - tangent)
    else:
        return (2 * np.pi - (tangent - np.pi / 2))

def AveragePoint(GridX: list,GridY:list)->list:
    totalX = 0
    for grid in GridX:
        if (len(grid) == 4):
            grid = int(grid)*10
        elif len(grid) == 5:
            grid = int(grid)
        else:
            return "Error Handler: Incorrect X ordinate"
        totalX += grid
    totalY = 0
    for grid in GridY:
        if (len(grid) == 4):
            grid = int(grid)*10
        elif len(grid) == 5:
            grid = int(grid)
        else:
            return "Error Handler: Incorrect Y ordinate"
        totalY += grid
    return (totalX/len(GridX),totalY/len(GridY))


def Wind(bearing, windDirection,windMagnitude):
    """
    Returns dictionary of "Tailwind" and "Crosswind"
    """
    tailwind = -(windMagnitude * np.cos(bearing - (windDirection * np.pi/180)))
    crosswind = windMagnitude * np.sin(bearing - (windDirection * np.pi/180)) 
    return {"Tailwind" : tailwind,"Crosswind":crosswind}


def Charge(system,FireAngle,distance) -> int:
    if system == "Sholef":
        if FireAngle == "High":
            if distance > 14000: return 5
            elif distance > 8400: return 4
            elif distance > 4300: return 3
            elif distance > 1950: return 2
            else: return 1
        elif FireAngle == "Low":
            if distance > 16000: return 5
            elif distance > 9150: return 4
            elif distance > 4525: return 3
            elif distance > 2000: return 2
            else: return 1
        else:
            if distance > 13000: return 5
            elif distance > 6450: return 4
            elif distance > 2950: return 3
            elif distance > 1275: return 2
            else: return 1
    if system == "L119":
        if FireAngle == "High":
            if distance > 6400: return 7
            elif distance > 5800: return 6
            elif distance > 4500: return 5
            elif distance > 3350: return 4
            elif distance > 2050: return 3
            elif distance > 850: return 2
            else: return 1
        elif FireAngle == "Low":
            if distance > 6200: return 7
            elif distance > 5300: return 6
            elif distance > 4100: return 5
            elif distance > 2950: return 4
            elif distance > 1750: return 3
            elif distance > 700: return 2
            else: return 1
        else:
            if distance > 5600: return 7
            elif distance > 4500: return 6
            elif distance > 3350: return 5
            elif distance > 2050: return 4
            elif distance > 860: return 3
            else: return 2
    if system == "L16":
        if distance > 4600: return 6
        elif distance > 4100: return 5
        elif distance > 3550: return 4
        elif distance > 2850: return 3
        elif distance > 1600: return 2
        elif distance > 450: return 1
        else: return 0
    if system == "M6":
        if distance > 1400: return 3
        elif distance > 1050: return 2
        elif distance > 700: return 1
        else: return 0

def GridPosition(artyX: str,artyY: str,adjacent: float,opposite:float,bearing: float, xFlip = False, yFlip = False,oppositeType = "triangle"):
    """
    Returns the grid positions reference (#####,#####) from an adjacent and opposite sides of
    a right-angled triange from a given bearing (radians) from a grid #####,#####
    """
    if oppositeType == "triangle":
        angle = bearing+np.arctan(opposite/adjacent)
        hypot = np.sqrt(adjacent*adjacent+opposite*opposite)
        if xFlip:
            gridX = int(artyX)-hypot*np.sin(angle)
        else:
            gridX = int(artyX)+hypot*np.sin(angle)
        if yFlip:
            gridY = int(artyY)-hypot*np.cos(angle)
        else:
            gridY = int(artyY)+hypot*np.cos(angle)
    elif oppositeType == "arc":
        angle = bearing+(opposite/adjacent)
        if xFlip:
            gridX = int(artyX)-adjacent*np.sin(angle)
        else:
            gridX = int(artyX)+adjacent*np.sin(angle)
        if yFlip:
            gridY = int(artyY)-adjacent*np.cos(angle)
        else:
            gridY = int(artyY)+adjacent*np.cos(angle)
    else:
        return AttributeError
    return("{:05}".format(int(np.round(gridX))),"{:05}".format(int(np.round(gridY))))

def PolynomialData(velocity: float,title: str,mass: float,dragCoef: float,crossArea:float,mortar = False,startingElev = 1599):
    currentFile = Path(__file__).resolve()
    baseDir = currentFile.parent
    stdDensity = 1.22498
    elevation = startingElev
    distance = 0
    table = []
    timeL = []
    heightInc = 0
    heightDec = 0
    maxHeight = 0
    TOF = 0
    aziDev=0
    head=0
    tail=0
    pressureInc=0
    pressureDec=0
    tempElev=0
    newTrajectory = []
    tempTraj = []
    highAngle = True
    lowAngle = True
    while (highAngle):
        newTrajectory = Trajectory(velocity,elevation,stdDensity,0,0,0,fireAngle="High",mass=mass,dragCoef=dragCoef,crossArea=crossArea)
        distance = newTrajectory[6][-1]
        heightInc = Trajectory(velocity,elevation,stdDensity,0,0,100,fireAngle="High",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]
        heightDec = Trajectory(velocity,elevation,stdDensity,0,0,-100,fireAngle="High",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]
        maxHeight = max(newTrajectory[7])*3.281/100
        TOF = Trajectory(velocity,elevation,stdDensity,0,0,0,fireAngle="High",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[9][-1]
        head = Trajectory(velocity,elevation,stdDensity,-1,0,0,fireAngle="High",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]
        tail = Trajectory(velocity,elevation,stdDensity,1,0,0,fireAngle="High",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]
        pressureInc = Trajectory(velocity,elevation,stdDensity*1.01,0,0,0,fireAngle="High",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]
        pressureDec = Trajectory(velocity,elevation,stdDensity*0.99,0,0,0,fireAngle="High",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]
        table.append([distance,elevation,heightInc,heightDec,maxHeight,TOF,pressureInc,pressureDec])
        print([distance,elevation,heightInc,heightDec,maxHeight,TOF,pressureInc,pressureDec])
        if distance > Trajectory(velocity,elevation-1,stdDensity,0,0,0,fireAngle="High",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]:
            highAngle = False
        elevation -=1
    while (lowAngle) and mortar == False:
        newTrajectory = Trajectory(velocity,elevation,stdDensity,0,0,0,fireAngle="Low",mass=mass,dragCoef=dragCoef,crossArea=crossArea)
        distance = newTrajectory[6][-1]
        heightInc = Trajectory(velocity,elevation,stdDensity,0,0,100,fireAngle="Low",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]
        heightDec = Trajectory(velocity,elevation,stdDensity,0,0,-100,fireAngle="Low",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]
        maxHeight = max(newTrajectory[7])*3.281/100
        TOF = Trajectory(velocity,elevation,stdDensity,0,0,0,fireAngle="Low",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[9][-1]
        head = Trajectory(velocity,elevation,stdDensity,-1,0,0,fireAngle="Low",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]
        tail = Trajectory(velocity,elevation,stdDensity,1,0,0,fireAngle="Low",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]
        pressureInc = Trajectory(velocity,elevation,stdDensity*1.01,0,0,0,fireAngle="Low",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]
        pressureDec = Trajectory(velocity,elevation,stdDensity*0.99,0,0,0,fireAngle="Low",mass=mass,dragCoef=dragCoef,crossArea=crossArea)[6][-1]
        table.append([distance,elevation,heightInc,heightDec,maxHeight,TOF,pressureInc,pressureDec])
        print([distance,elevation,heightInc,heightDec,maxHeight,TOF,pressureInc,pressureDec])
        if elevation == 1:
            lowAngle = False
        elevation -=1
    table =np.array(table)
    np.savetxt(baseDir/"polynomial"/"raw"/(str(str(title)+".rawdat")),table, delimiter='\t')
    return table

def PolynomialGeneration(velocity:float,title:str,graphs = False):
    currentFile = Path(__file__).resolve()
    baseDir = currentFile.parent
    data = np.loadtxt(baseDir/"polynomial"/"raw"/(str(str(title)+".rawdat")),delimiter='\t')
    table = []
    distance = data.T[0]
    elevation = data.T[1]
    heightInc = data.T[2]
    heightDec = data.T[3]
    pressureInc = data.T[6]
    pressureDec = data.T[7]
    #ELEVATION (Distance to Elevation)
    polyElevHigh = np.polyfit(distance[:np.argmax(distance)],elevation[:np.argmax(distance)],10)
    polyElevLow = np.polyfit(distance[np.argmax(distance):],elevation[np.argmax(distance):],10)
    if graphs: ElevTables(distance,elevation,polyElevHigh,polyElevLow,title+" - Elevation/Distance","Elevation (mils)","Residuals - High angle","Residuals - Low angle","Distance (metres)")
    #HEIGHT DIFFERENCES (Elevation to change in distance[elevation then recalculated from difference])
    if graphs: HeightGraph(elevation,distance,heightInc,heightDec)
    polyHeightInc = np.polyfit(elevation[:np.argmax(distance-heightInc)],
                                (distance-heightInc)[:np.argmax(distance-heightInc)],
                                10)
    polyHeightDec = np.polyfit(elevation, (distance-heightDec), 10)
    if graphs: HeightGraphs(elevation[:np.argmax(distance-heightInc)],elevation,(distance-heightInc)[:np.argmax(distance-heightInc)],(distance-heightDec),polyHeightInc,polyHeightDec,title+" - Distance Differences per 100m of Height) for each Elevation","100m Height Difference distance (metres)","Residuals - Increase","Residual - Decrease","Elevation (mils)")
    #AIR DENSITY 1% CHANGE (Distance change per 1% difference at different distances)
    # plt.plot(distance[:np.argmax(distance)], (pressureInc-distance)[:np.argmax(distance)])
    # plt.plot(distance[np.argmax(distance):], (pressureInc-distance)[np.argmax(distance):])
    # plt.plot(distance[:np.argmax(distance)], (pressureDec-distance)[:np.argmax(distance)])
    # plt.plot(distance[np.argmax(distance):], (pressureDec-distance)[np.argmax(distance):])
    # plt.show()
    polyDensIncHigh = np.polyfit(distance[:np.argmax(distance)], (pressureInc-distance)[:np.argmax(distance)], 10)
    polyDensIncLow = np.polyfit(distance[np.argmax(distance):], (pressureInc-distance)[np.argmax(distance):], 10)
    polyDensDecHigh = np.polyfit(distance[:np.argmax(distance)], (pressureDec-distance)[:np.argmax(distance)], 10)
    polyDensDecLow = np.polyfit(distance[np.argmax(distance):], (pressureDec-distance)[np.argmax(distance):], 10)
    if graphs: DensityGraph(distance[:np.argmax(distance)],distance[np.argmax(distance):],(pressureInc-distance)[:np.argmax(distance)],(pressureInc-distance)[np.argmax(distance):],(pressureDec-distance)[:np.argmax(distance)],(pressureDec-distance)[np.argmax(distance):],polyDensIncHigh,polyDensIncLow,polyDensDecHigh,polyDensDecLow,title+" - Distance deviation for ")
    table.append([polyElevHigh,polyElevLow,polyHeightInc,polyHeightDec,polyDensIncHigh,polyDensIncLow,polyDensDecHigh,polyDensDecLow])
    np.savetxt(baseDir/"polynomial"/(str(str(title)+".dat")),np.transpose(table[0]),delimiter="\t",header="Elevation/Distance high angle\tElevation/Distance Low angle\tHeight difference above\tHeight difference below\tAir density increase high angle\tAir density increase low angle\tAir density decrease high angle\tAir density decrease low angle")

def ElevTables(x,y,polyHigh,polyLow,title,ylabel1,ylabel2,ylabel3,xlabel1):
    points = np.arange(x[0],np.max(x),1)
    
    fig = plt.figure(figsize=(19, 9))
    gs = fig.add_gridspec(3, hspace=0.01,height_ratios=[4, 1, 1])
    (ax1,ax2,ax3) = gs.subplots(sharex=True)
    for ax in fig.get_axes():
        ax.grid(which="major")
        ax.grid(which="minor",color='gainsboro')
        ax.minorticks_on()
    ax1.plot(x,y,'r-')
    ax1.plot(points,np.polyval(polyHigh,points),'b--',linewidth=0.9)
    ax1.axhline(y[np.argmax(x)],color = 'k',linewidth=1,linestyle="--")
    ax1.minorticks_on()
    ax1.set_ylabel(ylabel1,fontsize=15)
    ax2.set_ylabel(ylabel2,fontsize=7)
    ax3.set_ylabel(ylabel3,fontsize=7)
    ax3.set_xlabel(xlabel1)
    fig.suptitle(title)
    for i in x[:np.argmax(x)]:
        ax2.plot([i,i], [0,y[np.where(x==i)[0][0]]-np.polyval(polyHigh,i)],'b-')
    points = np.arange(x[-1],np.max(x),1)
    ax1.plot(points,np.polyval(polyLow,points),'g--',linewidth=0.9)
    for i in x[np.argmax(x):]:
        ax3.plot([i,i], [0,y[np.where(x==i)[0][0]]-np.polyval(polyLow,i)],'g-')
    mng = plt.get_current_fig_manager()
    mng.resize(1700,1000)
    plt.show()

def HeightGraph(elevation,distance,heightInc,heightDec):
    plt.figure(figsize=(19, 9))
    plt.plot(elevation[np.argmax(distance-heightInc)-1:],(distance-heightInc)[np.argmax(distance-heightInc)-1:],label="Impossible region, height<100m")
    plt.plot(elevation[:np.argmax(distance-heightInc)],(distance-heightInc)[:np.argmax(distance-heightInc)],label="Target 100m higher")
    plt.plot(elevation,distance-heightDec,label="Target 100m lower")
    plt.legend(loc=4)
    plt.minorticks_on()
    plt.grid(which="major")
    plt.grid(which="minor",color='gainsboro')
    plt.axhline(0,color ='k',linewidth=2)
    plt.xlabel("Elevation")
    plt.ylabel("Difference in horizontal distance per 100m of target elevation")
    plt.title("Difference in horizontal distance per 100m of target elevation for each elevation")
    plt.show()

def HeightGraphs(x1,x2,y1,y2,polyInc,polyDec,title,ylabel1,ylabel2,ylabel3,xlabel1):
    points1 = np.arange(x1[0],np.min(x1),-1)
    points2 = np.arange(x2[0],np.min(x2),-1)
    fig = plt.figure(figsize=(19, 9))
    gs = fig.add_gridspec(3, hspace=0.01,height_ratios=[4, 1, 1])
    (ax1,ax2,ax3) = gs.subplots(sharex=True)
    for ax in fig.get_axes():
        ax.grid(which="major")
        ax.grid(which="minor",color='gainsboro')
        ax.minorticks_on()
    ax1.plot(x1,y1,'r-')
    ax1.plot(points1,np.polyval(polyInc,points1),'b--',linewidth=0.9)
    ax1.plot(x2,y2,'r-')
    ax1.plot(points2,np.polyval(polyDec,points2),'b--',linewidth=0.9)
    ax1.axhline(0,color = 'k',linewidth=1,linestyle="--")
    ax1.minorticks_on()
    ax1.set_ylabel(ylabel1,fontsize=15)
    ax2.set_ylabel(ylabel2,fontsize=7)
    ax3.set_ylabel(ylabel3,fontsize=7)
    ax3.set_xlabel(xlabel1)
    fig.suptitle(title)
    for i in x1:
        ax2.plot([i,i], [0,y1[np.where(x1==i)[0][0]]-np.polyval(polyInc,i)],'g-')
    for i in x2:
        ax3.plot([i,i], [0,y2[np.where(x2==i)[0][0]]-np.polyval(polyDec,i)],'g-')
    mng = plt.get_current_fig_manager()
    mng.resize(1700,1000)
    plt.show()
    
def DensityGraph(x1,x2,y1,y2,y3,y4,polyIncHigh,polyIncLow,polyDecHigh,polyDecLow,title):#,labely,labely1,labely2,labely3,labely4,labelx
    points1 = np.arange(x1[0],np.max(x1),1)
    points2 = np.arange(np.max(x2),x2[-1],-1)
    plt.figure(figsize=(19, 9))
    plt.title(title + " - ")
    plt.plot(x1,y1)
    plt.plot(points1,np.polyval(polyIncHigh,points1),'b--',linewidth=0.9)
    plt.plot(x2,y2)
    plt.plot(points2,np.polyval(polyIncLow,points2),'g--',linewidth=0.9)
    plt.plot(x1,y3)
    plt.plot(points1,np.polyval(polyDecHigh,points1),'b--',linewidth=0.9)
    plt.plot(x2,y4)
    plt.plot(points2,np.polyval(polyDecLow,points2),'g--',linewidth=0.9)
    plt.show()
    fig = plt.figure(figsize=(19, 9))
    gs = fig.add_gridspec(4, hspace=0.01,height_ratios=[1, 1, 1, 1])
    (ax1,ax2,ax3,ax4) = gs.subplots(sharex=True)
    for ax in fig.get_axes():
        ax.grid(which="major")
        ax.grid(which="minor",color='gainsboro')
        ax.minorticks_on()
    fig.suptitle(title)
    for i in x1:
        ax1.plot([i,i], [0,y1[np.where(x1==i)[0][0]]-np.polyval(polyIncHigh,i)],'g-')
    for i in x2:
        ax2.plot([i,i], [0,y2[np.where(x2==i)[0][0]]-np.polyval(polyIncLow,i)],'g-')
    for i in x1:
        ax3.plot([i,i], [0,y3[np.where(x1==i)[0][0]]-np.polyval(polyDecHigh,i)],'g-')
    for i in x2:
        ax4.plot([i,i], [0,y4[np.where(x2==i)[0][0]]-np.polyval(polyDecLow,i)],'g-')
    mng = plt.get_current_fig_manager()
    mng.resize(1700,1000)
    plt.show()

def Prediction(baseDir,system,charge,fireAngle,distance, heightDifference,airDensity):
    if system =="Sholef":
        if charge == 1:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"155mm Charge 1 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 2:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"155mm Charge 2 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 3:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"155mm Charge 3 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 4:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"155mm Charge 4 - Polynomial coefficients.dat",delimiter="\t").T
        else:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"155mm Charge 5 - Polynomial coefficients.dat",delimiter="\t").T
    elif system =="L119":
        if charge == 1:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"105mm Charge 1 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 2:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"105mm Charge 2 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 3:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"105mm Charge 3 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 4:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"105mm Charge 4 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 5:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"105mm Charge 5 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 6:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"105mm Charge 6 - Polynomial coefficients.dat",delimiter="\t").T
        else:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"105mm Charge 7 - Polynomial coefficients.dat",delimiter="\t").T
    elif system =="L16":
        if charge == 0:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"81mm Charge 0 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 1:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"81mm Charge 1 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 2:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"81mm Charge 2 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 3:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"81mm Charge 3 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 4:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"81mm Charge 4 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 5:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"81mm Charge 5 - Polynomial coefficients.dat",delimiter="\t").T
        else:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"81mm Charge 6 - Polynomial coefficients.dat",delimiter="\t").T
    elif system =="M6":
        if charge == 0:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"60mm Charge 0 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 1:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"60mm Charge 1 - Polynomial coefficients.dat",delimiter="\t").T
        elif charge == 2:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"60mm Charge 2 - Polynomial coefficients.dat",delimiter="\t").T
        else:
            file = np.loadtxt(baseDir/"Functions"/"polynomial"/"60mm Charge 3 - Polynomial coefficients.dat",delimiter="\t").T
    if fireAngle == "Low" or fireAngle =="Flat":
        polyElev,polyDensDec,polyDensInc = file[1],file[5],file[7]
    else:
        polyElev,polyDensDec,polyDensInc = file[0],file[4],file[6]
    polyHeightInc,polyHeightDec = file[2],file[3]
    if airDensity > 1.22498:
        distanceDensityCorr = -np.polyval(polyDensInc,distance)*(1-airDensity/1.22498)*100
    else:
        distanceDensityCorr = np.polyval(polyDensDec,distance)*(1-airDensity/1.22498)*100
    if heightDifference > 0:
        heightCorrection = np.polyval(polyHeightInc,np.polyval(polyElev,distance+distanceDensityCorr))*heightDifference/100
    else:
        heightCorrection = -np.polyval(polyHeightDec,np.polyval(polyElev,distance+distanceDensityCorr))*heightDifference/100
    predElev = np.polyval(polyElev,distance+distanceDensityCorr+heightCorrection)
    return predElev

def Solution(baseDir,artyX: str,artyY: str,system: str,fireAngle:str,tgtX:str,tgtY:str,artyHeight=float(0),targetHeight=float(0),maxHeight = float(100),windDirection=float(0),windMagnitude=float(0),humidity = float(100),temperature = float(15),pressure = float(1013.25),charge=-1,xFlip = False,yFlip= False):
    """
    Define artillery and target positions, fire angle and system

    Returns:
    'Distance' : distance,
    'Elevation' : predictElev,
    'Azimuth' : Azimuth(),
    'Vertex' : Vertex(),
    'Charge' : charge,
    'TOF' : trajectory.T[-1][9],
    'System' : system,
    'FireAngle' : fireAngle,
    'WindDirection' : windDirection,
    'WindMagnitude' : windMagnitude,
    'Temperature' : temperature,
    'Pressure' : pressure,
    'Humidity: humidity
    'LowPositions' : collisionAvoidance

    """
    #Wind direction is the direction the wind is going to
    seaRho = SeaLevelAirDensity(AirDensity(humidity,temperature,pressure),artyHeight)
    airDensity = AirDensity(humidity=humidity,temp=temperature,pressure=pressure)
    print(Trajectory(SystemInfo(system="L119",info="charge").get(charge=3),337,airDensity,0,0,artyHeight,targetHeight,"Low",SystemInfo(system="L119",info="mass").get(),SystemInfo(system="L119",info="dragCoef").get(),SystemInfo(system="L119",info="crossArea").get())[6][-1])
    print(baseDir,artyX,artyY,system,fireAngle,tgtX,tgtY,artyHeight,targetHeight,maxHeight,windDirection,windMagnitude,humidity,temperature,pressure,charge,xFlip,yFlip)
    
    distance = Pythag(artyX,artyY,tgtX,tgtY)
    bearing = Bearing(artyX,artyY,tgtX,tgtY,xFlip, yFlip)
    if charge < 0:
        charge = Charge(system,fireAngle,distance)
    windDict=Wind(bearing,windDirection,windMagnitude)
    print(windDict)
    predictElev = Prediction(baseDir=baseDir,system=system,charge=charge,fireAngle=fireAngle,distance=distance,heightDifference=targetHeight-artyHeight,airDensity=airDensity)
    print(predictElev)
    if predictElev <-100 or predictElev > 1450:
        charge = Charge(system,fireAngle,distance)
        predictElev = Prediction(baseDir=baseDir,system=system,charge=charge,fireAngle=fireAngle,distance=distance,heightDifference=targetHeight-artyHeight,airDensity=airDensity)
    trajectory = Trajectory(velocity=SystemInfo(system=system,info="charge").get(charge),elevation=predictElev,Rho=airDensity,Wx=windDict["Tailwind"],Wz=windDict["Crosswind"],targetH=targetHeight,artyHeight=artyHeight,fireAngle=fireAngle,mass=SystemInfo(system=system,info="mass").get(),dragCoef=SystemInfo(system=system,info="dragCoef").get(),crossArea=SystemInfo(system=system,info="crossArea").get())
    try: deltaDistance = distance - trajectory.T[-1][6]
    except: return ValueError
    iterations = 0
    oldDistance = distance
    while abs(deltaDistance) > accuracy and iterations <20:
        predictElev = Prediction(baseDir=baseDir,system=system,charge=charge,fireAngle=fireAngle,distance=oldDistance+deltaDistance,heightDifference=targetHeight-artyHeight,airDensity=airDensity)
        print("range",predictElev,trajectory[6][-1])
        if predictElev <-100 or predictElev > 1450:
            charge = Charge(system,fireAngle,distance)
            predictElev = Prediction(baseDir=baseDir,system=system,charge=charge,fireAngle=fireAngle,distance=distance,heightDifference=targetHeight-artyHeight,airDensity=airDensity)
        trajectory = Trajectory(velocity=SystemInfo(system=system,info="charge").get(charge),elevation=predictElev,Rho=airDensity,Wx=windDict["Tailwind"],Wz=windDict["Crosswind"],targetH=targetHeight,artyHeight=artyHeight,fireAngle=fireAngle,mass=SystemInfo(system=system,info="mass").get(),dragCoef=SystemInfo(system=system,info="dragCoef").get(),crossArea=SystemInfo(system=system,info="crossArea").get())
        oldDistance += deltaDistance
        deltaDistance = distance-trajectory.T[-1][6]
        iterations +=1
    if abs(deltaDistance) >= accuracy and iterations == 20:
        
        return RecursionError
        #FALLBACK METHOD NEEDED
    collisionAvoidance = []
    projectileTime = 0
    for projectile in trajectory.T:
        if projectile[7] < maxHeight and projectileTime+0.02 < projectile[9] and projectile[9] < trajectory.T[9][-1]-0.01:
            collisionAvoidance.append((projectile[6],projectile[8],projectile[7]))
            projectileTime = projectile[9]

    def Azimuth():
        angle = np.arctan(trajectory.T[-1][8]/trajectory.T[-1][6])
        if bearing-angle < 0:           return (bearing-angle+2*np.pi)
        elif bearing-angle > 2*np.pi:   return (bearing-angle-2*np.pi)
        else:                           return (bearing-angle)
    def Vertex():
        vertex = trajectory.T[np.argmax(trajectory[7])]
        grid = GridPosition(artyX,artyY,vertex[6],vertex[8],bearing,xFlip,yFlip,oppositeType="triangle")
        return([grid[0],grid[1],vertex[7]*3.28084/100])
    solutionDict = {
        "Range" : distance,
        "Elevation" : predictElev,
        "Bearing" : bearing,
        "Azimuth" : Azimuth(),
        "Vertex" : Vertex()[2],
        "Charge" : charge,
        "TOF" : trajectory.T[-1][9],
        "System" : system,
        "FireAngle" : fireAngle,
        "WindDirection" : windDirection,
        "WindMagnitude" : windMagnitude,
        "Temperature" : temperature,
        "Pressure" : pressure,
        "Humidity": humidity,
        "LowPositions" : collisionAvoidance
        
    }
    return(solutionDict)
def Line(baseDir,orientation: float,deviation: float,artyX: str,artyY: str,system: str,fireAngle:str,tgtX:str,tgtY:str,artyHeight=float(0),targetHeight=float(0),maxHeight = float(100),windDirection=float(0),windMagnitude=float(0),humidity = float(100),temperature = float(15),pressure = float(1013.25),charge=-1,xFlip = False,yFlip= False, progressbar = None):
    if orientation == "Vertical":
        farPosition = GridPosition(artyX=artyX,artyY=artyY,adjacent=Pythag(artyX=artyX,artyY=artyY,tgtX=tgtX,tgtY=tgtY)+deviation,opposite=0,bearing=Bearing(artyX=artyX,artyY=artyY,tgtX=tgtX,tgtY=tgtY,xFlip=xFlip,yFlip=yFlip),xFlip=xFlip,yFlip=yFlip)
        farSolution = Solution(baseDir=baseDir,artyX=artyX,artyY=artyY,system="Sholef",fireAngle=fireAngle,tgtX=farPosition[0],tgtY=farPosition[1],artyHeight=artyHeight,targetHeight=targetHeight,maxHeight=maxHeight,windDirection=windDirection,windMagnitude=windMagnitude,humidity=humidity,temperature=temperature,pressure=pressure,charge=charge,xFlip=xFlip,yFlip=yFlip)
        try:progressbar["value"] = progressbar["value"] + 1
        except: None
        solution = Solution(baseDir=baseDir,artyX=artyX,artyY=artyY,system=system,fireAngle=fireAngle,tgtX=tgtX,tgtY=tgtY,artyHeight=artyHeight,targetHeight=targetHeight,maxHeight=maxHeight,windDirection=windDirection,windMagnitude=windMagnitude,humidity=humidity,temperature=temperature,pressure=pressure,charge=farSolution["Charge"],xFlip=xFlip,yFlip=yFlip)
        try:progressbar["value"] = progressbar["value"] + 1
        except: None
        nearPosition = GridPosition(artyX=artyX,artyY=artyY,adjacent=Pythag(artyX=artyX,artyY=artyY,tgtX=tgtX,tgtY=tgtY)-deviation,opposite=0,bearing=Bearing(artyX=artyX,artyY=artyY,tgtX=tgtX,tgtY=tgtY,xFlip=xFlip,yFlip=yFlip),xFlip=xFlip,yFlip=yFlip)
        nearSolution = Solution(baseDir=baseDir,artyX=artyX,artyY=artyY,system="Sholef",fireAngle=fireAngle,tgtX=nearPosition[0],tgtY=nearPosition[1],artyHeight=artyHeight,targetHeight=targetHeight,maxHeight=maxHeight,windDirection=windDirection,windMagnitude=windMagnitude,humidity=humidity,temperature=temperature,pressure=pressure,charge=farSolution["Charge"],xFlip=xFlip,yFlip=yFlip)
        solution["Orientation"] = orientation
        solution["Far"] = farSolution["Elevation"]
        solution["Near"] = nearSolution["Elevation"]
        solution["TOF"] = nearSolution["TOF"]
        solution["Vertex"] = (solution["Vertex"][0],solution["Vertex"][1],nearSolution["Vertex"][2])
        solution["DeviationLength"] = deviation
        return solution
    elif orientation == "Horizontal":
        solution = Solution(baseDir=baseDir,artyX=artyX,artyY=artyY,system=system,fireAngle=fireAngle,tgtX=tgtX,tgtY=tgtY,artyHeight=artyHeight,targetHeight=targetHeight,maxHeight=maxHeight,windDirection=windDirection,windMagnitude=windMagnitude,humidity=humidity,temperature=temperature,pressure=pressure,charge=charge,xFlip=xFlip,yFlip=yFlip)
        solution["Orientation"] = orientation
        solution["Left"] = solution["Azimuth"]-deviation/Pythag(artyX=artyX,artyY=artyY,tgtX=tgtX,tgtY=tgtY)
        solution["Right"] = solution["Azimuth"]+deviation/Pythag(artyX=artyX,artyY=artyY,tgtX=tgtX,tgtY=tgtY)
        if solution["Left"] < 0 :
            solution["Left"] += 2*np.pi
        if solution["Right"] > 2*np.pi:
            solution["Right"] -= 2*np.pi
        solution["DeviationWidth"] = deviation
        return solution
    else:
        return AttributeError
def Box(baseDir,deviationLength: float,deviationWidth: float,artyX: str,artyY: str,system: str,fireAngle:str,tgtX:str,tgtY:str,artyHeight=float(0),targetHeight=float(0),maxHeight = float(100),windDirection=float(0),windMagnitude=float(0),humidity = float(100),temperature = float(15),pressure = float(1013.25),charge=-1,xFlip = False,yFlip= False,progressbar = None):
    farPosition = GridPosition(artyX=artyX,artyY=artyY,adjacent=Pythag(artyX=artyX,artyY=artyY,tgtX=tgtX,tgtY=tgtY)+deviationLength,opposite=0,bearing=Bearing(artyX=artyX,artyY=artyY,tgtX=tgtX,tgtY=tgtY,xFlip=xFlip,yFlip=yFlip),xFlip=xFlip,yFlip=yFlip,oppositeType="arc")
    farSolution = Solution(baseDir=baseDir,artyX=artyX,artyY=artyY,system="Sholef",fireAngle=fireAngle,tgtX=farPosition[0],tgtY=farPosition[1],artyHeight=artyHeight,targetHeight=targetHeight,maxHeight=maxHeight,windDirection=windDirection,windMagnitude=windMagnitude,humidity=humidity,temperature=temperature,pressure=pressure,charge=charge,xFlip=xFlip,yFlip=yFlip)
    try:progressbar["value"] = progressbar["value"] + 1
    except: None
    solution = Solution(baseDir=baseDir,artyX=artyX,artyY=artyY,system=system,fireAngle=fireAngle,tgtX=tgtX,tgtY=tgtY,artyHeight=artyHeight,targetHeight=targetHeight,maxHeight=maxHeight,windDirection=windDirection,windMagnitude=windMagnitude,humidity=humidity,temperature=temperature,pressure=pressure,charge=farSolution["Charge"],xFlip=xFlip,yFlip=yFlip)
    try:progressbar["value"] = progressbar["value"] + 1
    except: None
    nearPosition = GridPosition(artyX=artyX,artyY=artyY,adjacent=Pythag(artyX=artyX,artyY=artyY,tgtX=tgtX,tgtY=tgtY)-deviationLength,opposite=0,bearing=Bearing(artyX=artyX,artyY=artyY,tgtX=tgtX,tgtY=tgtY,xFlip=xFlip,yFlip=yFlip),xFlip=xFlip,yFlip=yFlip,oppositeType="arc")
    nearSolution = Solution(baseDir=baseDir,artyX=artyX,artyY=artyY,system="Sholef",fireAngle=fireAngle,tgtX=nearPosition[0],tgtY=nearPosition[1],artyHeight=artyHeight,targetHeight=targetHeight,maxHeight=maxHeight,windDirection=windDirection,windMagnitude=windMagnitude,humidity=humidity,temperature=temperature,pressure=pressure,charge=farSolution["Charge"],xFlip=xFlip,yFlip=yFlip)
    solution["Far"] = farSolution["Elevation"]
    solution["Near"] = nearSolution["Elevation"]
    solution["Left"] = solution["Azimuth"]-deviationWidth/Pythag(artyX=artyX,artyY=artyY,tgtX=tgtX,tgtY=tgtY)
    solution["Right"] = solution["Azimuth"]+deviationWidth/Pythag(artyX=artyX,artyY=artyY,tgtX=tgtX,tgtY=tgtY)
    if solution["Left"] < 0 :
        solution["Left"] += 2*np.pi
    if solution["Right"] > 2*np.pi:
        solution["Right"] -= 2*np.pi
    solution["DeviationLength"] = deviationLength
    solution["DeviationWidth"] = deviationWidth
    solution["TOF"] = nearSolution["TOF"]
    solution["Vertex"] = (solution["Vertex"][0],solution["Vertex"][1],nearSolution["Vertex"][2])
    return solution

def LineMultiPoint(baseDir,artyX: str,artyY: str,system: str,fireAngle:str,tgtX:list,tgtY:list,tgtHeight,tgtName,explicit = False,series = False, seriesOrientation = None,spread = 20,artyHeight=float(0),maxHeight = float(100),windDirection=float(0),windMagnitude=float(0),humidity = float(100),temperature = float(15),pressure = float(1013.25),charge=-1,xFlip = False,yFlip= False,progressbar = None):
    lineSolution = {}
    if explicit == False:
        if charge == -1:
            furthest = 0
            for i in range(len(tgtX)):
                if Pythag(artyX,artyY,tgtX[i],tgtY[i]) > furthest:
                    furthest = Pythag(artyX,artyY,tgtX[i],tgtY[i])
            
            charge = Charge(system,fireAngle,furthest)
        for i in range(len(tgtX)):
            if i < len(tgtX)-1:
                distance = Pythag(artyX,artyY,tgtX[i],tgtY[i])
                averagePoint = AveragePoint([tgtX[i],tgtX[i+1]],[tgtY[i],tgtY[i+1]])
                averagePointDistance = Pythag(artyX,artyY,str(int(averagePoint[0])),str(int(averagePoint[1])))
                if abs((Bearing(artyX,artyY,tgtX[i],tgtY[i],xFlip,yFlip)-Bearing(artyX,artyY,str(int(averagePoint[0])),str(int(averagePoint[1])),xFlip,yFlip))*averagePointDistance)> abs(averagePointDistance-distance):
                    grid1 = GridPosition(artyX,artyY,averagePointDistance,0,bearing=Bearing(artyX,artyY,tgtX[i],tgtY[i],xFlip,yFlip))
                    grid2 = GridPosition(artyX,artyY,averagePointDistance,0,bearing=Bearing(artyX,artyY,tgtX[i+1],tgtY[i+1],xFlip,yFlip))
                    averageHeight = (tgtHeight[i]+tgtHeight[i+1])/2
                    grid1Solution = Solution(baseDir,artyX,artyY,system,fireAngle,grid1[0],grid1[1],artyHeight,averageHeight,maxHeight,windDirection,windMagnitude,humidity,temperature,pressure,charge,xFlip,yFlip)
                    try:progressbar["value"] = progressbar["value"] + 1
                    except: None
                    grid2Solution = Solution(baseDir,artyX,artyY,system,fireAngle,grid2[0],grid2[1],artyHeight,averageHeight,maxHeight,windDirection,windMagnitude,humidity,temperature,pressure,grid1Solution["Charge"],xFlip,yFlip)
                    lineSolution[tgtName[i]+","+tgtName[i+1]] = {
                        "Orientation" : "Horizontal",
                        "Distance" : averagePointDistance,
                        "Elevation" : np.round(((grid1Solution["Elevation"]+grid2Solution["Elevation"])/2)*10)/10,
                        "Azimuth1" : grid1Solution["Azimuth"],
                        "Azimuth2" : grid2Solution["Azimuth"],
                        "Vertex" : grid1Solution["Vertex"] if grid1Solution["Vertex"] > grid2Solution["Vertex"] else grid2Solution["Vertex"],
                        "Charge" : grid1Solution["Charge"],
                        "TOF" : grid1Solution["TOF"] if grid1Solution["TOF"] < grid2Solution["TOF"] else grid2Solution["TOF"],
                        "System" : grid1Solution["System"],
                        "FireAngle" : fireAngle,
                        "WindDirection" : windDirection,
                        "WindMagnitude" : windMagnitude,
                        "Temperature" : temperature,
                        "Pressure" : pressure,
                        "Humidity" : humidity
                        }
                else:
                    averageBearing = (Bearing(artyX,artyY,tgtX[i],tgtY[i],xFlip,yFlip)+Bearing(artyX,artyY,tgtX[i+1],tgtY[i+1],xFlip,yFlip))/2
                    print(averageBearing,Bearing(artyX,artyY,tgtX[i],tgtY[i],xFlip,yFlip),Bearing(artyX,artyY,tgtX[i+1],tgtY[i+1],xFlip,yFlip))
                    grid1 = GridPosition(artyX,artyY,Pythag(artyX,artyY,tgtX[i],tgtY[i]),0,averageBearing,xFlip,yFlip)
                    grid2 = GridPosition(artyX,artyY,Pythag(artyX,artyY,tgtX[i+1],tgtY[i+1]),0,averageBearing,xFlip,yFlip)
                    print(grid1,grid2)
                    averageHeight = (tgtHeight[i]+tgtHeight[i+1])/2
                    grid1Solution = Solution(baseDir,artyX,artyY,system,fireAngle,grid1[0],grid1[1],artyHeight,averageHeight,maxHeight,windDirection,windMagnitude,humidity,temperature,pressure,charge,xFlip,yFlip)
                    try:progressbar["value"] = progressbar["value"] + 1
                    except: None
                    grid2Solution = Solution(baseDir,artyX,artyY,system,fireAngle,grid2[0],grid2[1],artyHeight,averageHeight,maxHeight,windDirection,windMagnitude,humidity,temperature,pressure,grid1Solution["Charge"],xFlip,yFlip)
                    lineSolution[tgtName[i]+","+tgtName[i+1]] = {
                        "Orientation" : "Vertical",
                        "Distance" : averagePointDistance,
                        "Elevation1" : grid1Solution["Elevation"],
                        "Elevation2" : grid2Solution["Elevation"],
                        "Azimuth" : (grid1Solution["Azimuth"]+grid2Solution["Azimuth"])/2,
                        "Vertex" : grid1Solution["Vertex"] if grid1Solution["Vertex"] > grid2Solution["Vertex"] else grid2Solution["Vertex"],
                        "Charge" : grid1Solution["Charge"],
                        "TOF" : grid1Solution["TOF"] if grid1Solution["TOF"] < grid2Solution["TOF"] else grid2Solution["TOF"],
                        "System" : grid1Solution["System"],
                        "FireAngle" : fireAngle,
                        "WindDirection" : windDirection,
                        "WindMagnitude" : windMagnitude,
                        "Temperature" : temperature,
                        "Pressure" : pressure,
                        "Humidity" : humidity
                        }
        return lineSolution
    #print(Solution(artyX="06390",artyY="12444",tgtX="20571",tgtY="10704",system="Sholef",charge=3,fireAngle="High",windDirection=180,windMagnitude=2,targetHeight=20.2,artyHeight=207.8,temperature=27.9,humidity=33.2,pressure=986.9)["Elevation"])
#print(LineMultiPoint(artyX="11390",artyY="12444",tgtX=["16590","16590","16290"],tgtY=["12444","12644","12644"],explicit=False,system="Sholef",charge=-1,fireAngle="High",windDirection=180,windMagnitude=2,tgtHeight=[73,23,20.2],tgtName=["XY-00","XY-01","XY-02"],artyHeight=207.8,temperature=27.9,humidity=33.2,pressure=986.9))