import gps
import json
from random import random
from threading import Thread
from time import sleep
from time import time
import math
SPOTLOCK_STATE = {
    "running" : False, 
    "lockedgps" : [0,0],
    "curgps" : [0,0],
    "deltas" : [0,0,0]
}

def getSpotlockData():
    return json.dumps(SPOTLOCK_STATE)

def controlSpotLock(state):
    global SPOTLOCK_STATE
    SPOTLOCK_STATE["running"] = bool(state)
    if(SPOTLOCK_STATE["running"]):
        loc = gps.getLocation()
        SPOTLOCK_STATE["lockedgps"] = loc.copy()
        SPOTLOCK_STATE["curgps"] = loc
        SPOTLOCK_STATE["deltas"] = [0,0,0]

def getAccelerations():
    #TODO read the sensors and apply a filter
    return [random() - .5, random() - .5]

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

def spotlockmain():
    global SPOTLOCK_STATE
    now = time()
    then = time()
    while(True):
        if(SPOTLOCK_STATE["running"]):
            now = time()
            dt = now - then
            then = now
            SPOTLOCK_STATE["curgps"] = gps.getLocation()
            updateDeltas(dt)
            updateHeading()
            sleep(.01)
def start():
    print("starting spotlock thread")
    t = Thread(target=spotlockmain)
    t.start()
