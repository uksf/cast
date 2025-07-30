#takistan 2000m high
import numpy as np
from Functions import cfg

#Number of IDFPs
IDFPs = 1
#10-figure grid
IDFP_1_Position = "1202417888"
IDFP_1_Altitude = 0

windDirection = 0
windMagnitude = 0

airTemperature =  15
airHumidity = 0
airPressure = 1013.25

cfg.artilleryPosition,cfg.artilleryAlt,cfg.windDir,cfg.windMag,cfg.pres,cfg.temp,cfg.humid = IDFP_1_Position,IDFP_1_Altitude,windDirection,windMagnitude,airPressure,airTemperature,airHumidity
from Functions import ArtilleryFunctions as af

# ("targetName", "targetPos", targetHeight) |
# [INTEGER](c)harge, (t)argetDisp,
# [STRING] "(e)ffect", "(l)ength", "(cond)ition", "(n)otes"
# [BOOLEAN] (h)igh angle,(v)ertex, (x)Flip, (y)Flip
# %Long hand priority%

#Charge 0 -> 153.9
#Charge 1 -> 243
#Charge 2 -> 388.8
#Charge 3 -> 648
#Charge 4 -> 810

#af.PolynomialGeneration(153.9,"155mm Charge 0")
af.Prediction("Sholef",0,float(1500),float(120),headWind=1,crossWind=2)
#print(mf.Pythag(artilleryPosition, "1378920095"))
# print(mf.BruteForceAdjust(2826,243,mf.airDensity,0,0,0,1270))
#print(af.PolynomialData(153.9,"Charge 0"))
#af.Prediction("0000000000",0,0,"high","0100001000",50,False,False)
# print(mf.airDensity)
# print(mf.BruteForceAdjust(7700,810,mf.airDensity,1,0,0,1383))

