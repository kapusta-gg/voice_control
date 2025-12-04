"""
Модуль с реализацией команды остановки.
"""

from interfaces.command_interface import CommandInterface
from interfaces.robot_interface import RobotInterface
import time


class StopCommand(CommandInterface):
    """Команда для остановки робота."""
    
    @property
    def priority(self) -> int:
        """Возвращает приоритет команды."""
        return 20  # Очень высокий приоритет для команды остановки
    
    def __init__(self, duration: float = 0.0):
        """
        Инициализирует команду остановки.
        
        Args:
            duration: Продолжительность остановки в секундах (0 для немедленной остановки)
        """
        self.duration = duration
        self.start_time = None
        self.is_complete = False
    
    def execute(self, robot: RobotInterface) -> bool:
        """
        Выполняет команду, применяя её к роботу.
        
        Args:
            robot: Робот, к которому применяется команда
            
        Returns:
            bool: True, если команда завершена, False, если команда продолжается
        """
        # Если это первое выполнение команды, запоминаем время начала
        if self.start_time is None:
            self.start_time = time.time()
        
        # Останавливаем робота
        robot.set_wheel_speeds(0.0, 0.0)
        
        # Если задана продолжительность, проверяем, не истекла ли она
        if self.duration > 0:
            current_time = time.time()
            if current_time - self.start_time >= self.duration:
                self.is_complete = True
                return True
        else:
            return True  # Если продолжительность не задана, команда завершается сразу
        
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
        if self.duration > 0:
            return f"Остановка на {self.duration} секунд"
        else:
            return "Остановка"

    def to_dict(self) -> dict:
        return {
            'type': 'stop',
            'params': {'duration': self.duration}
        }
