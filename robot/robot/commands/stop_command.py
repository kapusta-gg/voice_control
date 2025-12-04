import time
from typing import Optional, Tuple
from interfaces.command_interface import CommandInterface
from interfaces.robot_interface import RobotInterface

class StopCommand(CommandInterface):
    KD_BRAKE_LINEAR = 25.0
    KD_BRAKE_ANGULAR = 15.0
    VELOCITY_TOLERANCE = 0.01

    @property
    def priority(self) -> int: return 20

    def __init__(self, duration: float = 0.0):
        self.duration = duration
        self.stop_time_start = None
        self.is_robot_stopped = False
        self.is_complete = False

    def execute(self, robot: RobotInterface) -> bool:
        if self.is_complete: return True
        linear_v, angular_v = robot.get_chassis_velocities()
        is_moving = abs(linear_v) > self.VELOCITY_TOLERANCE or abs(angular_v) > self.VELOCITY_TOLERANCE
        if is_moving:
            braking_force = -self.KD_BRAKE_LINEAR * linear_v
            braking_torque = -self.KD_BRAKE_ANGULAR * angular_v
            robot.set_chassis_forces(braking_force, braking_torque)
        else:
            robot.set_chassis_forces(0.0, 0.0)
            if not self.is_robot_stopped:
                self.is_robot_stopped = True
                if self.duration > 0: self.stop_time_start = time.time()
                else: self.is_complete = True
        if self.is_robot_stopped and self.duration > 0:
            if time.time() - self.stop_time_start >= self.duration:
                self.is_complete = True
        return self.is_complete

    def check_completion(self) -> bool: return self.is_complete
    def get_description(self) -> str:
        if self.duration > 0: return f"Остановка и удержание на {self.duration} с"
        else: return "Полная остановка"
    def get_target_pose(self, robot: RobotInterface) -> Optional[Tuple[float, float, Optional[float]]]:
        return robot.get_position()