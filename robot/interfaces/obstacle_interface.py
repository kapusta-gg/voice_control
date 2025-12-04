"""
Модуль с интерфейсом для препятствий.
"""
from abc import ABC, abstractmethod
from typing import Tuple

class ObstacleInterface(ABC):
    """Абстрактный базовый класс для препятствий."""
    
    @abstractmethod
    def get_position(self) -> Tuple[float, float]:
        """
        Возвращает позицию препятствия.
        
        Returns:
            Tuple[float, float]: (x, y) координаты центра препятствия
        """
        pass
    
    @abstractmethod
    def get_dimensions(self) -> Tuple[float, float]:
        """
        Возвращает размеры препятствия.
        
        Returns:
            Tuple[float, float]: (ширина, высота) препятствия
        """
        pass