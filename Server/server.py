import spidev
import wiringpi2
from StepperMotor import Stepper
import time
#import serial
import thread
from math import *
import TempSensor
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

x = Stepper(18,22)
y = Stepper(12,16)
z = Stepper(24,7)
e = Stepper(8,10)

wiringpi2.wiringPiSetupPhys()

spi = spidev.SpiDev()
spi.open(0,1)

heatpin=11
fanpin=5
wiringpi2.pinMode(heatpin, 1)
wiringpi2.pinMode(fanpin, 1)
wiringpi2.digitalWrite(fanpin, 0) #Fan off
TEMP=-1
#These values convert from steps to mm
xcalib=4*1000/200.0  #steps/mm
ycalib=4*1000/200.0  #steps/mm
zcalib=10000/100.0 #steps/mm
ecalib=4*10000/195.0  #steps/mm(pulled extrusion)
zadjust=0
temp=0
lineNum=0
totalLines=0
isHeating=False
isPrinting=False

#port = serial.Serial("/dev/ttyAMA0", baudrate=38400, timeout=3.0) #Open serial connection to ADC

# def GCD(a,b):#greatest common divisor
# 	while b:
# 	   a, b = b, a%b;
# 	return a;
# 
# def LCM(a,b):#least common multipler
# 	if a == 0:
# 		return b;
# 	if b == 0:
# 		return a;
# 	return a*b/GCD(a,b);

def sign(a): #return the sign of number a
	if a>0:
		return 1;
	elif a<0:
		return -1;
	else:
		return 0;


def Vertical_Motor_Step(stepper3, step3, speed):
	"""Much simpler this one is.  Just move it."""
	global pos
	dir3=-sign(step3)
	step3=abs(step3)
	for i in range(0, step3):
		stepper3.move(dir3,1000000.0/speed);
	#print pos
	return 0;

def Horizontal_Motor_Step(stepper1, step1, stepper2, step2, stepper3, step3, T):
#   TODO extrusion rate
#   control stepper motor 1 and 2 simultaneously
#   stepper1 and stepper2 are objects of StepperMotor class
#   direction is reflected in the polarity of [step1] or [step2]

	dir1=sign(step1);  #get dirction from the polarity of argument [step]
	dir2=sign(step2);
	dir3=-sign(step3); #direction backwards for stepper

	step1=int(abs(step1));
	step2=int(abs(step2));
	step3=int(abs(step3));

# [total_micro_step] total number of micro steps
# stepper motor 1 will move one step every [micro_step1] steps
# stepper motor 2 will move one step every [micro_step2] steps
# So [total_mirco_step]=[micro_step1]*[step1] if step1<>0;  [total_micro_step]=[micro_step2]*[step2] if step2<>0 
	if step1==0 and step2==0 and step3==0:
		return 0;
	else:
		total_micro_step=step1+step2+step3
		micro_step1=total_micro_step+5
		micro_step2=total_micro_step+5
		micro_step3=total_micro_step+5

		if step1!=0: micro_step1=total_micro_step/float(step1);
		if step2!=0: micro_step2=total_micro_step/float(step2);
		if step3!=0: micro_step3=total_micro_step/float(step3);
		
	dt=(T*1000000.0)/(step1+step2+step3) #Convert to us

	#xmoved, ymoved, emoved= 0, 0, 0
	# print 'Total iteration steps =',total_micro_step
	for i in range(0, total_micro_step):
		if (step1!=0 and i % micro_step1<1):#motor 1 need to turn one step
			stepper1.move(dir1,dt);
			#xmoved+=1
			
		if (step2!=0 and i % micro_step2<1):#motor 2 need to turn one step
			stepper2.move(dir2,dt);
			#ymoved+=1

		if (step3!=0 and i % micro_step3<1):
			stepper3.move(dir3,dt);
			#emoved+=1
	
	# print xmoved, ymoved, emoved
# 	print step1, step2, step3
	return 0;
	
def get_adc(channel):
	# Only 2 channels 0 and 1 else return -1
	if ((channel > 1) or (channel < 0)):
		return -1
	# Send start bit, sgl/diff, odd/sign, MSBF
	# channel = 0 sends 0000 0001 1000 0000 0000 0000
	# channel = 1 sends 0000 0001 1100 0000 0000 0000
	# sgl/diff = 1; odd/sign = channel; MSBF = 0
	r = spi.xfer2([1,(2+channel)<<6,0])
   
	# spi.xfer2 returns same number of 8 bit bytes
	# as sent. In this case, 3 - 8 bit bytes are returned
	# We must then parse out the correct 10 bit byte from
	# the 24 bits returned. The following line discards
	# all bits but the 10 data bits from the center of
	# the last 2 bytes: XXXX XXXX - XXXX DDDD - DDDD DDXX
	ret = ((r[1]&31) << 6) + (r[2] >> 2)
	return ret
	
	
