"""
Модуль с интерфейсом для команд робота.
"""
from abc import ABC, abstractmethod

class CommandInterface(ABC):
    """Абстрактный базовый класс для команд робота."""

    @property
    @abstractmethod
    def priority(self) -> int:
        """
        Возвращает приоритет команды.

        Returns:
            int: Приоритет команды (чем выше число, тем выше приоритет)
        """
        pass
    
    @abstractmethod
    def execute(self, robot) -> bool:
        """
        Выполняет команду, применяя её к роботу.
        
        Args:
            robot: Робот, к которому применяется команда
            
        Returns:
            bool: True, если команда завершена, False, если команда продолжается
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Возвращает описание команды.

        Returns:
            str: Текстовое описание команды
        """
        pass
    @abstractmethod
    def check_completion(self) -> bool:
        """
        Проверяет, завершена ли команда.

        Returns:
            bool: True, если команда завершена, False, если команда продолжается
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Сериализует команду и ее параметры в словарь."""
        pass