import matplotlib.pyplot as plt

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


if __name__=="__main__":
    test=data()
    count=test.getData("E:/test.txt")
    print(test.gyro)