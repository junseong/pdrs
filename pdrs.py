#init
import matplotlib.pyplot as plt  # Graph
from mpl_toolkits import mplot3d
import numpy
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

def counter(data):
    result=0
    if data[0]==0:
        for i in range(1, len(data)):
            if data[i] is not data[i-1]:
                result=result+1
        return result/2
    else:
        for i in range(1, len(data)):
            if data[i] is not data[i-1]:
                result=result+1
        return (result-1)/2

def data_ready(path):
    data=open(path, 'r')
    result=[]
    for readline in data.readlines():
        result.append(readline.split('/'))
    return result

# Sensor

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
        self.turncount=counter(self.threshold)
        # Turn direction
        # abs(), max()
        
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
        self.stepcount=counter(self.threshold)
    
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
        self.stepcount=counter(self.threshold)

class Magn(sensor):
    def __init__(self):
        super().__init__()
        self.config=0.080*0.001 # Config 2 gauss
    
    def get(self, source):
        super().get(source, 6, self.config)

    def process(self):
        for i in range(len(self.x)):
            self.result.append(math.sqrt(self.x[i]**2+self.y[i]**2+self.z[i]**2))
            self.threshold.append(0)

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
            self.threshold.append(0)

class Activity:
    def __init__(self):
        self.result=[]
        self.x=[0]
        self.x.append(0)
        self.y=[0]
        self.y.append(0)
        self.z=[0]
        self.z.append(0)

    def get(self, gyro, acce, magn, pres, count):
        for i in range(1, len(count)):
            if gyro[i] is not gyro[i-1]:
                self.result.append("T")
            if acce[i] is not acce[i-1]:
                self.result.append("W")

        turn=0 
        x=0
        y=0
        z=0
        for i in range(len(self.result)-1):
            if self.result[i] is "T" and self.result[i+1] is "T":
                turn=turn+1
            if self.result[i] is "W":
                if i is 0:
                    x=0.37*math.cos(math.pi*0.5*turn)
                    y=0.37*math.sin(math.pi*0.5*turn)
                    z=0
                    self.x.append(x)
                    self.y.append(y)
                    self.z.append(z)
                else:
                    x=x+0.37*math.cos(math.pi*0.5*turn)
                    y=y+0.37*math.sin(math.pi*0.5*turn)
                    z=z
                    self.x.append(x)
                    self.y.append(y)
                    self.z.append(z)

        print(len(self.x))
        print(len(self.y))
        print(len(self.z))
class pdrs_main:
    def __init__(self):
        # Declare
        self.gyro=Gyro()
        self.acce=Acce()
        self.magn=Magn()
        self.temp=Temp()
        self.pres=Pres()
        self.activity=Activity()
        # Default data path
        self.source=data_ready("./data/1.txt")

    def get(self):
        self.gyro.get(self.source)
        self.acce.get(self.source)
        self.magn.get(self.source)
        self.temp.get(self.source)
        self.pres.get(self.source)
        self.count=[]
        for i in range(len(self.gyro.x)):
            self.count.append(i*0.01)

    def process(self):
        self.gyro.process()
        self.acce.process2()
        self.magn.process()
        self.pres.process()
        print("gyro turn count")
        print(self.gyro.turncount)
        print("step count")
        print(self.acce.stepcount)
        self.activity.get(self.gyro.threshold, self.acce.threshold, self.magn.threshold, self.pres.threshold, self.count)

    def empty(self):
        self.gyro=Gyro()
        self.acce=Acce()
        self.magn=Magn()
        self.temp=Temp()
        self.pres=Pres()
        self.activity=Activity()
        self.count=[]

    def source_change(self):
        try:
            self.source=data_ready(self.str.get())
            print("Source changed")
            self.empty()
            self.get()
            self.process()
        except:
            print("Error")

    def show_raw_data(self):
        # Gyro
        plt.figure(num='Result', figsize=(12, 6))
        plt.subplot(321)
        plt.plot(self.count, self.gyro.x)
        plt.plot(self.count, self.gyro.y)
        plt.plot(self.count, self.gyro.z)
        plt.ylim(-250, 250)
        plt.xlabel('time')
        plt.ylabel('Gyro raw data')
        # Acce
        plt.subplot(322)
        plt.plot(self.count, self.acce.x)
        plt.plot(self.count, self.acce.y)
        plt.plot(self.count, self.acce.z)
        plt.ylim(-2, 2)
        plt.xlabel('time')
        plt.ylabel('Acceleration raw data')
        # Magn
        plt.subplot(323)
        plt.plot(self.count, self.magn.x)
        plt.plot(self.count, self.magn.y)
        plt.plot(self.count, self.magn.z)
        plt.ylim(-2, 2)
        plt.xlabel('time')
        plt.ylabel('Magnetic raw data')
        # Temp
        plt.subplot(324)
        plt.plot(self.count, self.temp.x)
        plt.ylim(-10, 30)
        plt.xlabel('time')
        plt.ylabel('Temperature raw data')
        # Pressure
        plt.subplot(325)
        plt.plot(self.count, self.pres.x)
        plt.ylim(900, 1100)
        plt.xlabel('time')
        plt.ylabel('pressure raw data')
        plt.show()

    def show_processed_data(self):
        # Gyro
        plt.figure(num='Result', figsize=(12, 6))
        plt.subplot(221)
        plt.plot(self.count, self.gyro.result)
        plt.plot(self.count, self.gyro.threshold)
        plt.ylim(0, 50000)
        plt.xlabel('time')
        plt.ylabel('Gyro processed data')
        # Acce
        plt.subplot(222)
        plt.plot(self.count, self.acce.result)
        plt.plot(self.count, self.acce.threshold)
        plt.ylim(0, 0.2)
        plt.xlabel('time')
        plt.ylabel('Acceleration processed data')
        # Magn
        plt.subplot(223)
        plt.plot(self.count, self.magn.result)
        plt.ylim(0, 2)
        plt.xlabel('time')
        plt.ylabel('Magnetic processed data')
        # Pressure
        plt.subplot(224)
        plt.plot(self.count, self.pres.result)
        plt.ylim(900, 1100)
        plt.xlabel('time')
        plt.ylabel('pressure processed data')
        plt.show()
    
    def show_map(self):
        plt.figure()
        ax=plt.axes(projection='3d')
        ax.scatter(self.activity.x, self.activity.y, self.activity.z)
        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')
        ax.set_zlabel('Z axis')
        plt.show()

    def main_frame(self):
        # Structure
        self.frame=Tk()
        self.frame.title("PDRS")
        self.frame.geometry("300x200")
        # Text input -> source
        self.str=StringVar()
        self.textbox=ttk.Entry(self.frame, width=20, textvariable=self.str)
        self.textbox.grid(row=0, column=0)
        # Buttons
        self.button_source_change=ttk.Button(self.frame, text="source change", command=self.source_change)
        self.button_source_change.grid(row=0, column=1)
        self.button_show_raw_data=ttk.Button(self.frame, text="Show raw data", command=self.show_raw_data)
        self.button_show_raw_data.grid(row=2, column=0)
        self.button_show_processed_data=ttk.Button(self.frame, text="Show processed data", command=self.show_processed_data)
        self.button_show_processed_data.grid(row=2, column=1)
        self.button_show_map=ttk.Button(self.frame, text="Show map", command=self.show_map)
        self.button_show_map.grid(row=3, column=0)
        self.frame.mainloop()

if __name__=="__main__":
    test=pdrs_main()
    test.get()
    test.process()
    test.main_frame()