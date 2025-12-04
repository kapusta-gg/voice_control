"""
Модуль с интерфейсами для визуализации.
"""
from abc import ABC, abstractmethod
from typing import Callable


class VisualizerInterface(ABC):
    """Абстрактный базовый класс для визуализатора."""
    
    @abstractmethod
    def render(self) -> None:
        """Отрисовывает текущее состояние робота."""
        pass
    
    @abstractmethod
    def update(self) -> None:
        """Обновляет состояние визуализатора."""
        pass
    
    @abstractmethod
    def start(self, process_commands_callback: Callable) -> None:
        """
        Запускает визуализацию.
        
        Args:
            process_commands_callback: Функция обратного вызова для обработки команд
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Останавливает визуализацию."""
        pass