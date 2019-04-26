import time
import board
from pni_libs.helpers import *
from emc import *
import ultra

# Declare global variables here
# Avoid global variables if possible

class Elegoo_HAL:

    def __init__(self):
        # declare "global" variables here
        self.motor_pins = MotorPins()
        print("motor_pins success")
        self.car = emc()
        print("car success")
        self.ultrasensor = ultra.ultra()
        print("ultra success")
        self.previousmillis = millis()

    def loop(self):
        self.ultrasensor.update()
        distance2object = self.ultrasensor.get_obj()
        # boolean = self.ultrasensor.is_there_obj()

        if ((millis() - self.previousmillis) > 15):
            print("distance to object: ", distance2object)
            self.previousmillis = millis()
        # print("true/false: ", boolean)

if (__name__ == "__main__"):
    app = Elegoo_HAL()
    print("Ready")
    while True:
        app.loop()
