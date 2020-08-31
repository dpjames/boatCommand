from random import random
from threading import Thread
from time import sleep
origin = [-120.472, 35.1941]  
LOC = origin.copy()
def getLocation():
    return LOC.copy()
#def gpsmain():
#    global LOC
#    deltas = [
#            [1,1],
#            [1,-1],
#            [-1,-1],
#            [-1,1],
#            [0,0]
#    ]
#    cur=0
#    while(True):
#        cur = ((cur+1) % len(deltas))
#        LOC[0]=origin[0]+(deltas[cur][0]/100.0)
#        LOC[1]=origin[1]+(deltas[cur][1]/100.0)
#        sleep(2)

def gpsmain():
    global LOC
    while(True):
        dy = random() * 2/1000.0  - 5/10000.0
        dx = random() * 2/1000.0  - 5/10000.0
        LOC[0]+=dx
        LOC[1]+=dy
        sleep(1)
def start():
    print("starting gps thread")
    t = Thread(target=gpsmain)
    t.start()
