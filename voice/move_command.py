from typing import Optional
import math

from interfaces.command_interface import CommandInterface
from interfaces.robot_interface import RobotInterface


class MoveCommand(CommandInterface):
    """Команда для движения робота."""
    
    @property
    def priority(self) -> int:
        """Возвращает приоритет команды."""
        return 1

    def __init__(self, linear_speed: float = 0.5, angular_speed: float = 0.0, distance: Optional[float] = None):
        """
        Инициализирует команду движения.

        Args:
            linear_speed: Линейная скорость в м/с
            angular_speed: Угловая скорость в рад/с
            distance: Расстояние для движения в метрах (None для непрерывного движения)
        """
        self.linear_speed = linear_speed
        self.angular_speed = angular_speed
        self.distance = distance
        self.traveled_distance = 0.0
        self.start_x = None
        self.start_y = None
        self.start_theta = None
        self.is_complete = False

    def execute(self, robot: RobotInterface) -> bool:
        """
        Выполняет команду, применяя её к роботу.
        
        Args:
            robot: Робот, к которому применяется команда
            
        Returns:
            bool: True, если команда завершена, False, если команда продолжается
        """
        # Если это первое выполнение команды, запоминаем начальную позицию и ориентацию
        if self.start_x is None or self.start_y is None or self.start_theta is None:
            x, y, theta = robot.get_position()
            self.start_x = x
            self.start_y = y
            self.start_theta = theta
        
        # Получаем текущую позицию и ориентацию
        x, y, theta = robot.get_position()
        
        # Если задано расстояние, проверяем, не достигли ли мы его
        if self.distance is not None:
            # Вычисляем пройденное расстояние
            self.traveled_distance = math.sqrt((x - self.start_x) ** 2 + (y - self.start_y) ** 2)
            
            # Если достигли заданного расстояния, останавливаем робота и завершаем команду
            if self.traveled_distance >= self.distance:
                robot.set_wheel_speeds(0.0, 0.0)
                self.is_complete = True
                return True
        
        # Преобразуем линейную и угловую скорости в скорости колес
        # с учетом текущей ориентации робота
        width = robot.get_robot_dimensions()[0]
        
        # Применяем скорости относительно текущей ориентации робота
        left_speed = self.linear_speed - (self.angular_speed * width / 2)
        right_speed = self.linear_speed + (self.angular_speed * width / 2)
        
        # Устанавливаем скорости колес
        robot.set_wheel_speeds(left_speed, right_speed)
        
        # Если расстояние не задано, команда никогда не завершается
        return False
    
    def check_completion(self) -> bool:
        """Проверяет, завершена ли команда."""
        return self.is_complete
    
    def get_description(self) -> str:
        """
        Возвращает описание команды.

        Returns:
            str: Текстовое описание команды
        """
        if self.distance is not None:
            return f"Движение на {self.distance} м: линейная скорость={self.linear_speed} м/с, угловая скорость={self.angular_speed} рад/с"
        else:
            return f"Движение: линейная скорость={self.linear_speed} м/с, угловая скорость={self.angular_speed} рад/с"

    def to_dict(self) -> dict:
        return {
            'type': 'move',
            'params': {
                'linear_speed': self.linear_speed,
                'angular_speed': self.angular_speed,
                'distance': self.distance
            }
        }