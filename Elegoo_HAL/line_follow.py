import board
import time
from digitalio import DigitalInOut, Direction, Pull

class Line_follow:

    # in millimeters
    SENSOR_SEPARATION = 14.14

    def __init__(self):
        self.LEFT = DigitalInOut(board.D2)
        self.LEFT.direction = Direction.INPUT
        self.MIDDLE = DigitalInOut(board.D4)
        self.MIDDLE.direction = Direction.INPUT
        self.RIGHT = DigitalInOut(board.D10)
        self.RIGHT.direction = Direction.INPUT
        self.previousState = [self.read_left(), self.read_mid(), self.read_right()]
        self.previousTime = time.monotonic()

    def update(self):
        currentTime = time.monotonic()
        currentState = [self.read_left(), self.read_mid(), self.read_right()]

        if currentState[1] == True:
            self.status = "str8"
        elif currentState[0] == True:
            self.status = "left"
        elif currentState[2] == True:
            self.status = "right"

    def getStatus(self):
        return self.status

    def read_left(self):
        if (self.LEFT.value):
            return True
        else:
            return False

    def read_mid(self):
        if (self.MIDDLE.value):
            return True
        else:
            return False

    def read_right(self):
        if (self.RIGHT.value):
            return True
        else:
            return False

    #distance between sensors is 14.14mm
    def is_departing(self):
        if read_mid():
            if read_left():
                return "left"
            elif read_right():
                return "right"
            elif read_mid():
                return "straight"

        if read_left():
            if read.left():
                return "straight"
            elif read_mid():
                return "right"
            elif read_right():
                return "really right"
            else:
                return "left off track"

        if read_right():
            if read.left():
                return "really left"
            elif read_mid():
                return "left"
            elif read_right():
                return "straight"
            else:
                return "right off track"

    def turn_speed(self):
        refTime = time.monotonic()

        if (is_departing() == "right"):
            currentTime = time.monotonic()

            #speed in mm/s
            speed = SENSOR_SEPARATION / (currentTime - refTime)
            return string(speed) + "mm/s right"

        elif (is_departing() =="left"):
            currentTime = time.monotonic()

            #speed in mm/s
            speed = SENSOR_SEPARATION / (currentTime - refTime)
            return string(speed) + "mm/s left"
