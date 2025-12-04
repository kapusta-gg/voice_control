from abc import ABC, abstractmethod
from typing import Optional, Tuple


class CommandInterface(ABC):
    @property
    @abstractmethod
    def priority(self) -> int:
        pass

    @abstractmethod
    def execute(self, robot) -> bool:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def check_completion(self) -> bool:
        pass

    @abstractmethod
    def get_target_pose(self, robot) -> Optional[Tuple[float, float, Optional[float]]]:
        pass