def controlTemp():
	global temp
	global isHeating
	#Prints ADC Val to terminal
	while True:
		adc = get_adc(0)
		temp= TempSensor.getTemp(adc)
		if temp > 0 and temp < 240: #Are we getting reasonable numbers?
			if temp>TEMP:
				isHeating = False
				wiringpi2.digitalWrite(heatpin, 0)
			else:
				isHeating = True
				wiringpi2.digitalWrite(heatpin, 1)
		else:
			wiringpi2.digitalWrite(heatpin, 0)
			# print "Didn't receive response.  Killing heat."

		time.sleep(1)

def wait_for_temp():
	global isPrinting
	while temp < TEMP-1:
		print str(temp)+","+str(TEMP)
		if not isPrinting:
			break
		time.sleep(2)

def get_info():
	return [temp, lineNum, totalLines, isHeating]

def parse_line(line):
	global pos, f, absolute, TEMP, temp

	words=line.split()
	if len(words)==0:
		1; #Blank line
	elif words[0]=='G0':
		#Fast move, no extrude
		if absolute:
			dx,dy,dz=pos[0],pos[1],pos[2]
		else:
			dx,dy,dz=0,0,0

		for word in words:
			if word[0]=='X':
				dx=int(round(float(word[1:])*xcalib, 0))
			if word[0]=='Y':
				dy=int(round(float(word[1:])*ycalib, 0))
			if word[0]=='Z':
				dz=int(round(float(word[1:])*zcalib, 0))
		if absolute:
			dx-=pos[0]; dy-=pos[1]; dz-=pos[2];

		T=sqrt(dx**2+dy**2+dz**2)/1000
		pos[0]+=dx; pos[1]+=dy; pos[2]+=dz
		Horizontal_Motor_Step(x, dx, y, dy, e, 0, T)
		Vertical_Motor_Step(z, dz, 1000)

	elif words[0]=='G1':
		#Move while extruding

		if absolute:
			dx,dy,dz,de=pos[0],pos[1],pos[2],pos[3]
		else:
			dx,dy,dz,de=0 ,0 ,0 ,0
		
		T=0
		for word in words:
			if word[0]=='X':
				dx=int(round(float(word[1:])*xcalib, 0))
			if word[0]=='Y':
				dy=int(round(float(word[1:])*ycalib, 0))
			if word[0]=='Z':
				dz=int(round(float(word[1:])*zcalib, 0))
			if word[0]=='E':
				de=int(round(float(word[1:])*ecalib, 0))
			if word[0]=='F':
				f=float(word[1:])
		if absolute:
			dx-=pos[0]; dy-=pos[1]; dz-=pos[2]; de-=pos[3];

		T = sqrt((dx/xcalib)**2+(dy/ycalib)**2)/(f/60.0) #Time in sec
		#print T
		if T == 0 and de != 0:
			T = (abs(de)/ecalib)/(f/60.0)

		pos[0]+=dx; pos[1]+=dy; pos[2]+=dz; pos[3]+=de;
		Horizontal_Motor_Step(x, dx, y, dy, e, de, T)
		Vertical_Motor_Step(z, dz, 1000)

	elif words[0]=='G28':
		 parse_line('G0 X0 Y0 Z0')  #Move to origin, no extruding
	elif words[0]=='G21':
		1#Set to mm
	elif words[0]=='G90':
		absolute=True #Abs positioning
	elif words[0]=='G91':
		absolute=False #Rel. positioning
	elif words[0]=='G92':
		#Set current position/extrusion.	
		if len(words)==1:
			pos[0], pos[1], pos[2], pos[3] = 0.0, 0.0, 0.0, 0.0
		else:
			for word in words:
				if word[0]=='X':
					pos[0]=float(word[1:])
				if word[0]=='Y':
					pos[1]=float(word[1:])
				if word[0]=='Z':
					pos[2]=float(word[1:])
				if word[0]=='E':
					pos[3]=float(word[1:])

	### M's ###
	

	elif words[0]=='M106': #TODO: Add PWM
		wiringpi2.digitalWrite(fanpin, 1)
	elif words[0]=='M107':
		wiringpi2.digitalWrite(fanpin, 0)
	elif words[0]=='M109':
		#Temperature
		for word in words:
			if word[0]=='S':
				TEMP=int(word[1:])
				wait_for_temp()
				print "I'm at temperature!"
	elif words[0]=='M104':
		for word in words:
			if word[0]=='S':
				TEMP=int(word[1:])
				print "New temp of: "+str(TEMP)

	else:
		print "Unrecognized line: "+line


