"""
Модуль с реализацией команды поворота.
"""

from typing import Optional
import math

from interfaces.command_interface import CommandInterface
from interfaces.robot_interface import RobotInterface


class TurnCommand(CommandInterface):
    """Команда для поворота робота."""

    @property
    def priority(self) -> int:
        return 1



    def __init__(self, angular_speed: float = 0.5, angle: Optional[float] = None):
        """
        Инициализирует команду поворота.
        
        Args:
            angular_speed: Угловая скорость в рад/с (положительная - поворот вправо, отрицательная - влево)
            angle: Угол поворота в радианах (None для непрерывного поворота)
        """
        self.angular_speed = angular_speed
        self.angle = angle
        self.start_theta = None
        self.target_theta = None
        self.initial_direction = None
        self.is_complete = False
    
    def execute(self, robot: RobotInterface) -> bool:
        pass
    
    def _check_angle_reached(self, current_theta: float) -> bool:
        pass
    
    def check_completion(self) -> bool:
        pass
    
    def get_description(self) -> str:
        """
        Возвращает описание команды.
        
        Returns:
            str: Текстовое описание команды
        """
        if self.angle is not None:
            angle_degrees = math.degrees(abs(self.angle))
            direction = "вправо" if self.angular_speed < 0 else "влево"
            return f"Поворот {direction} на {angle_degrees:.1f}°: угловая скорость={abs(self.angular_speed)} рад/с"
        else:
            direction = "вправо" if self.angular_speed < 0 else "влево"
            return f"Поворот {direction}: угловая скорость={abs(self.angular_speed)} рад/с"
        
        
    def to_dict(self) -> dict:
        return {
            'type': 'turn',
            'params': {
                'angular_speed': self.angular_speed,
                'angle': self.angle
            }
        }
