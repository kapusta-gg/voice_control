"""
Модуль с интерфейсами для робота.
"""
from abc import ABC, abstractmethod
from typing import Tuple


class RobotInterface(ABC):
    """Абстрактный базовый класс для робота."""
    
    @abstractmethod
    def set_wheel_speeds(self, left_speed: float, right_speed: float) -> None:
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        pass
    
    @abstractmethod
    def get_position(self) -> Tuple[float, float, float]:
        pass
    
    @abstractmethod
    def get_wheel_speeds(self) -> Tuple[float, float]:
        pass
    
    @abstractmethod
    def get_target_wheel_speeds(self) -> Tuple[float, float]:
        pass
    
    @abstractmethod
    def get_robot_dimensions(self) -> Tuple[float, float]:
        pass

    @abstractmethod
    def get_max_speed(self) -> float:
        pass
