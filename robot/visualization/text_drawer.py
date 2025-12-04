"""
Модуль для отрисовки текста с использованием кастомных шрифтов.
"""
import pygame
from typing import Tuple, Optional


class TextDrawer:
    """Класс для отрисовки текста с использованием кастомных шрифтов."""
    
    def __init__(
        self,
        font_path: str,
        font_size: int,
        text_color: Tuple[int, int, int],
        background_color: Optional[Tuple[int, int, int]] = None,
        pos: Tuple[float, float] = (0, 0)
    ):
        self.font = pygame.font.Font(font_path, font_size)
        self.text_color = text_color
        self.background_color = background_color
        self.pos = pos

    def draw(self, surface: pygame.Surface, text: str) -> None:
        """
        Отрисовывает текст на поверхности.

        Args:
            surface: Поверхность для отрисовки
            text: Текст для отрисовки
        """
        text_surface = self.font.render(text, True, self.text_color, self.background_color)
        text_rect = text_surface.get_rect(topleft=self.pos)
        surface.blit(text_surface, text_rect)

    def set_position(self, pos: Tuple[float, float]) -> None:
        """
        Устанавливает позицию текста.

        Args:
            pos: Новая позиция текста (x, y)
        """
        self.pos = pos