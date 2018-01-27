import matplotlib.pyplot as plt

gyro_x=[]
gyro_y=[]
gyro_z=[]
accel_x=[]
accel_y=[]
accel_z=[]
magnet_x=[]
magnet_y=[]
magnet_z=[]
temperature=[]
pressure=[]

test=open("E:/test.txt", 'r')
lines=test.readlines()
for i in range(len(lines)):
    if i%8==1:
        gyro=lines[i].split(',')
        gyro_x.append(0.001*8.75*float(gyro[0]))
        gyro_y.append(0.001*8.75*float(gyro[1]))
        gyro_z.append(0.001*8.75*float(gyro[2]))
    if i%8==3:
        accel=lines[i].split(',')
        accel_x.append(0.001*0.061*float(accel[0]))
        accel_y.append(0.001*0.061*float(accel[1]))
        accel_z.append(0.001*0.061*float(accel[2]))
        magnet_x.append(0.001*0.080*float(accel[3]))
        magnet_y.append(0.001*0.080*float(accel[4]))
        magnet_z.append(0.001*0.080*float(accel[5]))
    if i%8==5:
        temperature.append(float(lines[i]))
    if i%8==7:
        pressure.append(float(lines[i]))

print(gyro_x)
print(gyro_y)
print(gyro_z)
print(accel_x)
print(accel_y)
print(accel_z)
print(magnet_x)
print(magnet_y)
print(magnet_z)
print(temperature)
print(pressure)

plt.figure(figsize=(9,6))
plt.subplot(321)
plt.plot(gyro_x, label='x')
plt.plot(gyro_y, label='y')
plt.plot(gyro_z, label='z')
plt.ylim(-250,250)
plt.title("Gyro")
plt.subplot(322)
plt.plot(accel_x, label='x')
plt.plot(accel_y, label='y')
plt.plot(accel_z, label='z')
plt.ylim(-2,2)
plt.title("Accel")
plt.subplot(323)
plt.plot(magnet_x, label='x')
plt.plot(magnet_y, label='y')
plt.plot(magnet_z, label='z')
plt.ylim(-2,2)
plt.title("Magnet")
plt.subplot(324)
plt.plot(temperature)
plt.title("Temperature")
plt.ylim(20, 25)
plt.subplot(325)
plt.plot(pressure)
plt.title("Pressure")
plt.ylim(1016,1020)
plt.show()