import math
import matplotlib.pyplot as plt

class data:
    def __init__(self):
        self.gyro=[]
        self.acce=[]
        self.magn=[]
        self.temp=[]
        self.pres=[]
        self.gyroCalib=[]
        self.acceCalib=[]
        self.magnCalib=[]
        self.processedGyro=[] # MAF / LPF
        self.thresholdGyro=[]
        self.processedAcce=[] # MAF / LPF
        self.thresholdAcce=[]
        self.processedMagn=[] # MAF / LPF
        self.thresholdMagn=[]
        self.processedPres=[] # LPF
        self.processedTemp=[]
        self.count=0
        
    def getData(self, path):
        sd=open(path, 'r')
        count=0
        for readline in sd.readlines():
            line=readline.split('/')
            self.gyro.append(line[0:3])
            self.acce.append(line[3:6])
            self.magn.append(line[6:9])
            self.temp.append(float(line[9]))
            self.pres.append(float(line[10]))
            self.count=self.count+1
        for i in range(len(self.gyro)):
            for j in range(3):
                self.gyro[i][j]=float(self.gyro[i][j])*8.75*0.001
                self.acce[i][j]=float(self.acce[i][j])*0.061*0.001
                self.magn[i][j]=float(self.magn[i][j])*0.080*0.001

    def average(self, data, num):
        temp_x=[]
        temp_y=[]
        temp_z=[]
        temp=[]
        if data[0][0]: # 2차원 배열을 입력 받을 경우(각속도, 가속도, 자기)
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
        else: # 1차원 배열을 입력받을 경우 (기압, 온도)
            avg=0
            for i in range(num):
                avg=avg+data[i]
            avg=avg/num
            return avg

    def calibData(self):
        try:
            calibrationHandler=open('./data/CalibrationData.txt', 'r')
            calibs=calibrationHandler.readlines()
            self.gyroCalib=calibs[0].split('/')
            self.acceCalib=calibs[1].split('/')
            self.magnCalib=calibs[2].split('/')
            self.gyroBias=math.sqrt(float(self.gyroCalib[0])**2+float(self.gyroCalib[1])**2+float(self.gyroCalib[2])**2)
            self.acceBias=math.sqrt(float(self.acceCalib[0])**2+float(self.acceCalib[1])**2+float(self.acceCalib[2])**2)
            return 0
        except:
            print("No calibration data")
            calibrationHandler=open('CalibrationData.txt', 'w')
            gyro=self.average(self.gyro,50)
            acce=self.average(self.acce,50)
            magn=self.average(self.magn,50)
            calibrationHandler.write(str(gyro[0])+'/'+str(gyro[1])+'/'+str(gyro[2])+'\n')
            calibrationHandler.write(str(acce[0])+'/'+str(acce[1])+'/'+str(acce[2])+'\n')
            calibrationHandler.write(str(magn[0])+'/'+str(magn[1])+'/'+str(magn[2]))
            self.calibData(trashvalue)


    def dataEnergy(self, data, num):
        return math.sqrt(data[num][0]**2+data[num][1]**2+data[num][2]**2) # sqrt시에 부호 생각해 줘야 함 -> 2개의 threshold 를 사용하는 step detection 할 때 중요
            

    def MAF(self, data, calib, windowsize):
        processed=[]
        for i in range(self.count):
            sum=0
            if i<=windowsize:
                for j in range(0,i*2):
                    energy=math.sqrt(data[j][0]**2+data[j][1]**2+data[j][2]**2)
                    sum=sum+(energy-calib)**2
                movingavg=sum/(i*2+1)
                processed.append(movingavg)    
            elif i>windowsize and i+windowsize<=self.count:
                for j in range(i-windowsize, i+windowsize):
                    energy=math.sqrt(data[j][0]**2+data[j][1]**2+data[j][2]**2)
                    sum=sum+(energy-calib)**2
                movingavg=sum/(windowsize*2+1)
                processed.append(movingavg)
            else:
                for j in range(self.count-i*2,self.count):
                    energy=math.sqrt(data[j][0]**2+data[j][1]**2+data[j][2]**2)
                    sum=sum+(energy-calib)**2
                movingavg=sum/((self.count-i)*2+1)
                processed.append(movingavg)
        return processed

    def LPF(self, data, a):
        processed=[]
        processed.append(data[0])
        for i in range(1, self.count):
            processed.append(a*data[i-1]+data[i]*(1-a))
        return processed
    
    def threshold(self, data, value):
        result=[]
        temp=[]
        for i in range(self.count):
            if data[i]>value:
                temp=[data[i], int(1)]
            else:
                temp=[data[i], int(0)]
            result.append(temp)
        return result


    def process(self):
        #gyro sensor part
        self.processedGyro=self.MAF(self.gyro, self.gyroBias, 10)
        self.thresholdGyro=self.threshold(self.processedGyro, 2000) # Turn detection threshold 2500
            
        #acce sensor part
        self.processedAcce=self.MAF(self.acce, self.acceBias, 5) # 윈도우 값이 10 일 때 너무 smooth 해지는 결과가 있었음 (두 개의 문턱값 설정에 애로) 5정도로 낮추니 파악하기 용이 하였음
        self.LPFAcce=[]
        for i in range(self.count):
            self.LPFAcce.append((self.dataEnergy(self.acce, i)-self.acceBias)**2)

        self.LPFAcce=self.LPF(self.processedAcce, 0.9)
        #magn sensor part


        #temp sensor part
        

        #pres sensor part
        self.processedPres=self.LPF(self.pres, 0.9)

    def showRaw(self):
        count=[]
        for i in range(self.count):
            count.append(i*0.01)
        plt.figure(num = 'Raw Data /// Blue : x, Orange : y, Green : z', figsize = (9,6))
        #gyro 최대 값 +-250
        plt.subplot(321)
        plt.plot(count, self.gyro)
        plt.ylim(-250, 250)
        plt.xlabel('time')
        plt.ylabel('dps')
        #acce 최대 값 +- 2
        plt.subplot(322)
        plt.plot(count, self.acce)
        plt.ylim(-2, 2)
        plt.xlabel('time')
        plt.ylabel('g')
        #magn 최대 값 +- 2        
        plt.subplot(323)
        plt.plot(count, self.magn)
        plt.ylim(-2, 2)
        plt.xlabel('time')
        plt.ylabel('gauss')
        #temp
        plt.subplot(324)
        plt.plot(count, self.temp)
        plt.ylim(-10, 30)
        plt.xlabel('time')
        plt.ylabel('C')
        #pres
        plt.subplot(325)
        plt.plot(count, self.pres)
        plt.ylim(900, 1100)
        plt.xlabel('time')
        plt.ylabel('Hpa')
        #show
        plt.show()

    def showProcessd(self):
        count=[]
        for i in range(self.count):
            count.append(i*0.01)
        plt.figure(num = 'Processed Data /// Blue : x, Orange : y, Green : z', figsize = (9,6))
        #gyro 에너지값
        plt.subplot(221)
        plt.plot(count, self.processedGyro)
        plt.ylim(0, 50000)
        plt.xlabel('time')
        plt.ylabel('Gyro energy')
        #acce 최대 값 +- 2
        plt.subplot(222)
        plt.plot(count, self.processedAcce)
        plt.ylim(0, 1)
        plt.xlabel('time')
        plt.ylabel('MAF Acce')
        #magn 최대 값 +- 2        
        plt.subplot(223)
        plt.plot(count, self.thresholdGyro)
        plt.ylim(0, 2)
        plt.xlabel('time')
        plt.ylabel('gyro threshold')
        #pres
        plt.subplot(224)
        plt.plot(count, self.processedPres)
        plt.ylim(900, 1100)
        plt.xlabel('time')
        plt.ylabel('Hpa')
        #show
        plt.show()

if __name__=="__main__":
    test=data()
    test.getData("./data/test.txt")
    test.calibData()
    test.process()
    test.showRaw()
    test.showProcessd()