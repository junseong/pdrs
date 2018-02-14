#init
import matplotlib  # Graph
import math        # Square
from tkinter import *     # Visualization
from tkinter import ttk


# Config part
    # ODR
    # Sensitivity
    # Calibration data
    # Window size (changable)
        # gyro sensor -> 10
        # acce sensor -> 5
    # Smoothing factor
    


# Data collection module
    # Raw Data
        # Angle (3-axis)
        # Accel (3-axis)
        # Magnet (3-axis)
        # Temp
        # Pressure


# Motion segmentation module
    # Turn detection
        # Energy -> Moving average filter -> Threshold
    # Turn direction
        # Maximum abolute value : abs(gyro data) -> Moving average filter -> Take biggest value

    # Altitude change detection
        # Pressure -> LPF -> Avg(P(t))-Avg(P(t-1)) -> Threshold

    #


# Activity recognition module
    # Energy of Acceleration
        # High -> Activity
            # Walking
            # Stairs (Pressure change)
        # Low
            # Stationary
            # Eleavator (Pressure change + Magnetic fields)



# Activity specification module
    # Step detection & Counting
        # Step detection
            # Energy -> Moving average fileter -> Threshold 1 (Swing phase), Threshold 2 (Stance phase) : Symmetric value
        # Stair detection
            # Energy -> Low-pass filter - bias -> Peak detection



# Visualization module
    # Graph
        # matplotlib
            # Raw data -> Axis
            # Processed Data -> Energy & Step function (Threshold)
    # Map
        # POI Point Of Interest
        # Initial position + diff position -> per 10ms

# Functions

def SIGMA(data, start, end):
    result=0
    for i in range(start, end):
        result=result+data[i]
    return result

def MAF(data, window):
    result=[]
    for i in range(len(data)):
        if i<=window:
            result.append(SIGMA(data, i, i*2))
        if i>window and i+window<=len(data):
            result.append(SIGMA(data, i-window, i+window))
        else:
            result.append(SIGMA(data, i*2-len(data), len(data)))
    return result

def LPF():
    pass

def THRESHOLD():
    pass

class sensor: # Parent class -> x/y/z raw data, result, threshold result
    def __init__(self):
        self.x=[]
        self.y=[]
        self.z=[]
        self.result=[]  # Contain processed data (MAF, LPF)
        self.threshold=[] # Contain 0 or 1

    def get(self, source, position, offset):
        for i in range(len(source)):
            self.x.append(float(source[i][position])*offset)
            self.y.append(float(source[i][position+1])*offset)
            self.z.append(float(source[i][position+2])*offset)

class Gyro(sensor):
    def __init__(self):
        super().__init__()
        self.bias=6.9449755432434745 # Bias value
        self.config=8.75*0.001 # Config 250 dps

    def get(self, source):
        super().get(source, 0, self.config)

    def process(self):
        magnitude=[] # Magnitude of 3-axis gyro raw data
        for i in range(len(self.x)):
            magnitude.append(math.sqrt(self.x[i]**2+self.y[i]**2+self.z[i]**2))
        for i in range(len(self.x)):
            magnitude[i]=(magnitude[i]-self.bias)**2
        self.result=MAF(magnitude, 10)

class Acce(sensor):
    def __init__(self):
        super().__init__()
        self.bias=1.0405649575004565 # Bias value
        self.config=0.061*0.001 # Config 2 g

    def get(self, source):
        super().get(source, 3, self.config)

    def process(self):
        magnitude=[] # Magnitude of 3-axis acce raw data
        for i in range(len(self.x)):
            magnitude.append(math.sqrt(self.x[i]**2+self.y[i]**2+self.z[i]**2))
        for i in range(len(self.x)):
            magnitude[i]=(magnitude[i]-self.bias)**2
        self.result=MAF(magnitude, 10)

class Magn(sensor):
    def __init__(self):
        super().__init__()
        self.config=0.080*0.001 # Config 2 gauss
    
    def get(self, source):
        super().get(source, 6, self.config)

class Temp(sensor):
    def get(self, source):
        for i in range(len(source)):
            self.x.append(float(source[i][9]))

class Pres(sensor):
    def get(self, source):
        for i in range(len(source)):
            self.x.append(float(source[i][10]))

def dataReady(path):
    data=open(path, 'r')
    result=[]
    for readline in data.readlines():
        result.append(readline.split('/'))
    return result

if __name__=="__main__":
    # Initial routine
    source=dataReady("./data/test.txt")
    gyro=Gyro()
    gyro.get(source)
    acce=Acce()
    acce.get(source)
    magn=Magn()
    magn.get(source)
    temp=Temp()
    temp.get(source)
    pres=Pres()
    pres.get(source)
    # Process routine
    gyro.process()
    acce.process()
