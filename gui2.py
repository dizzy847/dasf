import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import time
import json
import threading
import cv2
import numpy as np
from PIL import Image, ImageTk
import docker
import git
import rospy
from geometry_msgs.msg import Twist
import torch
import tensorflow as tf


class CollaborativeRobotGUI:
    def __init__(self, master):
        self.master = master
        master.title("ARM-IMR-165: Коллаборативная система управления")
        master.geometry("1200x800")

        # ROS инициализация
        try:
            rospy.init_node('robot_gui_node', anonymous=True)
            self.cmd_vel_pub = rospy.Publisher('/arm_imr165/cmd_vel', Twist, queue_size=10)
        except:
            print("ROS не обнаружен, работаем в автономном режиме")

        # Стили
        self.setup_styles()

        # Основные фреймы
        self.setup_main_frames()

        # Компоненты интерфейса
        self.setup_robot_control()
        self.setup_vision_system()
        self.setup_ai_integration()
        self.setup_documentation()
        self.setup_status_bar()

        # Инициализация систем
        self.init_robot_state()
        self.init_vision_system()
        self.load_documentation()

        # Тестовые данные
        self.test_objects = ["Деталь A", "Деталь B", "Деталь C", "Деталь D", "Деталь E"]

        # Docker клиент
        self.docker_client = docker.from_env()

    def setup_styles(self):
        """Настройка стилей интерфейса"""
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Emergency.TButton', foreground='white', background='red', font=('Arial', 12, 'bold'))
        self.style.configure('Warning.TLabel', foreground='red', font=('Arial', 10, 'bold'))
        self.style.configure('Success.TLabel', foreground='green', font=('Arial', 10, 'bold'))

    def setup_main_frames(self):
        """Настройка основных фреймов интерфейса"""
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - управление роботом
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Управление роботом", padding=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Центральная панель - техническое зрение
        self.vision_frame = ttk.LabelFrame(self.main_frame, text="Система технического зрения", padding=10)
        self.vision_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Правая панель - AI и документация
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.ai_frame = ttk.LabelFrame(self.right_frame, text="Интеграция ИИ", padding=10)
        self.ai_frame.pack(fill=tk.BOTH, expand=True)

        self.doc_frame = ttk.LabelFrame(self.right_frame, text="Документация", padding=10)
        self.doc_frame.pack(fill=tk.BOTH, expand=True)

    def setup_robot_control(self):
        """Настройка панели управления роботом"""
        # Вкладки для разных режимов управления
        self.control_notebook = ttk.Notebook(self.control_frame)
        self.control_notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка ручного управления
        self.manual_tab = ttk.Frame(self.control_notebook)
        self.control_notebook.add(self.manual_tab, text="Ручное управление")
        self.setup_manual_control()

        # Вкладка автоматического управления
        self.auto_tab = ttk.Frame(self.control_notebook)
        self.control_notebook.add(self.auto_tab, text="Автоматическое управление")
        self.setup_auto_control()

        # Вкладка программирования
        self.prog_tab = ttk.Frame(self.control_notebook)
        self.control_notebook.add(self.prog_tab, text="Программирование")
        self.setup_programming()

        # Панель безопасности
        self.setup_safety_panel()

    def setup_manual_control(self):
        """Настройка ручного управления"""
        # Управление суставами
        joints = ["Основание", "Плечо", "Локоть", "Запястье", "Поворот"]
        self.joint_vars = []

        for i, joint in enumerate(joints):
            frame = ttk.Frame(self.manual_tab)
            frame.pack(fill=tk.X, pady=2)

            ttk.Label(frame, text=f"{joint}:").pack(side=tk.LEFT, padx=5)

            var = tk.DoubleVar(value=0)
            scale = ttk.Scale(frame, from_=-180, to=180, variable=var,
                              command=lambda v, idx=i: self.update_joint(v, idx))
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            label = ttk.Label(frame, text="0°", width=5)
            label.pack(side=tk.LEFT, padx=5)

            self.joint_vars.append((var, label))

        # Управление захватом
        grip_frame = ttk.Frame(self.manual_tab)
        grip_frame.pack(fill=tk.X, pady=10)

        self.gripper_state = False
        self.gripper_btn = ttk.Button(grip_frame, text="Закрыть захват",
                                      command=self.toggle_gripper)
        self.gripper_btn.pack(side=tk.LEFT, expand=True)

        # Координатное управление
        coord_frame = ttk.LabelFrame(self.manual_tab, text="Декартовы координаты")
        coord_frame.pack(fill=tk.BOTH, pady=5)

        coords = ["X", "Y", "Z", "RX", "RY", "RZ"]
        self.coord_entries = []

        for i in range(0, 6, 3):
            row_frame = ttk.Frame(coord_frame)
            row_frame.pack(fill=tk.X, pady=2)

            for j in range(3):
                if i + j >= 6:
                    break

                frame = ttk.Frame(row_frame)
                frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

                ttk.Label(frame, text=f"{coords[i + j]}:").pack(side=tk.LEFT)

                entry = ttk.Entry(frame, width=8)
                entry.pack(side=tk.LEFT, padx=2)
                self.coord_entries.append(entry)

        ttk.Button(coord_frame, text="Переместить",
                   command=self.move_to_coordinates).pack(pady=5)

    def setup_auto_control(self):
        """Настройка автоматического управления"""
        # Список программ
        prog_frame = ttk.Frame(self.auto_tab)
        prog_frame.pack(fill=tk.X, pady=5)

        ttk.Label(prog_frame, text="Программа:").pack(side=tk.LEFT)

        self.prog_combo = ttk.Combobox(prog_frame, values=["Захват детали", "Сортировка", "Упаковка"])
        self.prog_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.prog_combo.current(0)

        # Параметры программы
        param_frame = ttk.LabelFrame(self.auto_tab, text="Параметры")
        param_frame.pack(fill=tk.BOTH, pady=5)

        ttk.Label(param_frame, text="Объект:").grid(row=0, column=0, sticky=tk.W)
        self.obj_combo = ttk.Combobox(param_frame, values=self.test_objects)
        self.obj_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        self.obj_combo.current(0)

        ttk.Label(param_frame, text="Скорость:").grid(row=1, column=0, sticky=tk.W)
        self.speed_slider = ttk.Scale(param_frame, from_=10, to=100, value=50)
        self.speed_slider.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(param_frame, text="Точность:").grid(row=2, column=0, sticky=tk.W)
        self.precision_combo = ttk.Combobox(param_frame, values=["Высокая", "Средняя", "Низкая"])
        self.precision_combo.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        self.precision_combo.current(1)

        # Управление выполнением
        exec_frame = ttk.Frame(self.auto_tab)
        exec_frame.pack(fill=tk.X, pady=10)

        ttk.Button(exec_frame, text="Запуск", command=self.start_program).pack(side=tk.LEFT, expand=True)
        ttk.Button(exec_frame, text="Пауза", command=self.pause_program).pack(side=tk.LEFT, expand=True)
        ttk.Button(exec_frame, text="Стоп", command=self.stop_program).pack(side=tk.LEFT, expand=True)

    def setup_programming(self):
        """Настройка вкладки программирования"""
        # Редактор кода
        editor_frame = ttk.Frame(self.prog_tab)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        self.code_editor = tk.Text(editor_frame, wrap=tk.WORD, font=('Courier', 10))
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(editor_frame, command=self.code_editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_editor.config(yscrollcommand=scrollbar.set)

        # Панель управления редактором
        btn_frame = ttk.Frame(self.prog_tab)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Загрузить", command=self.load_program).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Сохранить", command=self.save_program).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Выполнить", command=self.execute_program).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Отладить", command=self.debug_program).pack(side=tk.LEFT)

    def setup_safety_panel(self):
        """Настройка панели безопасности"""
        safety_frame = ttk.Frame(self.control_frame)
        safety_frame.pack(fill=tk.X, pady=10)

        # Светофорная индикация
        self.traffic_light = tk.Canvas(safety_frame, width=60, height=20, bg='white')
        self.traffic_light.pack(side=tk.LEFT, padx=5)
        self.update_traffic_light('red')

        # Кнопка аварийной остановки
        self.emergency_btn = ttk.Button(safety_frame, text="АВАРИЙНАЯ ОСТАНОВКА",
                                        style='Emergency.TButton', command=self.emergency_stop)
        self.emergency_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Зоны безопасности
        zone_frame = ttk.Frame(self.control_frame)
        zone_frame.pack(fill=tk.X)

        ttk.Label(zone_frame, text="Зона безопасности:").pack(side=tk.LEFT)
        self.safety_zone_combo = ttk.Combobox(zone_frame, values=["Полная", "Ограниченная", "Выключена"])
        self.safety_zone_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.safety_zone_combo.current(0)
        self.safety_zone_combo.bind("<<ComboboxSelected>>", self.update_safety_zone)

    def setup_vision_system(self):
        """Настройка системы технического зрения"""
        # Вкладки для разных режимов зрения
        self.vision_notebook = ttk.Notebook(self.vision_frame)
        self.vision_notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка изображения с камеры
        self.camera_tab = ttk.Frame(self.vision_notebook)
        self.vision_notebook.add(self.camera_tab, text="Камера")
        self.setup_camera_view()

        # Вкладка обработки изображений
        self.processing_tab = ttk.Frame(self.vision_notebook)
        self.vision_notebook.add(self.processing_tab, text="Обработка")
        self.setup_image_processing()

        # Вкладка калибровки
        self.calibration_tab = ttk.Frame(self.vision_notebook)
        self.vision_notebook.add(self.calibration_tab, text="Калибровка")
        self.setup_calibration()

    def setup_camera_view(self):
        """Настройка просмотра с камеры"""
        self.camera_canvas = tk.Canvas(self.camera_tab, bg='black')
        self.camera_canvas.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(self.camera_tab)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Старт", command=self.start_camera).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Стоп", command=self.stop_camera).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Снимок", command=self.take_snapshot).pack(side=tk.LEFT)

        # Инициализация камеры
        self.camera_active = False
        self.camera_thread = None
        self.current_frame = None

    def setup_image_processing(self):
        """Настройка обработки изображений"""
        # Параметры обработки
        param_frame = ttk.Frame(self.processing_tab)
        param_frame.pack(fill=tk.X, pady=5)

        ttk.Label(param_frame, text="Режим:").pack(side=tk.LEFT)
        self.proc_mode = ttk.Combobox(param_frame, values=["Детекция", "Сегментация", "Классификация"])
        self.proc_mode.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.proc_mode.current(0)

        # Область изображения
        self.proc_canvas = tk.Canvas(self.processing_tab, bg='black')
        self.proc_canvas.pack(fill=tk.BOTH, expand=True)

        # Результаты обработки
        result_frame = ttk.Frame(self.processing_tab)
        result_frame.pack(fill=tk.X, pady=5)

        ttk.Label(result_frame, text="Результат:").pack(side=tk.LEFT)
        self.result_label = ttk.Label(result_frame, text="Не обработано", style='Warning.TLabel')
        self.result_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(result_frame, text="Обработать", command=self.process_image).pack(side=tk.RIGHT)

    def setup_calibration(self):
        """Настройка калибровки камеры"""
        calib_frame = ttk.Frame(self.calibration_tab)
        calib_frame.pack(fill=tk.BOTH, expand=True)

        # Шахматная доска для калибровки
        self.calib_canvas = tk.Canvas(calib_frame, bg='black')
        self.calib_canvas.pack(fill=tk.BOTH, expand=True)

        # Параметры калибровки
        param_frame = ttk.Frame(calib_frame)
        param_frame.pack(fill=tk.X, pady=5)

        ttk.Label(param_frame, text="Ширина:").grid(row=0, column=0, sticky=tk.W)
        self.calib_width = ttk.Entry(param_frame, width=5)
        self.calib_width.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.calib_width.insert(0, "9")

        ttk.Label(param_frame, text="Высота:").grid(row=0, column=2, sticky=tk.W)
        self.calib_height = ttk.Entry(param_frame, width=5)
        self.calib_height.grid(row=0, column=3, sticky=tk.W, padx=5)
        self.calib_height.insert(0, "6")

        ttk.Label(param_frame, text="Размер (мм):").grid(row=0, column=4, sticky=tk.W)
        self.calib_size = ttk.Entry(param_frame, width=5)
        self.calib_size.grid(row=0, column=5, sticky=tk.W, padx=5)
        self.calib_size.insert(0, "25")

        # Кнопки управления
        btn_frame = ttk.Frame(calib_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Начать калибровку", command=self.start_calibration).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Сохранить параметры", command=self.save_calibration).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Загрузить параметры", command=self.load_calibration).pack(side=tk.LEFT)

    def setup_ai_integration(self):
        """Настройка интеграции с ИИ"""
        # Вкладки для разных AI функций
        self.ai_notebook = ttk.Notebook(self.ai_frame)
        self.ai_notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка обучения модели
        self.training_tab = ttk.Frame(self.ai_notebook)
        self.ai_notebook.add(self.training_tab, text="Обучение")
        self.setup_model_training()

        # Вкладка работы модели
        self.inference_tab = ttk.Frame(self.ai_notebook)
        self.ai_notebook.add(self.inference_tab, text="Работа модели")
        self.setup_model_inference()

        # Вкладка развертывания
        self.deployment_tab = ttk.Frame(self.ai_notebook)
        self.ai_notebook.add(self.deployment_tab, text="Развертывание")
        self.setup_model_deployment()

    def setup_model_training(self):
        """Настройка обучения модели"""
        # Выбор модели
        model_frame = ttk.Frame(self.training_tab)
        model_frame.pack(fill=tk.X, pady=5)

        ttk.Label(model_frame, text="Модель:").pack(side=tk.LEFT)
        self.model_type = ttk.Combobox(model_frame, values=["YOLOv5", "EfficientNet", "ResNet", "Custom CNN"])
        self.model_type.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.model_type.current(0)

        # Параметры обучения
        param_frame = ttk.LabelFrame(self.training_tab, text="Параметры обучения")
        param_frame.pack(fill=tk.X, pady=5)

        ttk.Label(param_frame, text="Эпохи:").grid(row=0, column=0, sticky=tk.W)
        self.epochs = ttk.Entry(param_frame, width=5)
        self.epochs.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.epochs.insert(0, "10")

        ttk.Label(param_frame, text="Размер батча:").grid(row=0, column=2, sticky=tk.W)
        self.batch_size = ttk.Entry(param_frame, width=5)
        self.batch_size.grid(row=0, column=3, sticky=tk.W, padx=5)
        self.batch_size.insert(0, "16")

        ttk.Label(param_frame, text="Скорость обучения:").grid(row=1, column=0, sticky=tk.W)
        self.learning_rate = ttk.Entry(param_frame, width=8)
        self.learning_rate.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.learning_rate.insert(0, "0.001")

        ttk.Label(param_frame, text="Датасет:").grid(row=1, column=2, sticky=tk.W)
        self.dataset_path = ttk.Entry(param_frame)
        self.dataset_path.grid(row=1, column=3, sticky=tk.EW, padx=5)
        ttk.Button(param_frame, text="Обзор", command=self.browse_dataset).grid(row=1, column=4, padx=5)

        # Прогресс обучения
        self.train_progress = ttk.Progressbar(self.training_tab, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.train_progress.pack(fill=tk.X, pady=5)

        self.train_status = ttk.Label(self.training_tab, text="Готов к обучению")
        self.train_status.pack(fill=tk.X)

        # Кнопки управления
        btn_frame = ttk.Frame(self.training_tab)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Начать обучение", command=self.start_training).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Остановить", command=self.stop_training).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Сохранить модель", command=self.save_model).pack(side=tk.LEFT)

    def setup_model_inference(self):
        """Настройка работы модели"""
        # Выбор модели
        model_frame = ttk.Frame(self.inference_tab)
        model_frame.pack(fill=tk.X, pady=5)

        ttk.Label(model_frame, text="Модель:").pack(side=tk.LEFT)
        self.inference_model = ttk.Combobox(model_frame, values=["YOLOv5", "EfficientNet", "ResNet", "Custom CNN"])
        self.inference_model.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.inference_model.current(0)

        ttk.Button(model_frame, text="Загрузить", command=self.load_model).pack(side=tk.LEFT, padx=5)

        # Область вывода
        self.inference_canvas = tk.Canvas(self.inference_tab, bg='black')
        self.inference_canvas.pack(fill=tk.BOTH, expand=True)

        # Результаты
        result_frame = ttk.Frame(self.inference_tab)
        result_frame.pack(fill=tk.X, pady=5)

        ttk.Label(result_frame, text="Результат:").pack(side=tk.LEFT)
        self.inference_result = ttk.Label(result_frame, text="Модель не загружена", style='Warning.TLabel')
        self.inference_result.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(result_frame, text="Выполнить", command=self.run_inference).pack(side=tk.RIGHT)

    def setup_model_deployment(self):
        """Настройка развертывания модели"""
        # Контейнеризация
        docker_frame = ttk.LabelFrame(self.deployment_tab, text="Docker контейнер")
        docker_frame.pack(fill=tk.X, pady=5)

        ttk.Label(docker_frame, text="Образ:").grid(row=0, column=0, sticky=tk.W)
        self.docker_image = ttk.Entry(docker_frame)
        self.docker_image.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.docker_image.insert(0, "arm-imr165-ai:latest")

        ttk.Label(docker_frame, text="Порт:").grid(row=0, column=2, sticky=tk.W)
        self.docker_port = ttk.Entry(docker_frame, width=6)
        self.docker_port.grid(row=0, column=3, sticky=tk.W, padx=5)
        self.docker_port.insert(0, "5000")

        btn_frame = ttk.Frame(docker_frame)
        btn_frame.grid(row=1, column=0, columnspan=4, sticky=tk.EW, pady=5)

        ttk.Button(btn_frame, text="Собрать", command=self.build_docker).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Запустить", command=self.run_docker).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Остановить", command=self.stop_docker).pack(side=tk.LEFT)

        # Логи контейнера
        log_frame = ttk.Frame(self.deployment_tab)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.docker_logs = tk.Text(log_frame, wrap=tk.WORD, height=10)
        self.docker_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_frame, command=self.docker_logs.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.docker_logs.config(yscrollcommand=scrollbar.set)

    def setup_documentation(self):
        """Настройка панели документации"""
        # Документация API
        api_frame = ttk.LabelFrame(self.doc_frame, text="API документация")
        api_frame.pack(fill=tk.BOTH, expand=True)

        self.api_docs = tk.Text(api_frame, wrap=tk.WORD)
        self.api_docs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(api_frame, command=self.api_docs.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.api_docs.config(yscrollcommand=scrollbar.set)

        # Управление версиями
        git_frame = ttk.Frame(self.doc_frame)
        git_frame.pack(fill=tk.X, pady=5)

        ttk.Button(git_frame, text="Commit", command=self.git_commit).pack(side=tk.LEFT)
        ttk.Button(git_frame, text="Push", command=self.git_push).pack(side=tk.LEFT)
        ttk.Button(git_frame, text="Pull", command=self.git_pull).pack(side=tk.LEFT)

        self.git_status = ttk.Label(git_frame, text="Репозиторий не инициализирован")
        self.git_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def setup_status_bar(self):
        """Настройка строки состояния"""
        self.status_frame = ttk.Frame(self.master)
        self.status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_var = tk.StringVar(value="Система готова к работе")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var,
                                      relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, ipady=5)

        # Индикатор ROS
        self.ros_indicator = tk.Canvas(self.status_frame, width=20, height=20, bg='red')
        self.ros_indicator.pack(side=tk.RIGHT, padx=5)

        # Индикатор Docker
        self.docker_indicator = tk.Canvas(self.status_frame, width=20, height=20, bg='red')
        self.docker_indicator.pack(side=tk.RIGHT, padx=5)

    def init_robot_state(self):
        """Инициализация состояния робота"""
        self.robot_connected = False
        self.emergency_stop_flag = False
        self.current_position = [0, 0, 0, 0, 0, 0]  # X, Y, Z, RX, RY, RZ
        self.target_position = [0, 0, 0, 0, 0, 0]
        self.joint_angles = [0, 0, 0, 0, 0]  # 5 суставов
        self.gripper_state = False  # Открыт

        # Подключение к роботу
        self.connect_to_robot()

    def init_vision_system(self):
        """Инициализация системы технического зрения"""
        self.camera = None
        self.calibration_params = None
        self.processing_params = {
            'threshold': 128,
            'blur': 5,
            'contour_color': (0, 255, 0)
        }

    def load_documentation(self):
        """Загрузка документации"""
        # Загрузка API документации
        api_docs = """=== API управления роботом ARM-IMR-165 ===

1. Подключение:
   - connect(ip: str, port: int) -> bool
   - disconnect() -> None

2. Управление движением:
   - move_joint(joint: int, angle: float) -> bool
   - move_linear(x: float, y: float, z: float) -> bool
   - move_circular(pose1: list, pose2: list) -> bool

3. Управление захватом:
   - set_gripper(state: bool) -> bool
   - get_gripper() -> bool

4. Получение состояния:
   - get_position() -> list
   - get_joint_angles() -> list
   - get_status() -> dict
"""
        self.api_docs.insert(tk.END, api_docs)

    def update_status(self, message, color="black"):
        """Обновление строки состояния"""
        self.status_var.set(message)
        self.status_label.config(foreground=color)

    def update_traffic_light(self, color):
        """Обновление светофора"""
        colors = {'red': '#ff0000', 'yellow': '#ffff00', 'green': '#00ff00'}
        self.traffic_light.delete("all")
        self.traffic_light.create_oval(10, 5, 50, 15, fill=colors.get(color, 'white'), outline='black')

    # ===== Методы управления роботом =====
    def connect_to_robot(self):
        """Подключение к роботу"""
        try:
            # Здесь должна быть реальная логика подключения
            self.robot_connected = True
            self.update_status("Подключено к роботу ARM-IMR-165", "green")
            self.update_traffic_light('green')
            self.draw_robot()
        except Exception as e:
            self.robot_connected = False
            self.update_status(f"Ошибка подключения: {str(e)}", "red")
            self.update_traffic_light('red')

    def update_joint(self, value, joint_idx):
        """Обновление угла сустава"""
        angle = round(float(value))
        self.joint_angles[joint_idx] = angle
        self.joint_vars[joint_idx][1].config(text=f"{angle}°")

        # Обновляем визуализацию
        self.draw_robot()

        # Отправляем команду роботу (если подключен)
        if self.robot_connected and not self.emergency_stop_flag:
            # В реальной системе здесь будет вызов API робота
            self.update_status(f"Сустав {joint_idx + 1} установлен на {angle}°")

    def toggle_gripper(self):
        """Переключение состояния захвата"""
        self.gripper_state = not self.gripper_state
        state = "Закрыт" if self.gripper_state else "Открыт"
        self.gripper_btn.config(text=f"{'Открыть' if self.gripper_state else 'Закрыть'} захват")

        # Обновляем визуализацию
        self.draw_robot()

        # Отправляем команду роботу
        if self.robot_connected and not self.emergency_stop_flag:
            # В реальной системе здесь будет вызов API робота
            self.update_status(f"Захват {state.lower()}")

    def move_to_coordinates(self):
        """Перемещение в заданные координаты"""
        try:
            # Получаем координаты из полей ввода
            coords = []
            for entry in self.coord_entries:
                coords.append(float(entry.get()))

            self.target_position = coords.copy()

            # В реальной системе здесь будет вызов API робота
            if self.robot_connected and not self.emergency_stop_flag:
                self.update_status(f"Перемещение в X={coords[0]}, Y={coords[1]}, Z={coords[2]}")
                # Здесь должна быть логика расчета углов суставов через обратную кинематику

                # Визуализация движения
                self.animate_movement()
        except ValueError:
            self.update_status("Ошибка: неверные координаты", "red")

    def animate_movement(self):
        """Анимация движения робота к целевой позиции"""
        steps = 20
        delta = [(t - c) / steps for t, c in zip(self.target_position, self.current_position)]

        for _ in range(steps):
            if self.emergency_stop_flag:
                break

            self.current_position = [c + d for c, d in zip(self.current_position, delta)]
            # Здесь должна