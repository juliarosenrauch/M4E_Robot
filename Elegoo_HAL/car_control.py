
import time
import board
from pni_libs.helpers import *
from emc import *
from servo import *
#from line_sensor import *
from ultra import *
#from line_follow import *

class Car_Control:
    def __init__(self):
        self.motors = emc()
        self.servo = servo()
        self.ultrasensor = ultra()
        #self.line_follow = Line_follow()
        self.cur_test = None
        # TODO: initialize other modules

        self._scan_init()
        self.previousmillis = millis()


    def update(self):
        self.motors.update()
        self.servo.update()
        self.ultrasensor.update()

        #self.line_follow.update()

        # if ((millis() - self.previousmillis) > 1000):
        # self._scanning_update()


        if (self.cur_test is not None):
            self.cur_test()

    def servo_test_start(self):
        # if (self.servo._operation_step == SO_State.INIT):
        #    print("Servo has not been initialized yet.")
        #    return -1
        self.servo_test_actions = []
        self.servo_test_actions.append(-90)
        self.servo_test_actions.append(-45)
        self.servo_test_actions.append(0)
        self.servo_test_actions.append(45)
        self.servo_test_actions.append(90)
        self.servo_test_index = 0
        self.ultrasensor_detections = []
        self.angle_set = 0
        self.cur_test = self._servo_test_update
        return 0

    def _servo_test_update(self):
        if (self.servo.get_operation() != 1):
            if (self.servo_test_index < len(self.servo_test_actions)):
                angle = self.servo_test_actions[self.servo_test_index]
                if (self.angle_set == 0):
                    print("Servo going to angle: {0}".format(angle))
                    self.angle_set = 1
                    self.servo.set_angle(angle)
                else:
                    if (abs(float(self.servo.get_angle()) - float(angle)) < 2):
                        self.angle_set = 0
                        self.servo_test_index += 1
                        print("servo in position")

                        ultrasensor_reading = self.ultrasensor.get_obj()
                        print("Ultrasonic sensor reading: {0}".format(ultrasensor_reading))
                        if (ultrasensor_reading < 0.01):
                            self.ultrasensor_detections.append([self.servo.get_angle(), "Detection"])
                        else:
                            self.ultrasensor_detections.append([self.servo.get_angle(), "None"])
            else:
                    print("servo test sequence complete")
                    for pos in self.ultrasensor_detections:
                        #print(pos)
                        pass
                    self.cur_test = None

    @staticmethod
    def angle_to_duration(angle):
        if angle >= 0:
            return angle * 0.4 / 90.0000
        else:
            return -1 * angle * 0.4 / 90.0000

    def emc_test_straight(self):
        self.cur_test = self._emc_test_update
        self.movements = []
        self.movements.append(["straight", 0.5, 1])
        self.movements.append(["straight", 1.0, 1])
        self.movements.append(["straight", -1.0, 0.02])
        self.movements.append(["straight", -0.5, 3])
        self.movements.append(["straight", 1.0, 0.02])
        self.movement_idx = 0

    def emc_test_turn(self):
        self.cur_test = self._emc_test_update
        self.movements = []
        time = 0.1
        while time <= 0.6:
            self.movements.append(["turn", "left", 0.7, None, time])
            self.movements.append(["hold", 0.5])
            self.movements.append(["turn", "right", 0.7, None, time])
            self.movements.append(["hold", 0.5])
            time += 0.1
        self.movement_idx = 0

    def _emc_test_update(self):
        op_id, op_status = self.motors.get_current_operation_and_status()
        if (op_id == "idle"):
            if (self.movement_idx < len(self.movements)):
                cur_movement = self.movements[self.movement_idx]
                if (cur_movement[0] == "straight"):
                    print("moving straight")
                    self.motors.straight(cur_movement[1], cur_movement[2])
                elif cur_movement[0] == "turn":
                    print("turning")
                    self.motors.turn(cur_movement[1], speed=cur_movement[2], radius=cur_movement[3], duration=cur_movement[4])
                elif cur_movement[0] == "hold":
                    print("holding")
                    self.motors.hold(duration=cur_movement[1])
                self.movement_idx = self.movement_idx + 1
            else:
                print("emc test sequence complete")
                self.cur_test = None

    def _scan_init(self):
        # Scanning initial variables
        self._scan_angles = list(range(-90, 100, 10))
        self._scan_index = 0
        self._scan_angle_set = 0
        self._scan_True_count = 0
        self._scan_largest_True_count = 0
        self._scan_results = []
        self._scan_largest_obstacle = None
        self._scan_result_valid = False
        self._scan_all_distances = []
        self._scan_distance = 0
        self._last_angle_idx = 0

    def _scanning_update(self):
        if (self.servo.get_operation() != 1):
            angle = self._scan_angles[self._scan_index]
            if (self._scan_angle_set == 0):
                self._scan_angle_set = 1
                self.servo.set_angle(angle)
            else:
                if (abs(float(self.servo.get_angle()) - float(angle)) < 2):
                    self._scan_angle_set = 0
                    tf, distance = self.ultrasensor.tf_distance()
                    self._scan_results.append(tf)
                    self._scan_all_distances.append(distance)

                    if self._scan_results[self._scan_index]:
                        self._scan_True_count += 1

                    else:
                        if (self._scan_True_count > self._scan_largest_True_count):
                            self._scan_largest_True_count = self._scan_True_count
                            self._scan_last_angle = angle - 10
                            self._scan_True_count = 0
                            self._last_angle_idx = self._scan_index

                        else:
                            self._scan_True_count = 0

                    if self._scan_index == 18:
                        if self._scan_largest_True_count == 0:
                            self._scan_largest_obstacle = None
                            print("No obstacles")

                        else:
                            if (self._scan_True_count > self._scan_largest_True_count):
                                self._scan_largest_True_count = self._scan_True_count
                                self._scan_last_angle = angle
                                self._last_angle_idx = self._scan_index

                            self._scan_largest_obstacle = self._scan_last_angle - (5 * self._scan_largest_True_count)
                            print("largest object angle: ", self._scan_largest_obstacle)

                            # we know the last index of the largest, we can find the middle index from subtracting half of hte true largest true count
                            # use that index to find distance

                            middleindex = self._last_angle_idx - int(self._scan_largest_True_count / 2)
                            self._scan_distance = self._scan_all_distances[middleindex]

                        self._scan_index = 0
                        self._scan_results = []
                        self._scan_True_count = 0
                        self._scan_largest_True_count = 0
                        self._scan_result_valid = True

                    else:
                        self._scan_index += 1

    def static_tracking_test_start(self):
        self.cur_test = self._static_tracking_test

    def _static_tracking_test(self):
        if (self._scan_largest_obstacle != None and self._scan_result_valid):
            self._scan_result_valid = False
            op_id, op_status = self.motors.get_current_operation_and_status()
            duration = Car_Control.angle_to_duration(self._scan_largest_obstacle)
            if (self._scan_largest_obstacle > 2.5):
                if (op_id == "idle"):
                    print("turning left")
                    self.motors.turn("left", speed=0.7, radius=None, duration=duration)
            elif (self._scan_largest_obstacle < -2.5):
                if (op_id == "idle"):
                    print("turning right")
                    self.motors.turn("right", speed=0.7, radius=None, duration=duration)
            else:
                pass
        else:
            pass

    def lineFollowStart(self):
        self.cur_test = self.line_cases

    def line_cases(self):
        direction = self.line_follow.getStatus()
        print(direction)
        if (direction == "str8"):
            self.motors.straight(0.25, 0.01)
        elif (direction == "left"):
            self.motors.turn("right", speed = 0.3, radius = None, duration = 0.01)
        elif (direction == "right"):
            self.motors.turn("left", speed = 0.3, radius = None, duration = 0.01)
