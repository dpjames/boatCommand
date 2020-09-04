from random import random
from threading import Thread
from time import sleep
import spotlock
import gpsd
LOC = [-120.472, 35.1941]
def getLocation():
    return LOC.copy()

def gpsmain():
    global LOC
    while(True):
        #pos = gpsd.get_current()
        #LOC[0] = pos.lon
        #LOC[1] = pos.lat
        LOC[0]+=.0001
        LOC[1]+=.0001
        sleep(.3)
def start():
    gpsd.connect()
    print("starting gps thread")
    t = Thread(target=gpsmain)
    t.start()
