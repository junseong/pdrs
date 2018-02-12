#init
import matplotlib  #graph
import math        #square
from tkinter import *     #visualize
from tkinter import ttk


# Config part
    # ODR
    # Sensitivity
    # Calibration data
    # Window size
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

class sensor:
    def __init__(self):
        self.x=[]
        self.y=[]
        self.z=[]
        self.result=[]
        self.threshold=[]

class Gyro(sensor):
    def __init__(self):
        super().__init__()
        self.bias=6.9449755432434745
        self.config=8.75*0.001

class Acce(sensor):
    def __init__(self):
        super().__init__()
        self.bias=1.0405649575004565
        self.config=0.061*0.001

class Magn(sensor):
    pass

class Temp(sensor):
    pass

class Pres(sensor):
    pass





if __name__=="__main__":
    gyro=Gyro()
    acce=Acce()
    magn=Magn()
    temp=Temp()
    pres=Pres()