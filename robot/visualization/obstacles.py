"""
Модуль с реализацией препятствий.
"""
from typing import Tuple

from interfaces.obstacle_interface import ObstacleInterface
import pygame


class Obstacle(ObstacleInterface):

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        avoidance_margin: float = 0.3,
        color: Tuple[int, int, int] = (255, 0, 0)  # Красный цвет по умолчанию
    ):
        """
        Инициализирует препятствие.
        
        Args:
            x: X-координата центра препятствия
            y: Y-координата центра препятствия
            width: Ширина препятствия
            height: Высота препятствия
            avoidance_margin: Дополнительный отступ для обхода препятствия
            color: Цвет препятствия в формате RGB
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.avoidance_margin = avoidance_margin
        self.color = color
        
        # Создаем Rect для препятствия с учетом отступа
        self.rect = pygame.Rect(
            x - (width / 2 + avoidance_margin),
            y - (height / 2 + avoidance_margin),
            width + 2 * avoidance_margin,
            height + 2 * avoidance_margin
        )
        
        # Создаем Rect для основного тела препятствия
        self.body_rect = pygame.Rect(
            x - width / 2,
            y - height / 2,
            width,
            height
        )
    
    def get_position(self) -> Tuple[float, float]:
        """
        Возвращает позицию препятствия.
        
        Returns:
            Tuple[float, float]: (x, y) координаты центра препятствия
        """
        return self.x, self.y
    
    def get_dimensions(self) -> Tuple[float, float]:
        """
        Возвращает размеры препятствия.
        
        Returns:
            Tuple[float, float]: (ширина, высота) препятствия
        """
        return self.width, self.height
    
    def get_color(self) -> Tuple[int, int, int]:
        """
        Возвращает цвет препятствия.
        
        Returns:
            Tuple[int, int, int]: Цвет препятствия в формате RGB
        """
        return self.color