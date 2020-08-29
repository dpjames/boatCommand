from random import random
from threading import Thread
from time import sleep
cloc = [-120.472, 35.1941]  
def getLocation():
    return cloc.copy()
def gpsmain():
    DT = .2
    while(True):
        acc = random() * .0004 - .0002
        dx=(acc*DT*DT)
        acc = random() * .0004 - .0002
        dy=(acc*DT*DT)
        cloc[0]+=dx
        cloc[1]+=dy
        sleep(DT)
def start():
    print("starting gps thread")
    t = Thread(target=gpsmain)
    t.start()
