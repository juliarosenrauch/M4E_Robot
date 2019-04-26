
#do your imports here
import time
import board
from digitalio import DigitalInOut, Direction, Pull
import pulseio

class SO_State:
    IDLE = 0
    INIT = 1
    RUN = 2

class servo:

    def __init__(self):
        #do your pin configuration here
        #also set the default value of your variables
        # self.SerPin = DigitalInOut(board.D3)
        # self.SerPin.direction = Direction.OUTPUT

        self._idle_pwm = servo._percent_to_duty_cycle(0)
        self.SERVO = pulseio.PWMOut(board.D3, frequency=50,
        duty_cycle=self._idle_pwm)
        self._operation_step = SO_State.IDLE

        self._servo_angle = 0
        self.set_angle(self._servo_angle)
        self._turn_time = 90/500
        self._operation_step = SO_State.INIT

        # No way of determining starting angle so just giving maximum time

    def update(self):
        # This will be called by the car control module
        # once every loop, use this function to do
        # any task that needs to happen in the background
        update_time = time.monotonic() - self._start_time
        if (self._operation_step == SO_State.INIT):
            if (update_time >= self._turn_time):
                self.SERVO.duty_cycle = self._idle_pwm
                self._operation_step = SO_State.IDLE
        elif (self._operation_step == SO_State.RUN):
            if (update_time >= self._turn_time):
                self._servo_angle = self._target_angle
                self.SERVO.duty_cycle = self._idle_pwm
                self._operation_step = SO_State.IDLE
            else:
                self._servo_angle += (update_time) * 500 * self._rot_dir
                self._start_time += update_time
                self._turn_time -= update_time

    def set_angle(self, degree):
        # degree: Angle move to from -90 to 90
        # Interpolation: -90 = 2.5%, 90 = 12.5%
        if (self._operation_step != SO_State.INIT):
            percent = ((2.5 * (90 - degree) + 12.5 * (degree - (-90))) / (90 - (-90))) / 100
            #print(percent)
            #print(servo._percent_to_duty_cycle(percent))
            self.SERVO.duty_cycle = servo._percent_to_duty_cycle(percent)
            angle_change = degree - self._servo_angle
            self._target_angle = degree
            if angle_change > 0:
                self._rot_dir = 1
            else:
                self._rot_dir = -1

            #Time required to turn to new position given 500 deg/s
            self._turn_time = abs(angle_change) / 500
            self._start_time = time.monotonic()

            self._operation_step = SO_State.RUN

    def get_angle(self):
        # Returns None if in initialization since angle can't be calculated

        if (self._operation_step == SO_State.INIT):
            return None
        else:
            return self._servo_angle

    def get_operation(self):
        return self._operation_step

    def _percent_to_duty_cycle(percent):
        val = int(percent * (2.0 ** 16.0 - 1))
        return val
