import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import logging
import threading
import queue
from logging.handlers import RotatingFileHandler


class RobotControlSystem:
    """Класс для управления роботом и обработки данных"""

    def __init__(self):
        # Инициализация состояния системы
        self.motor_states = {
            'base': {'temp': 25.0, 'position_deg': 0.0, 'position_rad': 0.0, 'ticks': 0},
            'shoulder': {'temp': 25.0, 'position_deg': 0.0, 'position_rad': 0.0, 'ticks': 0},
            'elbow': {'temp': 25.0, 'position_deg': 0.0, 'position_rad': 0.0, 'ticks': 0},
            'wrist': {'temp': 25.0, 'position_deg': 0.0, 'position_rad': 0.0, 'ticks': 0},
            'gripper': {'temp': 25.0, 'position_deg': 0.0, 'position_rad': 0.0, 'ticks': 0}
        }
        self.system_status = "DISCONNECTED"
        self.log_queue = queue.Queue()
        self.setup_logging()
        self.safety_status = "OK"
        self.target_position = (0, 0)
        self.current_speed = 1.0

    def setup_logging(self):
        """Настройка системы логирования"""
        self.logger = logging.getLogger('RobotLogger')
        self.logger.setLevel(logging.INFO)

        # Основной лог
        main_handler = RotatingFileHandler(
            'robot_operations.log',
            maxBytes=1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))

        # Лог аварийных ситуаций
        critical_handler = logging.FileHandler(
            'critical_events.log',
            encoding='utf-8'
        )
        critical_handler.setLevel(logging.CRITICAL)

        self.logger.addHandler(main_handler)
        self.logger.addHandler(critical_handler)


