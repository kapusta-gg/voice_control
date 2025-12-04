"""
Модуль с реализацией робота.
"""
import math
from typing import Tuple, List

from interfaces.robot_interface import RobotInterface
from interfaces.obstacle_interface import ObstacleInterface

class Robot(RobotInterface):
    # Физические свойства
    MASS = 5.0  # кг
    # Момент инерции для прямоугольника, вращающегося вокруг центра
    MOMENT_OF_INERTIA_FACTOR = 1.0 / 12.0

    # Физические ограничения
    MAX_DRIVE_FORCE = 15.0      # Ньютоны
    MAX_TURN_TORQUE = 10.0      # Ньютон-метры
    MAX_LINEAR_SPEED = 2.0      # м/с
    MAX_ANGULAR_SPEED = 4.0     # рад/с

    # Коэффициенты сопротивления
    LINEAR_DRAG_COEFFICIENT = 2.5
    ANGULAR_DRAG_COEFFICIENT = 1.5

    HITBOX_SCALE_FACTOR = 0.2

    def __init__(
        self,
        x: float = 0.0, y: float = 0.0, theta: float = 0.0,
        width: float = 0.5, length: float = 0.5
    ):
        self.x, self.y, self.theta = x, y, theta % (2 * math.pi)
        self.width, self.length = width, length
        self.moment_of_inertia = self.MASS * (width**2 + length**2) * self.MOMENT_OF_INERTIA_FACTOR
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0
        self.target_linear_force = 0.0
        self.target_angular_torque = 0.0
        self.obstacles: List[ObstacleInterface] = []
        self.is_collided = False

    def set_chassis_forces(self, linear_force: float, angular_torque: float) -> None:
        self.target_linear_force = max(-self.MAX_DRIVE_FORCE, min(self.MAX_DRIVE_FORCE, linear_force))
        self.target_angular_torque = max(-self.MAX_TURN_TORQUE, min(self.MAX_TURN_TORQUE, angular_torque))

    def update(self, dt: float) -> None:
        if self.is_collided: return
        linear_drag_force = -self.linear_velocity * self.LINEAR_DRAG_COEFFICIENT
        angular_drag_torque = -self.angular_velocity * self.ANGULAR_DRAG_COEFFICIENT
        net_force = self.target_linear_force + linear_drag_force
        net_torque = self.target_angular_torque + angular_drag_torque
        linear_accel = net_force / self.MASS
        angular_accel = net_torque / self.moment_of_inertia
        self.linear_velocity += linear_accel * dt
        self.angular_velocity += angular_accel * dt
        self.linear_velocity = max(-self.MAX_LINEAR_SPEED, min(self.MAX_LINEAR_SPEED, self.linear_velocity))
        self.angular_velocity = max(-self.MAX_ANGULAR_SPEED, min(self.MAX_ANGULAR_SPEED, self.angular_velocity))
        if abs(self.linear_velocity) < 1e-6 and abs(self.angular_velocity) < 1e-6: return
        total_dist = abs(self.linear_velocity) * dt
        num_steps = int(math.ceil(total_dist / (self.length / 4.0))) or 1
        step_dt = dt / num_steps
        for _ in range(num_steps):
            prev_x, prev_y, prev_theta = self.x, self.y, self.theta
            self.x += self.linear_velocity * math.cos(prev_theta) * step_dt
            self.y += self.linear_velocity * math.sin(prev_theta) * step_dt
            self.theta = (self.theta + self.angular_velocity * step_dt) % (2 * math.pi)
            if self._check_body_collision_sat():
                print("[Робот] СТОЛКНОВЕНИЕ (SAT)! Аварийная остановка.")
                self.is_collided = True; self.x, self.y, self.theta = prev_x, prev_y, prev_theta
                self.linear_velocity, self.angular_velocity = 0.0, 0.0
                self.target_linear_force, self.target_angular_torque = 0.0, 0.0
                return

    def get_position(self) -> Tuple[float, float, float]: return self.x, self.y, self.theta
    def get_chassis_velocities(self) -> Tuple[float, float]: return self.linear_velocity, self.angular_velocity
    def get_robot_dimensions(self) -> Tuple[float, float]: return self.width, self.length
    def set_obstacles(self, obstacles: List[ObstacleInterface]) -> None: self.obstacles = obstacles
    def get_wheel_speeds(self) -> Tuple[float, float]:
        r_v = self.linear_velocity + (self.angular_velocity * self.width / 2)
        l_v = self.linear_velocity - (self.angular_velocity * self.width / 2)
        return l_v, r_v

    def get_target_wheel_speeds(self) -> Tuple[float, float]:
        """
        Оценивает целевые скорости на основе приложенных сил/моментов.
        Это оценка скорости в установившемся режиме (когда ускорение равно нулю).
        """
        target_linear_v = (self.target_linear_force / self.LINEAR_DRAG_COEFFICIENT) if self.LINEAR_DRAG_COEFFICIENT > 0 else 0.0
        target_angular_v = (self.target_angular_torque / self.ANGULAR_DRAG_COEFFICIENT) if self.ANGULAR_DRAG_COEFFICIENT > 0 else 0.0

        target_linear_v = max(-self.MAX_LINEAR_SPEED, min(self.MAX_LINEAR_SPEED, target_linear_v))
        target_angular_v = max(-self.MAX_ANGULAR_SPEED, min(self.MAX_ANGULAR_SPEED, target_angular_v))

        r_v = target_linear_v + (target_angular_v * self.width / 2)
        l_v = target_linear_v - (target_angular_v * self.width / 2)
        return l_v, r_v

    def _check_body_collision_sat(self):
        if not self.obstacles: return None

        hitbox_width = self.width * self.HITBOX_SCALE_FACTOR
        hitbox_length = self.length * self.HITBOX_SCALE_FACTOR
        hw, hl = hitbox_width / 2, hitbox_length / 2

        cos_t, sin_t = math.cos(self.theta), math.sin(self.theta)
        robot_corners = [(self.x + lx*cos_t - ly*sin_t, self.y + lx*sin_t + ly*cos_t) for lx, ly in [(-hl,-hw),(hl,-hw),(hl,hw),(-hl,hw)]]
        for obstacle in self.obstacles:
            ox, oy = obstacle.get_position(); ow, oh = obstacle.get_dimensions()
            obstacle_corners = [(ox-ow/2,oy-oh/2),(ox+ow/2,oy-oh/2),(ox+ow/2,oy+oh/2),(ox-ow/2,oy+oh/2)]
            axes = [(robot_corners[1][0]-robot_corners[0][0], robot_corners[1][1]-robot_corners[0][1]), (robot_corners[3][0]-robot_corners[0][0], robot_corners[3][1]-robot_corners[0][1]), (1,0), (0,1)]
            collision = True
            for axis in axes:
                robot_min, robot_max = self._project_shape(robot_corners, axis)
                obstacle_min, obstacle_max = self._project_shape(obstacle_corners, axis)
                if robot_max < obstacle_min or obstacle_max < robot_min: collision = False; break
            if collision: return obstacle
        return None

    def _project_shape(self, corners, axis):
        axis_len = math.sqrt(axis[0]**2 + axis[1]**2)
        if axis_len == 0: return 0,0
        norm_axis = (axis[0] / axis_len, axis[1] / axis_len)
        min_proj, max_proj = float('inf'), float('-inf')
        for corner in corners:
            projection = corner[0] * norm_axis[0] + corner[1] * norm_axis[1]
            min_proj, max_proj = min(min_proj, projection), max(max_proj, projection)
        return min_proj, max_proj