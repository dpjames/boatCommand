from random import random
from threading import Thread
from time import sleep
from gps import *
LOC = [0,0]
gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
def getLocation():
    return LOC.copy()

def gpsmain():
    global LOC
    while(True):
        report = gpsd.next() #
        if report['class'] == 'TPV':
            #print getattr(report,'lat',0.0),"\t",
            #print getattr(report,'lon',0.0),"\t",
            #print getattr(report,'time',''),"\t",
            #print getattr(report,'alt','nan'),"\t\t",
            #print getattr(report,'epv','nan'),"\t",
            #print getattr(report,'ept','nan'),"\t",
            #print getattr(report,'speed','nan'),"\t",
            #print getattr(report,'climb','nan'),"\t"
            lat = getattr(report,'lat',0.0)
            lon = getattr(report,'lon',0.0)
            LOC[0] = lon
            LOC[1] = lat
        sleep(.3)
def start():
    print("starting gps thread")
    t = Thread(target=gpsmain)
    t.start()
