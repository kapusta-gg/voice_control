"""
Модуль с интерфейсами для робота с динамической моделью управления.
"""
from abc import ABC, abstractmethod
from typing import Tuple, List

from interfaces.obstacle_interface import ObstacleInterface


class RobotInterface(ABC):
    """Абстрактный базовый класс для робота, управляемого через силы и моменты."""

    @abstractmethod
    def set_chassis_forces(self, linear_force: float, angular_torque: float) -> None:
        """
        Устанавливает целевую линейную силу и угловой момент для шасси робота.

        Args:
            linear_force: Линейная сила в Ньютонах.
            angular_torque: Угловой момент (крутящий момент) в Ньютон-метрах.
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Обновляет состояние робота за временной шаг dt."""
        pass

    @abstractmethod
    def get_position(self) -> Tuple[float, float, float]:
        """Возвращает текущую позицию и ориентацию робота (x, y, theta)."""
        pass

    @abstractmethod
    def get_chassis_velocities(self) -> Tuple[float, float]:
        """Возвращает текущую линейную и угловую скорость шасси."""
        pass

    @abstractmethod
    def get_wheel_speeds(self) -> Tuple[float, float]:
        """Возвращает текущие скорости колес (для информации/визуализации)."""
        pass

    @abstractmethod
    def get_robot_dimensions(self) -> Tuple[float, float]:
        """Возвращает размеры робота (width, length)."""
        pass

    @abstractmethod
    def set_obstacles(self, obstacles: List[ObstacleInterface]) -> None:
        """Устанавливает список препятствий для проверки коллизий."""
        pass