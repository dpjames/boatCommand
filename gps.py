from random import random
from threading import Thread
from time import sleep
cloc = [-120.472, 35.1941]  
def getLocation():
    return cloc.copy()
def gpsmain():
    DT = .5
    while(True):
        acc = random() * .0002 - .0001
        dx=(acc*DT*DT)
        acc = random() * .0002 - .0001
        dy=(acc*DT*DT)
        cloc[0]+=dx
        cloc[1]+=dy
        sleep(DT)
def start():
    print("starting gps thread")
    t = Thread(target=gpsmain)
    t.start()
