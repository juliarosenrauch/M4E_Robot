
import time
import board
from digitalio import DigitalInOut, Direction, Pull
import pulseio

class MotorPins:
    def __init__(self):
        self.ENA = board.D6
        self.ENB = board.D5
        self.IN1 = board.D7
        self.IN2 = board.D8
        self.IN3 = board.D9
        self.IN4 = board.D11

class SO_State:
    INIT = 0
    RUN = 1
    END = 2
    ERROR = 3

class emc:

    def __init__(self):
        # check motor_pins is a MotorPins type object
        self._cur_task = self.idle
        self._cur_task_str = ""
        self.IN1 = DigitalInOut(board.D7)
        self.IN1.direction = Direction.OUTPUT
        self.IN2 = DigitalInOut(board.D8)
        self.IN2.direction = Direction.OUTPUT
        self.IN3 = DigitalInOut(board.D9)
        self.IN3.direction = Direction.OUTPUT
        self.IN4 = DigitalInOut(board.D11)
        self.IN4.direction = Direction.OUTPUT

        self.straight_speed = 0
        self._right_side_pwm = 0
        self._left_side_pwm = 0
        self.RIGHT_SIDE = pulseio.PWMOut(board.D6, frequency=60,
        duty_cycle=self._right_side_pwm)
        self.LEFT_SIDE = pulseio.PWMOut(board.D5, frequency=60,
        duty_cycle=self._left_side_pwm)

    def straight(self, speed = 1.0, duration = None):
        self._cur_task = self._straight
        self.straight_speed = speed
        self.straight_duration = duration
        self.straight_operation_step = SO_State.INIT
        pass

    def turn(self, direction, speed=1.0, radius=None, duration=None):
        self._cur_task = self._turn
        print("Direction: {0}".format(direction))
        print("Speed: {0}".format(speed))
        print("Duration: {0}".format(duration))
        print("Radius: {0}".format(radius))
        self.turn_direction = direction
        self.turn_speed = speed
        self.turn_duration = duration
        self.turn_operation_step = SO_State.INIT
        self.turn_radius = radius
        pass

    def hold(self, duration=None):
        self._cur_task = self._hold
        self.hold_duration = duration
        self.hold_operation_step = SO_State.INIT

    def _set_dir_forward(self):
        self.IN1.value = True
        self.IN2.value = False
        self.IN3.value = False
        self.IN4.value = True

    def _set_dir_reverse(self):
        self.IN1.value = False
        self.IN2.value = True
        self.IN3.value = True
        self.IN4.value = False

    def _set_dir_idle(self):
        self.IN1.value = False
        self.IN2.value = False
        self.IN3.value = False
        self.IN4.value = False

    def _set_dir_right(self):
        self.IN1.value = True
        self.IN2.value = False
        self.IN3.value = True
        self.IN4.value = False

    def _set_dir_left(self):
        self.IN1.value = False
        self.IN2.value = True
        self.IN3.value = False
        self.IN4.value = True

    def _straight(self):
        # step 1:
        # set speed and direction
        # step 2:
        # wait until timer is done
        # step 3:
        # go back to idle
        self._cur_task_str = "straight"
        if (self.straight_operation_step == SO_State.INIT):
            self.straight_op_start_time = time.monotonic()
            if (self.straight_speed > 0):
                self._set_dir_forward()
            elif (self.straight_speed < 0):
                self._set_dir_reverse()
            else:
                self.straight_operation_step = SO_State.END

            self.RIGHT_SIDE.duty_cycle = emc._speed_to_duty_cycle(self.straight_speed)
            self.LEFT_SIDE.duty_cycle = emc._speed_to_duty_cycle(self.straight_speed)
            self.straight_operation_step = SO_State.RUN

        elif(self.straight_operation_step == SO_State.RUN):
            if (self.straight_duration != None):
                if (time.monotonic() - self.straight_op_start_time
                    > self.straight_duration):
                    self.straight_operation_step = SO_State.END

        elif(self.straight_operation_step == SO_State.END):
            self.RIGHT_SIDE.duty_cycle = 0
            self.LEFT_SIDE.duty_cycle = 0
            self._set_dir_idle()
            self._cur_task = self.idle
        elif(self.straight_operation_step == SO_State.ERROR):
            pass
        else:
            pass

    def _radius_ratio(self):
        return self.turn_radius / (self.turn_radius + 1)

    def _turn(self):
        self._cur_task_str = "turn"

        if self.turn_operation_step == SO_State.INIT:
            self.turn_op_start_time = time.monotonic()

            speed = abs(self.turn_speed)

            if self.turn_direction == "left":
                if self.turn_radius is not None:
                    if self.turn_speed > 0:
                        self._set_dir_forward()
                    elif self.turn_speed < 0:
                        self._set_dir_reverse()
                    self.RIGHT_SIDE.duty_cycle = emc._speed_to_duty_cycle(speed)
                    self.LEFT_SIDE.duty_cycle = emc._speed_to_duty_cycle(speed * self._radius_ratio())
                    self.turn_operation_step = SO_State.RUN
                else:
                    if self.turn_speed > 0:
                        self._set_dir_left()
                    elif self.turn_speed < 0:
                        self._set_dir_right()
                    self.RIGHT_SIDE.duty_cycle = emc._speed_to_duty_cycle(speed)
                    self.LEFT_SIDE.duty_cycle = emc._speed_to_duty_cycle(speed)
                    self.turn_operation_step = SO_State.RUN
                if speed == 0:
                    self.turn_operation_step = SO_State.END

            elif self.turn_direction == "right":
                if self.turn_radius is not None:
                    if self.turn_speed > 0:
                        self._set_dir_forward()
                    elif self.turn_speed < 0:
                        self._set_dir_reverse()
                    self.LEFT_SIDE.duty_cycle = emc._speed_to_duty_cycle(speed)
                    self.RIGHT_SIDE.duty_cycle = emc._speed_to_duty_cycle(speed * self._radius_ratio())
                    self.turn_operation_step = SO_State.RUN
                else:
                    if self.turn_speed > 0:
                        self._set_dir_right()
                    elif self.turn_speed < 0:
                        self._set_dir_left()
                    self.LEFT_SIDE.duty_cycle = emc._speed_to_duty_cycle(speed)
                    self.RIGHT_SIDE.duty_cycle = emc._speed_to_duty_cycle(speed)
                    self.turn_operation_step = SO_State.RUN
                if speed == 0:
                    self.turn_operation_step = SO_State.END

            else:
                self.turn_operation_step = SO_State.ERROR

        elif self.turn_operation_step == SO_State.RUN:
            if self.turn_duration is not None:
                if time.monotonic() - self.turn_op_start_time > self.turn_duration:
                    self.turn_operation_step = SO_State.END

        elif self.turn_operation_step == SO_State.END:
            print("ending")
            self.LEFT_SIDE.duty_cycle = 0
            self.RIGHT_SIDE.duty_cycle = 0
            self._set_dir_idle()
            self._cur_task = self.idle
        elif self.straight_operation_step == SO_State.ERROR:
            pass
        else:
            pass

    def stop(self):
        pass

    def idle(self):
        self._cur_task_str = "idle"

    def _hold(self):
        self._cur_task_str = "hold"
        self._set_dir_idle()
        print("hold function")
        print(self.hold_operation_step)

        if self.hold_operation_step == SO_State.INIT:
            self.hold_op_start_time = time.monotonic()
            self.hold_operation_step = SO_State.RUN

        elif self.hold_operation_step == SO_State.RUN:
            if self.hold_duration is not None:
                if time.monotonic() - self.hold_op_start_time > self.hold_duration:
                    self.hold_operation_step = SO_State.END

        elif self.hold_operation_step == SO_State.END:
            self._cur_task = self.idle

        elif self.hold_operation_step == SO_State.ERROR:
            pass

        pass

    def update(self):
        self._cur_task()
        pass

    def get_current_operation_and_status(self):

        if (self._cur_task_str == "straight"):
            return "straight", self.straight_operation_step
        elif (self._cur_task_str == "hold"):
            return "hold", self.hold_operation_step
        elif (self._cur_task_str == "idle"):
            return "idle", None
        elif self._cur_task_str == "turn":
            return "turn", self.turn_operation_step
        else:
            time.sleep(1)
            print("Error in current operation")
            return "error", None

    def _speed_to_duty_cycle(speed):
        val = int(abs(speed) * (2.0 ** 16.0 - 1))
        return val
        pass
