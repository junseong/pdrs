#init
import matplotlib.pyplot as plt  # Graph
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
    c=1/(2*window+1)
    for i in range(len(data)):
        if i<=window:
            result.append(c*SIGMA(data, 0, i*2))
        elif i>window and i+window<=len(data):
            result.append(c*SIGMA(data, i-window, i+window))
        else:
            result.append(c*SIGMA(data, len(data)-2*i, len(data)))
    return result

def LPF(data, i, a):
    if data[i-1]:
        return data[i]*(1-a)+data[i-1]*a
    else:
        return data[i]

def THRESHOLD(data, threshold):
    result=[]
    for i in range(len(data)):
        if data[i]>threshold:
            result.append(threshold)
        elif data[i]<threshold*(-1):
            result.append(threshold*(-1))
        else:
            result.append(0)
    return result

def dataReady(path):
    data=open(path, 'r')
    result=[]
    for readline in data.readlines():
        result.append(readline.split('/'))
    return result

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
        self.turncount=0

    def get(self, source):
        super().get(source, 0, self.config)

    def process(self):
        # Magnitude of 3-axis gyro raw data
        magnitude=[]
        for i in range(len(self.x)):
            magnitude.append(math.sqrt(self.x[i]**2+self.y[i]**2+self.z[i]**2))
        for i in range(len(self.x)):
            magnitude[i]=(magnitude[i]-self.bias)**2
        # Moving average filter (Window size = 10)
        self.result=MAF(magnitude, 10)
        # Threshold (Value = 5000)
        self.threshold=THRESHOLD(self.result, 5000)
        for i in range(len(self.threshold)):
            if self.threshold[i-1]:
                if self.threshold[i] is not self.threshold[i-1]:
                    self.turncount=self.turncount+1
            else:
                if self.threshold[i] is not 0:
                    self.turncount=self.turncount+1
        # Turn direction

class Acce(sensor):
    def __init__(self):
        super().__init__()
        self.bias=1.0405649575004565 # Bias value
        self.config=0.061*0.001 # Config 2 g
        self.stepcount=0

    def get(self, source):
        super().get(source, 3, self.config)
    
    def process(self): # +- magnitude
        # Magnitude of 3-axis acce raw data
        magnitude=[]
        for i in range(len(self.x)):
            if self.x[i]>0 and self.y[i]>0 and self.z[i]>0:
                magnitude.append(math.sqrt(self.x[i]**2+self.y[i]**2+self.z[i]**2))
            else:
                magnitude.append((-1)*math.sqrt(self.x[i]**2+self.y[i]**2+self.z[i]**2))
        for i in range(len(self.x)):
            if magnitude[i]>0:
                magnitude[i]=(magnitude[i]-self.bias)**2
            else:
                magnitude[i]=(-1)*(magnitude[i]+self.bias)**2
        # Moving average filter (Window size = 3)
        self.result=MAF(magnitude, 3)
        # Threshold (Value = 0.06)
        self.threshold=THRESHOLD(self.result, 0.02)
        for i in range(len(self.threshold)):
            if self.threshold[i-1]:
                if self.threshold[i]<self.threshold[i-1]:
                    self.stepcount=self.stepcount+1
    
    def process2(self):
        # Magnitude of 3-axis acce raw data
        magnitude=[]
        for i in range(len(self.x)):
            magnitude.append(math.sqrt(self.x[i]**2+self.y[i]**2+self.z[i]**2))
        for i in range(len(self.x)):
            magnitude[i]=(magnitude[i]-self.bias)**2
        # Moving average filter (Window size = 3)
        self.result=MAF(magnitude, 4)
        # Threshold (Value = 0.06)
        self.threshold=THRESHOLD(self.result, 0.06)
        for i in range(len(self.threshold)):
            if self.threshold[i-1]== 0 or self.threshold[i-1]==0.06:
                if self.threshold[i] is not self.threshold[i-1]:
                    self.stepcount=self.stepcount+1
            elif self.threshold[i] is not 0:
                self.stepcount=self.stepcount+1

    

class Magn(sensor):
    def __init__(self):
        super().__init__()
        self.config=0.080*0.001 # Config 2 gauss
    
    def get(self, source):
        super().get(source, 6, self.config)

    def process(self):
        for i in range(len(self.x)):
            self.result.append(math.sqrt(self.x[i]**2+self.y[i]**2+self.z[i]**2))
        


class Temp(sensor):
    def get(self, source):
        for i in range(len(source)):
            self.x.append(float(source[i][9]))

class Pres(sensor):
    def get(self, source):
        for i in range(len(source)):
            self.x.append(float(source[i][10]))
    def process(self):
        for i in range(len(self.x)):
            self.result.append(LPF(self.x, i, 0.9))

if __name__=="__main__":
    # Initial routine
    source=dataReady("./data/1.txt")
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
    acce.process2()
    magn.process()
    pres.process()

    print(gyro.turncount/2)
    print(acce.stepcount/2)


    # Show routine
    count=[]
    for i in range(len(gyro.x)):
        count.append(i*0.01) # 10 ms per sample

    plt.figure(num='Result', figsize=(12, 6))

    plt.subplot(221)
    plt.plot(count, gyro.result)
    plt.plot(count, gyro.threshold)
    plt.ylim(0, 50000)
    plt.xlabel('time')
    plt.ylabel('Gyro result')
    
    plt.subplot(222)
    #plt.plot(count, acce.x)
    #plt.plot(count, acce.y)
    #plt.plot(count, acce.z)
    plt.plot(count, acce.result)
    plt.plot(count, acce.threshold)
    #plt.ylim(-2,2)
    plt.ylim(0, 0.2)
    plt.xlabel('time')
    plt.ylabel('Acce result')

    plt.subplot(223)
    plt.plot(count, pres.x)
    plt.plot(count, pres.result)
    plt.ylim(1015, 1020)
    plt.xlabel('time')
    plt.ylabel('Pressure result')
    
    plt.subplot(224)
    plt.plot(count, magn.result)
    plt.ylim(0, 2)
    plt.xlabel('time')
    plt.ylabel('Magnetic result')

    plt.show()