class RobotGUI(tk.Tk):
    """Главный класс графического интерфейса"""

    def __init__(self, control_system):
        super().__init__()
        self.control_system = control_system
        self.title("Управление роботизированной ячейкой IMR-165")
        self.geometry("1280x800")
        self.configure_styles()
        self.create_widgets()
        self.setup_threads()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def configure_styles(self):
        """Настройка стилей элементов"""
        self.style = ttk.Style()
        self.style.configure('Emergency.TButton', foreground='white', background='red')
        self.style.configure('StatusIndicator.TLabel', font=('Arial', 12, 'bold'))
        self.style.map('StatusIndicator.TLabel',
                       background=[('active', 'green'), ('disabled', 'gray')])

    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Основные контейнеры
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Панель управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Панель состояния
        status_frame = ttk.LabelFrame(main_frame, text="Состояние системы", padding=10)
        status_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Инициализация компонентов
        self.create_control_panel(control_frame)
        self.create_status_panel(status_frame)
        self.create_visualization()
        self.create_log_panel()

    def create_control_panel(self, parent):
        """Панель управления"""
        # Кнопки управления
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Вкл", command=self.power_on).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Выкл", command=self.power_off).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Пауза", command=self.pause).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Аварийный стоп",
                   style='Emergency.TButton', command=self.emergency_stop).pack(side=tk.RIGHT, padx=2)

        # Управление скоростью
        ttk.Label(parent, text="Скорость перемещения:").pack(anchor=tk.W)
        self.speed_var = tk.DoubleVar(value=0.5)
        self.speed_scale = ttk.Scale(parent, from_=0.1, to=1.0, variable=self.speed_var)
        self.speed_scale.pack(fill=tk.X)

        # Обновление скорости в control_system
        self.speed_var.trace_add('write', lambda *args: self.update_speed())

    def create_status_panel(self, parent):
        """Панель состояния системы"""
        # Индикаторы моторов
        motor_frame = ttk.LabelFrame(parent, text="Состояние моторов", padding=10)
        motor_frame.pack(fill=tk.BOTH, expand=True)

        self.motor_indicators = {}
        for motor in ['base', 'shoulder', 'elbow', 'wrist', 'gripper']:
            frame = ttk.Frame(motor_frame)
            frame.pack(fill=tk.X, pady=2)

            ttk.Label(frame, text=motor.capitalize(), width=12).pack(side=tk.LEFT)
            self.motor_indicators[motor] = {
                'temp': ttk.Label(frame, text="25.0°C", width=8),
                'deg': ttk.Label(frame, text="0.00°", width=8),
                'rad': ttk.Label(frame, text="0.00 рад", width=10),
                'ticks': ttk.Label(frame, text="0 тик", width=8)
            }
            for metric in self.motor_indicators[motor].values():
                metric.pack(side=tk.LEFT, padx=2)

        # Индикатор состояния системы
        self.system_status_indicator = ttk.Label(
            parent,
            text="ВЫКЛЮЧЕН",
            style='StatusIndicator.TLabel',
            background='gray',
            anchor=tk.CENTER
        )
        self.system_status_indicator.pack(fill=tk.X, pady=5)

    def create_visualization(self):
        """Визуализация робота и рабочей зоны"""
        self.canvas = tk.Canvas(self, bg='white', width=600, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Отрисовка рабочей зоны
        self.canvas.create_rectangle(100, 300, 500, 500, outline='blue', dash=(4, 2), tag="work_area")
        self.canvas.create_text(300, 280, text="Рабочая зона", fill='blue')

    def create_log_panel(self):
        """Панель журналирования событий"""
        log_frame = ttk.LabelFrame(self, text="Журнал событий", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            height=8,
            font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

    def setup_threads(self):
        """Настройка фоновых потоков"""
        self.running = True
        self.after(100, self.update_system_status)

    def update_system_status(self):
        """Обновление состояния системы в реальном времени"""
        if self.running:
            try:
                # Обновление данных моторов
                for motor, indicators in self.motor_indicators.items():
                    state = self.control_system.motor_states[motor]
                    indicators['temp'].config(text=f"{state['temp']:.1f}°C")
                    indicators['deg'].config(text=f"{state['position_deg']:.2f}°")
                    indicators['rad'].config(text=f"{state['position_rad']:.2f} рад")
                    indicators['ticks'].config(text=f"{state['ticks']}")

                # Обновление логов
                while not self.control_system.log_queue.empty():
                    log = self.control_system.log_queue.get()
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.insert(tk.END, log + "\n")
                    self.log_text.config(state=tk.DISABLED)
                    self.log_text.see(tk.END)

            except Exception as e:
                self.control_system.logger.error(f"Ошибка обновления: {str(e)}")

            # Планируем следующее обновление через 100 мс
            self.after(100, self.update_system_status)

    def power_on(self):
        """Включение системы"""
        self.control_system.system_status = "CONNECTED"
        self.system_status_indicator.config(text="ВКЛЮЧЕН", background='green')
        self.control_system.log_queue.put("Система включена.")

    def power_off(self):
        """Выключение системы"""
        self.control_system.system_status = "DISCONNECTED"
        self.system_status_indicator.config(text="ВЫКЛЮЧЕН", background='gray')
        self.control_system.log_queue.put("Система выключена.")

    def pause(self):
        """Пауза системы"""
        self.control_system.system_status = "PAUSED"
        self.system_status_indicator.config(text="ПАУЗА", background='yellow')
        self.control_system.log_queue.put("Система на паузе.")

    def emergency_stop(self):
        """Аварийная остановка"""
        self.control_system.system_status = "EMERGENCY_STOP"
        self.system_status_indicator.config(text="АВАРИЯ", background='red')
        self.control_system.log_queue.put("Аварийная остановка активирована!")

    def update_speed(self):
        """Обновление скорости перемещения"""
        self.control_system.current_speed = self.speed_var.get()
        self.control_system.log_queue.put(f"Скорость изменена: {self.control_system.current_speed:.2f}")

    def on_close(self):
        """Обработка закрытия окна"""
        self.running = False
        self.destroy()


if __name__ == "__main__":
    control_system = RobotControlSystem()
    app = RobotGUI(control_system)
    app.mainloop()