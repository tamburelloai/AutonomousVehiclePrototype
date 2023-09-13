import time
from Kit.PCA9685 import PCA9685
import os
import pickle


class Servo:
    def __init__(self):
        self.PwmServo = PCA9685(0x40, debug=True)
        self.PwmServo.setPWMFreq(50)
        self._init_angles()
        #self.PwmServo.setServoPulse(8,1500)
        #self.PwmServo.setServoPulse(9,1500)

    def setServoPwm(self,channel,angle,error=10):
        angle=int(angle)
        if channel=='0':
            self.PwmServo.setServoPulse(8,2500-int((angle+error)/0.09))
        elif channel=='1':
            self.PwmServo.setServoPulse(9,500+int((angle+error)/0.09))
        elif channel=='2':
            self.PwmServo.setServoPulse(10,500+int((angle+error)/0.09))
        elif channel=='3':
            self.PwmServo.setServoPulse(11,500+int((angle+error)/0.09))
        elif channel=='4':
            self.PwmServo.setServoPulse(12,500+int((angle+error)/0.09))
        elif channel=='5':
            self.PwmServo.setServoPulse(13,500+int((angle+error)/0.09))
        elif channel=='6':
            self.PwmServo.setServoPulse(14,500+int((angle+error)/0.09))
        elif channel=='7':
            self.PwmServo.setServoPulse(15,500+int((angle+error)/0.09))

    def load_prior_angles(self):
        try:
            if 'servo_angles.pickle' in os.listdir():
                with open('servo_angles.pickle', 'rb') as f:
                    return pickle.load(f)
        except:
            return None

    def _init_angles(self, prior=None):
        initial = {0: 36, 1: 105}
        if not prior:
            prior = self.load_prior_angles()
        if prior:
            if initial[0] < prior[0]:
                while initial[0] < prior[0]:
                    prior[0] -= 1
                    self.setServoPwm('0', prior[0])
                    time.sleep(0.001)
            elif initial[0] > prior[0]:
                while initial[0] > prior[0]:
                    prior[0] += 1
                    self.setServoPwm('0', prior[0])
                    time.sleep(0.001)
            
            if initial[1] < prior[1]:
                while initial[1] < prior[1]:
                    prior[1] -= 1
                    self.setServoPwm('1', prior[1])
                    time.sleep(0.001)
            elif initial[1] > prior[1]:
                while initial[1] > prior[1]:
                    prior[1] += 1
                    self.setServoPwm('1', prior[1])
                    time.sleep(0.001)
        else:
            self.setServoPwm('0', initial[0])
            self.setServoPwm('1', initial[1])
        self.initial = initial


# Main program logic follows:
if __name__ == '__main__':
    if False:
        print("Now servos will rotate to 90°.") 
        print("If they have already been at 90°, nothing will be observed.")
        print("Please keep the program running when installing the servos.")
        print("After that, you can press ctrl-C to end the program.")
        pwm=Servo()
        while True:
            try :
                pwm.setServoPwm('0',90)
                pwm.setServoPwm('1',90)
            except KeyboardInterrupt:
                print ("\nEnd of program")
                break

    

    
       



    
