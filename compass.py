from random import random
import berry
def getHeading():
    #print((-1 * berry.VALS["tchead"] + 90) % 360)
    return (berry.VALS["tchead"] + 90) % 360
    

