
import math
import queue
import threading
import zmq
from typing import Dict, Any, Optional

from robot.robot import Robot
from robot.command_queue import CommandQueue
from visualization.visualizer import RobotVisualizer
from interfaces.command_interface import CommandInterface
from robot.commands.move_command import MoveCommand
from robot.commands.turn_command import TurnCommand
from robot.commands.stop_command import StopCommand

ZMQ_PORT = 5555


def command_factory(data: Dict[str, Any]) -> Optional[CommandInterface]:
    """Фабрика для создания объектов команд из словаря."""
    command_type = data.get("command")
    params = data.get("params", {})

    if command_type == "move":
        distance = params.get("distance")
        linear_speed = params.get("linear_speed", 0.5)

        if distance is not None and distance < 0:
            linear_speed = -abs(linear_speed)
        final_distance = abs(distance) if distance is not None else None

        return MoveCommand(
            linear_speed=linear_speed,
            distance=final_distance
        )

    elif command_type == "turn":
        return TurnCommand(
            angular_speed=params.get("angular_speed", 0.8),
            angle=params.get("angle")
        )
    elif command_type == "stop":
        return StopCommand(
            duration=params.get("duration", 0.0)
        )
    else:
        print(f"[ZMQ Клиент] Неизвестный тип команды: {command_type}")
        return None


def zmq_client_thread(command_q: queue.Queue):
    """
    Клиент ZeroMQ, работающий в отдельном потоке.
    Слушает команды и кладет их в потокобезопасную очередь.
    """
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://localhost:{ZMQ_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print(f"[ZMQ Клиент] Клиент ZeroMQ запущен на порту {ZMQ_PORT}...")

    try:
        while True:
            data = socket.recv_json()
            print(f"[ZMQ Клиент] Получена команда: {data}")
            command_obj = command_factory(data)
            if command_obj:
                command_q.put(command_obj)
    except (zmq.ZMQError, KeyboardInterrupt):
        print("[ZMQ Клиент] Клиент ZeroMQ остановлен.")
    finally:
        socket.close()
        context.term()


def main():
    """Главная функция для запуска симуляции."""
    # 1. Инициализация основных компонентов
    robot = Robot(x=0, y=0, theta=math.pi / 2)
    command_queue = CommandQueue()

    # 2. Создание потокобезопасной очереди для команд от ZMQ
    zmq_command_queue = queue.Queue()

    # 3. Настройка и запуск визуализатора
    visualizer = RobotVisualizer(robot, command_queue)

    # Добавление препятствий для демонстрации
    visualizer.add_obstacle(2, 2, 1, 1)
    visualizer.add_obstacle(-3, 1, 0.5, 2)
    visualizer.add_obstacle(0, -2.5, 3, 0.5)
    visualizer.add_obstacle(2.5, -1, 1, 3)

    # 4. Запуск ZMQ клиента в отдельном потоке
    zmq_thread = threading.Thread(target=zmq_client_thread, args=(zmq_command_queue,), daemon=True)
    zmq_thread.start()

    # 5. Функция обратного вызова для обработки команд из всех источников
    def process_all_commands():
        # Обработка команд из ZMQ
        while not zmq_command_queue.empty():
            command = zmq_command_queue.get()
            command_queue.add_command(command)

        # Обновление очереди команд робота
        command_queue.update(robot)

    # 6. Запуск главного цикла симуляции
    visualizer.start(process_all_commands)


if __name__ == "__main__":
    main()