# def adjust():
# 	global zadjust
# 	while True:
# 		if zadjust==0:
# 			zadjust=int(raw_input("Enter Z adjustment: "))
# 		time.sleep(1)	

def actually_adjust():
	global zadjust
	if zadjust !=0:
		Vertical_Motor_Step(z, zadjust, 1000)
		#print 'I adjusted the z axis '+str(zadjust)+' steps!'
		zadjust = 0 

def x_step(xsteps, T):
	Horizontal_Motor_Step(x, xsteps, y, 0, e, 0, T)
	return True
	
def y_step(ysteps, T):
	Horizontal_Motor_Step(x, 0, y, ysteps, e, 0, T)
	return True
	
def z_step(zsteps):
	global zadjust
	if not isPrinting:
		Vertical_Motor_Step(z, zsteps, 1000)
	else:
		zadjust = zsteps
	return True
	
def e_step(esteps, T):
	Horizontal_Motor_Step(x, 0, y, 0, e, esteps, T)
	return True

def set_temp(temptoset):
	global TEMP
	TEMP = temptoset
	return True

def server_receive_file(filename, arg):
    with open("/home/pi/reprap/files/"+filename, "wb") as handle:
		handle.write(arg.data)
		return True

def remote_print(filename):
	thread.start_new_thread(print_file, ("/home/pi/reprap/files/"+filename,))
	return True

def stop_print():
	global isPrinting
	isPrinting = False
	return True

thread.start_new_thread(controlTemp, ())
pos=[0, 0, 0, 0] #Now in steps
f=1000
absolute=True
abs_z_steps=0
#while temp < TEMP:
#	time.sleep(1);

#hasGCode= raw_input("Have GCode? (y/n) ")
# if not args.file:
# #if hasGCode=="n":
# 	try:
# 		while True:
# 			xsteps = int(raw_input("X axis? "))
# 			ysteps = int(raw_input("Y axis? "))
# 			zsteps = int(raw_input("Z axis? "))
# 			esteps = -int(raw_input("Extrusion steps? ")) 
# 			speed  = int(raw_input("Speed? "))	
# 			
# 
# 			Horizontal_Motor_Step(x, xsteps, y, ysteps, e, esteps, speed)
# 			Vertical_Motor_Step(z, zsteps, speed)
# 	
# 	
# 			#motor = int(raw_input("Choose motor(1,2,3): "))
# 			#direction = int(raw_input("Input Direction: "))
# 			#steps = int(raw_input("Input Step Number: "))
# 			#if (motor == 1):
# 		#		x.move(direction,steps,0.001)
# 		#	elif (motor == 2):
# 		#		y.move(direction,steps,0.001)
# 		#	elif (motor == 3):
# 		#		z.move(direction,steps,0.001)
# 	except KeyboardInterrupt:
# 		GPIO.output(heatpin, 0)
# 		GPIO.cleanup()
# else:
def print_file(gcfile):
	global isPrinting, lineNum, totalLines, TEMP, pos
	pos = [0,0,0,0]
	isPrinting=True
	#thread.start_new_thread(adjust, ())
	lineNum = 1
	totalLines=0
	for line in open(gcfile,'r'):
		totalLines+=1
	print totalLines

	for line in open(gcfile,'r'):
		if not isPrinting:
			break
		parse_line(line)
# 		print str(lineNum)+'/'+str(totalLines), str(100*lineNum/float(totalLines))+'%'
# 		print 'Temp = '+str(temp)
		actually_adjust()
		lineNum+=1
	isPrinting = False
	lineNum=0
	totalLines=0
	print "I am done."
	wiringpi2.digitalWrite(heatpin, 0)
	wiringpi2.digitalWrite(fanpin, 0)
	TEMP = 0

server = SimpleXMLRPCServer(("192.168.1.90", 8000))
print "Listening on port 8000..."
server.register_function(x_step, "x_step")
server.register_function(y_step, "y_step")
server.register_function(z_step, "z_step")
server.register_function(e_step, "e_step")
server.register_function(get_info, "get_info")
server.register_function(set_temp, "set_temp")
server.register_function(server_receive_file, "server_receive_file")
server.register_function(remote_print, "print_file")
server.register_function(stop_print, "stop_print")
server.serve_forever()

