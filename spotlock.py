import gpsmodule
import compass
from gpiozero import Servo
import json
from threading import Thread
from time import sleep
from time import time
import math
import berry

SPOTLOCK_STATE = {
    "running" : False, 
    "lockedgps" : [0,0],
    "curgps" : [0,0],
    "deltas" : [0,0,0]
}

MOTOR_PIN = 14
MOTOR_MIN_PULSE = .0005
MOTOR_MAX_PULSE = .0025
MOTOR_FRAME = .003

MOTOR = Servo(MOTOR_PIN, min_pulse_width=MOTOR_MIN_PULSE, max_pulse_width=MOTOR_MAX_PULSE, frame_width=MOTOR_FRAME)

def getSpotlockData():
    return json.dumps(SPOTLOCK_STATE)

def controlSpotLock(state):
    global SPOTLOCK_STATE
    SPOTLOCK_STATE["running"] = bool(state)
    if(SPOTLOCK_STATE["running"]):
        loc = gpsmodule.getLocation()
        SPOTLOCK_STATE["lockedgps"] = loc.copy()
        SPOTLOCK_STATE["curgps"] = loc
        SPOTLOCK_STATE["deltas"] = [0,0,0]

def getAccelerations():
    #TODO read the sensors and apply a filter
    #return [random() - .5, random() - .5]
    return [berry.VALS.xacc, berry.VALS.yacc]

def updateDeltas(dt):
    acc = getAccelerations()
    dx = acc[0] * (dt ** 2)
    dy = acc[0] * (dt ** 2)
    SPOTLOCK_STATE["deltas"][0]+=dx
    SPOTLOCK_STATE["deltas"][1]+=dy
    SPOTLOCK_STATE["deltas"][0] = SPOTLOCK_STATE["curgps"][0] - SPOTLOCK_STATE["lockedgps"][0]
    SPOTLOCK_STATE["deltas"][1] = SPOTLOCK_STATE["curgps"][1] - SPOTLOCK_STATE["lockedgps"][1]
def updateHeading():
    vec = list(map(lambda v : (-1 * v), SPOTLOCK_STATE["deltas"]))
    mag = math.sqrt(vec[0]**2 + vec[1]**2)
    theta = math.degrees(math.atan2(vec[1],vec[0]))
    SPOTLOCK_STATE["heading"] = [mag, theta]

def updateMotor():
    compass_heading = compass.getHeading()
    compx = math.cos(math.radians(compass_heading))
    compy = math.sin(math.radians(compass_heading))
    our_heading = SPOTLOCK_STATE["heading"][1]
    ourx = math.cos(math.radians(our_heading))
    oury = math.sin(math.radians(our_heading))
    dot = ourx * compx + oury * compy
    motor_dir = math.degrees(math.asin(dot))
    if(motor_dir > 0): #positive means they are pointing together, ie with the boat
        motor_dir = 180 - motor_dir
    else:
        motor_dir = motor_dir + 90
    if((ourx * compy) > (oury * compx)):
        #comp is clockwise of us
        motor_dir = abs(motor_dir)
    else:
        motor_dir = abs(motor_dir) * -1
    motor_dir = min(max(motor_dir, -90), 90)
    MOTOR.value = motor_dir / 90.0

def spotlockmain():
    global SPOTLOCK_STATE
    now = time()
    then = time()
    while(True):
        if(SPOTLOCK_STATE["running"]):
            now = time()
            dt = now - then
            then = now
            SPOTLOCK_STATE["curgps"] = gpsmodule.getLocation()
            updateDeltas(dt)
            updateHeading()
            updateMotor()
        sleep(1)
def start():
    print("starting spotlock thread")
    t = Thread(target=spotlockmain)
    t.start()

