import sys
import time
import math
import IMU
import datetime
import os
import json
import collections
from threading import Thread


magXmin = 0
magYmin = 0
magZmin = 0
magXmax = 0
magYmax = 0
magZmax = 0

a = datetime.datetime.now()

IMU.detectIMU()     #Detect if BerryIMU is connected.
if(IMU.BerryIMUversion == 99):
    print(" No BerryIMU found... exiting ")
    sys.exit()
IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass

VALS = {
        "xv" : 0,
        "yv" : 0,
        "dx" : 0,
        "dy" : 0,
        "tchead" : 0,
        }

SAMPLES = 100
xacclist = collections.deque(maxlen=SAMPLES)
yacclist = collections.deque(maxlen=SAMPLES)
zacclist = collections.deque(maxlen=SAMPLES)

xmaglist = collections.deque(maxlen=SAMPLES)
ymaglist = collections.deque(maxlen=SAMPLES)
zmaglist = collections.deque(maxlen=SAMPLES)

def imumain():
    global VALS

    global a
    global b
    global magXmax
    global magXmin
    global magYmax
    global magYmin
    global magZmax
    global magZmin
    while(True):

        #Read the accelerometer,gyroscope and magnetometer values
        try:
            ACCx = -1 * IMU.readACCx()
            ACCy = -1 * IMU.readACCy()
            ACCz = -1 * IMU.readACCz()
            GYRx = IMU.readGYRx()
            GYRy = IMU.readGYRy()
            GYRz = IMU.readGYRz()
            MAGx = IMU.readMAGx()
            MAGy = IMU.readMAGy()
            MAGz = IMU.readMAGz()
        except:
            continue

        #update compass
        if MAGx > magXmax:
            magXmax = MAGx
        if MAGy > magYmax:
            magYmax = MAGy
        if MAGz > magZmax:
            magZmax = MAGz

        if MAGx < magXmin:
            magXmin = MAGx
        if MAGy < magYmin:
            magYmin = MAGy
        if MAGz < magZmin:
            magZmin = MAGz



        #Apply compass calibration
        MAGx -= (magXmin + magXmax) /2
        MAGy -= (magYmin + magYmax) /2
        MAGz -= (magZmin + magZmax) /2


        xacclist.append(ACCx)
        yacclist.append(ACCy)
        zacclist.append(ACCz)

        xmaglist.append(MAGx) 
        ymaglist.append(MAGy) 
        zmaglist.append(MAGz) 

        ACCx = sum(xacclist) / SAMPLES
        ACCy = sum(yacclist) / SAMPLES
        ACCz = sum(zacclist) / SAMPLES

        MAGx = sum(xmaglist) / SAMPLES
        MAGy = sum(ymaglist) / SAMPLES
        MAGz = sum(zmaglist) / SAMPLES

        ##Calculate loop Period(LP). How long between Gyro Reads
        b = datetime.datetime.now() - a
        a = datetime.datetime.now()
        LP = b.microseconds/(1000000*1.0)
        heading = 180 * math.atan2(MAGy,MAGx)/math.pi
        #Only have our heading between 0 and 360
        if heading < 0:
            heading += 360
        ####################################################################
        ###################Tilt compensated heading#########################
        ####################################################################
        #Normalize accelerometer raw values.
        accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
        accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
        #Calculate pitch and roll
        pitch = toFixed(math.asin(accXnorm), 100) #rotation about y
        roll = toFixed(-math.asin(accYnorm/math.cos(pitch)), 100) #rotation about x


        #Calculate the new tilt compensated values
        #The compass and accelerometer are orientated differently on the the BerryIMUv1, v2 and v3.
        #This needs to be taken into consideration when performing the calculations

        #X compensation
        if(IMU.BerryIMUversion == 1 or IMU.BerryIMUversion == 3):            #LSM9DS0 and (LSM6DSL & LIS2MDL)
            magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
        else:                                                                #LSM9DS1
            magXcomp = MAGx*math.cos(pitch)-MAGz*math.sin(pitch)

        #Y compensation
        if(IMU.BerryIMUversion == 1 or IMU.BerryIMUversion == 3):            #LSM9DS0 and (LSM6DSL & LIS2MDL)
            magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)
        else:                                                                #LSM9DS1
            magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)+MAGz*math.sin(roll)*math.cos(pitch)





        #Calculate tilt compensated heading
        tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/math.pi

        if tiltCompensatedHeading < 0:
            tiltCompensatedHeading += 360

        tiltCompensatedHeading-=13

        ##################### END Tilt Compensation ########################
        VALS["tchead"] = tiltCompensatedHeading

        G_X = toFixed(ACCx * .244 / 1000, 0)  
        G_Y = toFixed(ACCy * .244 / 1000, 0)  
        GRAV_X = toFixed(-1 * math.sin(pitch), 0)
        GRAV_Y = toFixed(math.cos(pitch)*math.sin(roll), 0)
        VALS["xacc"] = toFixed(GRAV_X + G_X, 0)  * 9.81 #convert into m/s^2
        VALS["yacc"] = toFixed(G_Y  + GRAV_Y, 0) * 9.81
        VALS["xv"] += toFixed(VALS["xacc"], 10) * LP 
        VALS["yv"] += VALS["yacc"] * LP 
        VALS["dx"] += toFixed(VALS["xv"], 0) * LP 
        VALS["dy"] += toFixed(VALS["yv"], 0) * LP 
        global count
        count+=1
        if(count % 50 == 0):
            ob = {
                #"pitch" : math.degrees(pitch),
                #"kx" : kalmanX,
                #"ky" : kalmanY + 180,
                #"pg" : toFixed(-1 * math.sin(pitch), 1000),
                #"kg" : toFixed(-1 * math.sin(math.radians(kalmanY - 180)), 1000),
                #"gx" : G_X,
                #"gx" : G_X,
                #"gravx" : GRAV_X,
                #"xa" : toFixed(VALS["xacc"], 10),
                #"xv" : toFixed(VALS["xv"], 1000),
                #"dx" : toFixed(VALS["dx"], 1000),
                "head" : (tiltCompensatedHeading)
            }
            #global mmax
            #global mmin
            #if(ob["xa"] > mmax):
            #    mmax = ob["xa"]
            #if(ob["xa"] < mmin):
            #    mmin = ob["xa"]
            #ob["min"] = mmin
            #ob["max"] = mmax
            print("\r", end=" ")
            print(json.dumps(ob), end=" ")
        if(count % 1000 == 0):
            VALS["xv"] = 0
            VALS["yv"] = 0
            VALS["dx"] = 0
            VALS["dy"] = 0
            #mmax = 0
            #mmin = 0
count = 0
mmax = -10
mmin = 10
def toFixed(v,n):
    if n == 0:
        return v
    return int(v * n) / float(n)

def start():
    print("starting imu thread")
    t = Thread(target=imumain)
    t.start()

if __name__ == "__main__":
    imumain()

