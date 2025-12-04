from typing import Optional, Tuple
import math
import time
from interfaces.command_interface import CommandInterface
from interfaces.robot_interface import RobotInterface


class MoveCommand(CommandInterface):
    # Коэффициенты PID-регулятора по ПОЗИЦИИ
    KP = 20.0  # Пропорциональный gain: ошибка позиции -> сила
    KI = 2  # Интегральный gain: уменьшен для снижения перерегулирования
    KD = 25.0  # Дифференциальный gain: демпфирование скорости

    MAX_INTEGRAL = 2.0  # Ограничение для anti-windup

    # Пороги завершения
    DISTANCE_TOLERANCE = 0.01
    VELOCITY_TOLERANCE = 0.01

    @property
    def priority(self) -> int:
        return 1

    def __init__(self, linear_speed: float, distance: Optional[float] = None):
        if linear_speed == 0 and distance is not None:
            raise ValueError("Не заданы значения.")

        self.direction_sign = math.copysign(1, linear_speed) if linear_speed != 0 else 1.0
        self.max_speed = abs(linear_speed)

        self.distance_to_travel = abs(distance) if distance is not None else None

        self.start_x, self.start_y, self.start_theta = None, None, None
        self.is_complete = False
        self.integral_error = 0.0
        self.last_time = None

    def execute(self, robot: RobotInterface) -> bool:
        current_time = time.time()
        dt = (current_time - self.last_time) if self.last_time is not None else 1.0 / 60.0
        self.last_time = current_time

        current_linear_velocity, _ = robot.get_chassis_velocities()

        if self.distance_to_travel is not None:
            # --- РЕЖИМ: ДВИЖЕНИЕ НА ДИСТАНЦИЮ ---
            if self.start_x is None:
                self.start_x, self.start_y, self.start_theta = robot.get_position()

            current_x, current_y, _ = robot.get_position()
            traveled_distance = math.sqrt((current_x - self.start_x) ** 2 + (current_y - self.start_y) ** 2)
            position_error = self.distance_to_travel - traveled_distance

            # Проверка завершения команды
            if abs(position_error) < self.DISTANCE_TOLERANCE and abs(current_linear_velocity) < self.VELOCITY_TOLERANCE:
                robot.set_chassis_forces(0.0, 0.0)
                self.is_complete = True
                return True

            # PID-контроллер по позиции
            self.integral_error += position_error * dt
            # Anti-windup и сброс интеграла у цели для предотвращения перерегулирования
            if abs(position_error) < 0.05:
                self.integral_error = 0
            self.integral_error = max(-self.MAX_INTEGRAL, min(self.MAX_INTEGRAL, self.integral_error))

            p_term = self.KP * position_error
            i_term = self.KI * self.integral_error
            d_term = -self.KD * (current_linear_velocity * self.direction_sign)  # Тормозим скорость

            linear_force = (p_term + i_term + d_term) * self.direction_sign

        else:
            # --- РЕЖИМ: НЕПРЕРЫВНОЕ ДВИЖЕНИЕ ---
            # PI-регулятор по СКОРОСТИ
            speed_error = self.max_speed - abs(current_linear_velocity)

            self.integral_error += speed_error * dt
            self.integral_error = max(-self.MAX_INTEGRAL, min(self.MAX_INTEGRAL, self.integral_error))

            p_term = self.KP * speed_error
            i_term = self.KI * self.integral_error

            linear_force = (p_term + i_term) * self.direction_sign

        robot.set_chassis_forces(linear_force, 0.0)
        return self.is_complete

    def check_completion(self) -> bool:
        return self.is_complete

    def get_description(self) -> str:
        direction = "вперёд" if self.direction_sign > 0 else "назад"
        if self.distance_to_travel is not None:
            return f"Движение {direction} на {self.distance_to_travel:.1f} м"
        else:
            return f"Непрерывное движение {direction} со скоростью {self.max_speed:.1f} м/с"

    def get_target_pose(self, robot: RobotInterface) -> Optional[Tuple[float, float, Optional[float]]]:
        if self.distance_to_travel is None:
            return None

        # Определяем начальную позицию и ориентацию
        if self.start_theta is not None:
            start_x, start_y, start_theta = self.start_x, self.start_y, self.start_theta
        else:
            start_x, start_y, start_theta = robot.get_position()

        # Расстояние с учетом направления
        effective_distance = self.distance_to_travel * self.direction_sign

        # Вычисляем целевые координаты
        target_x = start_x + effective_distance * math.cos(start_theta)
        target_y = start_y + effective_distance * math.sin(start_theta)

        # Целевая ориентация не меняется
        return target_x, target_y, start_theta