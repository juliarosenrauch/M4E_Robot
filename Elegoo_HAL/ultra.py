import time
from pni_libs.helpers import *
import microcontroller as mc
import board
from digitalio import DigitalInOut, Direction, Pull
import pulseio

class constants:

    LOW = 0
    HIGH = 1

    CM = 28
    INC = 71

    TIMEOUT = 5 # in milliseconds

    # default pins on elegoo v3 bot
    TRIGPIN = board.A5
    ECHOPIN = board.A4

    # distance at which object is considered present
    RANGE = 25

class ultra:

    def __init__(self, trigPin = constants.TRIGPIN, echoPin = constants.ECHOPIN):
        self.trig = trigPin
        self.echo = echoPin
        if (self.trig == self.echo):
            self.threePins = True
        else:
            self.threePins = False

        self.trigdig = DigitalInOut(self.trig)
        self.trigdig.direction = Direction.OUTPUT

        self.echodig = DigitalInOut(self.echo)
        self.echodig.direction = Direction.INPUT

        self.previousmillis = 0
        self.timeout = constants.TIMEOUT

    def update(self):
        # This will be called by the car control module
        # once every loop, use this function to do
        # any task that needs to happen in the background
        pass


    def timing(self):
        if (self.threePins):
            self.trigdig.direction = digitalio.Direction.OUTPUT

        self.trigdig.value = constants.LOW
        mc.delay_us(2)
        self.trigdig.value = constants.HIGH
        mc.delay_us(10)
        self.trigdig.value = constants.LOW

        if (self.threePins):
            self.trigdig.direction = digitalio.Direction.INPUT

        delay = constants.TIMEOUT / 10 * 1000
        n_delay = 0
        while(self.echodig.value == constants.LOW):
            mc.delay_us(10)
            n_delay += 1

            if(n_delay > delay):
                return None


        n_delay = 0
        timed_out = 0
        while(self.echodig.value == constants.HIGH):
            mc.delay_us(10)
            n_delay += 1

            if(n_delay > delay):
                timed_out = 1
                break

        if (timed_out):
            return None
        else:
            return n_delay / 1000 * 10



    # If the unit of measure is not passed as a parameter,
    # by default, it will return the distance in centimeters.
    # To change the default, replace CM by INC.
    def read(self, und = constants.CM):
        tim = self.timing()
        if (tim != None):
            return tim * 5000 / und
        else:
            return None


    # This method is too verbal, so, it's deprecated.
    # Use read() instead.

    def get_obj(self, und = constants.CM):
        return self.read(und)

    # Return true or false value if object is present

    def is_there_obj(self, distance = constants.RANGE):
        obj = self.get_obj()
        if (obj == None):
            return False
        else:
            return (obj < distance)

    def tf_distance(self, distance = constants.RANGE):
        obj = self.get_obj()
        if (obj == None):
            return False, None
        else:
            if (obj < distance):
                return True, obj
            else:
                return False, None
