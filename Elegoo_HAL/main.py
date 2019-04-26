# New project template for Adafruit Metro M4
# Created by: Mark Ma (mma@precision-nano.com)
# Created on: 23 Sept 2018


import time
import board
from pni_libs.helpers import *
from car_control import *


# Declare global variables here
# Avoid global variables if possible

class Elegoo_HAL:

    def __init__(self):
        # declare "global" variables here
        self.car = Car_Control()

    def setup(self):
        self.flip_flop = True

        self.car.static_tracking_test_start()
        # self.car.servo_test_start()
        # self.car.lineFollowStart()

    def loop(self):
        self.car.update()

if (__name__ == "__main__"):
    app = Elegoo_HAL()
    app.setup()
    print("Ready")
    while True:
        app.loop()
