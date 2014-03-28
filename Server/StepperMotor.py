import RPi.GPIO as GPIO
import time

class Stepper:
    
    direction=1
    position=0
    
    stepPin=0 #pin numbers
    dirPin=0
    def __init__(self,stepPin,dirPin):
    #initial a Bipolar_Stepper_Moter objects by assigning the pins
    
        GPIO.setmode(GPIO.BOARD)
        
        self.stepPin=stepPin
        self.dirPin=dirPin
        
        GPIO.setup(self.stepPin,GPIO.OUT)
        GPIO.setup(self.dirPin,GPIO.OUT)
        print "Stepper Configured"
        self.direction=0      
        self.position=0
        
    def move(self, direction1, steps, delay=0.2):
        self.direction = direction1
	if direction1==1:
	    GPIO.output(self.dirPin, 1);
	else:
            GPIO.output(self.dirPin, 0);
        for i in range(steps):         
            GPIO.output(self.stepPin,0)
            time.sleep(delay/2.0)
            GPIO.output(self.stepPin,1)
            time.sleep(delay/2.0)
            self.position += direction1

    def unhold(self):
        GPIO.output(self.dirPin,0)
        GPIO.output(self.stepPin,0)
        
