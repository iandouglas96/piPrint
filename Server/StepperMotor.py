import wiringpi2

class Stepper:
    stepPin=0 #pin numbers
    dirPin=0
    def __init__(self,stepPin,dirPin):
    	#initial a Bipolar_Stepper_Moter objects by assigning the pins
        wiringpi2.wiringPiSetupPhys()
        
        self.stepPin=stepPin
        self.dirPin=dirPin
        
        wiringpi2.pinMode(self.stepPin,1)
        wiringpi2.pinMode(self.dirPin,1)
        print "Stepper Configured"   
        
    def move(self, direction1, delay):
		if direction1==1:
			wiringpi2.digitalWrite(self.dirPin, 1);
		else:
			wiringpi2.digitalWrite(self.dirPin, 0);    
		wiringpi2.digitalWrite(self.stepPin,0)
		wiringpi2.delayMicroseconds(int(delay//2))
		wiringpi2.digitalWrite(self.stepPin,1)
		wiringpi2.delayMicroseconds(int(delay//2))