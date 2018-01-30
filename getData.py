class data:
    def __init__(self):
        self.gyro=[]
        self.acce=[]
        self.magn=[]
        self.temp=[]
        self.pres=[]

    def getData(self, path):
        sd=open(path, 'r')
        for readline in sd.readlines():
            line=readline.split('/')
            self.gyro.append(line[0:3])
            self.acce.append(line[3:6])
            self.magn.append(line[6:9])
            self.temp.append(line[9])
            self.pres.append(line[10])
    
    def config(self):
        for i in range(len(self.gyro)):
            for j in range(3):
                self.gyro[i][j]=float(self.gyro[i][j])*8.75*0.001
        for i in range(len(self.acce)):
            for j in range(3):
                self.acce[i][j]=float(self.acce[i][j])*0.061*0.001
        for i in range(len(self.magn)):
            for j in range(3):
                self.magn[i][j]=float(self.magn[i][j])*0.080*0.001

    def average(self, data, num):
        temp_x=[]
        temp_y=[]
        temp_z=[]
        if data[0][0]: #입력된 리스트가 2차원 일 때(자이로, 가속도, 자기)
            avg_x=0
            avg_y=0
            avg_z=0
            for i in range(num):
                avg_x=avg_x+float(data[i][0])
                avg_y=avg_y+float(data[i][1])
                avg_z=avg_z+float(data[i][2])
            avg_x=avg_x/num
            avg_y=avg_y/num
            avg_z=avg_z/num
            return (avg_x, avg_y, avg_z)
        else:
            pass #error handler

    def calibData(self):
        self.gyroCalib=[]
        self.acceCalib=[]
        self.magnCalib=[]
        #getData("E:/test.txt")
        self.gyroCalib.append(self.average(self.gyro,50))
        self.acceCalib.append(self.average(self.acce,50))
        self.magnCalib.append(self.average(self.magn,50))
        print(self.gyroCalib)
        print(self.acceCalib)
        print(self.magnCalib)
       

    def process(self):
        pass


if __name__=="__main__":
    test=data()
    test.getData("E:/test.txt")
    print("센서에서 얻은 raw 데이터의 calibration")
    test.calibData()
    test.config()
    print("변환된 데이터의 calibration")
    test.calibData()