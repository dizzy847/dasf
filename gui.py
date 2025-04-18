import tkinter as tk
from tkinter import ttk, messagebox
import math
import time


class RobotARM_IMR165_GUI:
    def __init__(self, master):
        self.master = master
        master.title("Управление роботом ARM-IMR-165")
        master.geometry("1000x700")

        # Стиль
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))

        # Основные фреймы
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Панель управления
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Управление манипулятором", padding=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Панель визуализации
        self.visual_frame = ttk.LabelFrame(self.main_frame, text="Визуализация", padding=10)
        self.visual_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Холст для визуализации робота
        self.canvas = tk.Canvas(self.visual_frame, bg='white', width=400, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Параметры робота
        self.joint_angles = [0, 0, 0, 0, 0]  # 5 степеней свободы
        self.gripper_state = False  # Открыт/закрыт

        # Создание элементов управления
        self.create_joint_controls()
        self.create_gripper_control()
        self.create_utility_buttons()
        self.create_status_bar()

        # Инициализация визуализации
        self.draw_robot()

    def create_joint_controls(self):
        """Создаем элементы управления для каждого сустава"""
        joints = ["Основание", "Плечо", "Локоть", "Запястье", "Поворот захвата"]

        for i, joint in enumerate(joints):
            frame = ttk.Frame(self.control_frame)
            frame.pack(fill=tk.X, pady=5)

            label = ttk.Label(frame, text=f"{joint}:")
            label.pack(side=tk.LEFT, padx=5)

            scale = ttk.Scale(frame, from_=-180, to=180, value=0,
                              command=lambda val, idx=i: self.update_joint_angle(val, idx))
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            value_label = ttk.Label(frame, text="0°", width=5)
            value_label.pack(side=tk.LEFT, padx=5)

            # Сохраняем ссылки на элементы
            setattr(self, f"joint_{i}_scale", scale)
            setattr(self, f"joint_{i}_label", value_label)

    def create_gripper_control(self):
        """Создаем элементы управления захватом"""
        frame = ttk.Frame(self.control_frame)
        frame.pack(fill=tk.X, pady=10)

        self.gripper_label = ttk.Label(frame, text="Захват: Открыт")
        self.gripper_label.pack(side=tk.LEFT, padx=5)

        self.gripper_btn = ttk.Button(frame, text="Закрыть", command=self.toggle_gripper)
        self.gripper_btn.pack(side=tk.RIGHT, padx=5)

    def create_utility_buttons(self):
        """Создаем служебные кнопки"""
        frame = ttk.Frame(self.control_frame)
        frame.pack(fill=tk.X, pady=10)

        ttk.Button(frame, text="Домой", command=self.home_position).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(frame, text="Сброс", command=self.reset_robot).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(frame, text="Сохранить", command=self.save_position).pack(side=tk.LEFT, fill=tk.X, expand=True,
                                                                             padx=5)

        # Кнопка аварийной остановки
        emergency_frame = ttk.Frame(self.control_frame)
        emergency_frame.pack(fill=tk.X, pady=10)

        self.emergency_btn = ttk.Button(emergency_frame, text="АВАРИЙНАЯ ОСТАНОВКА",
                                        style='Emergency.TButton', command=self.emergency_stop)
        self.emergency_btn.pack(fill=tk.X, expand=True)
        self.style.configure('Emergency.TButton', foreground='white', background='red', font=('Arial', 12, 'bold'))

    def create_status_bar(self):
        """Создаем строку состояния"""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(self.status_frame, text="Готов к работе", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, ipady=5)

    def update_joint_angle(self, value, joint_idx):
        """Обновляем угол сустава"""
        angle = round(float(value))
        self.joint_angles[joint_idx] = angle
        getattr(self, f"joint_{joint_idx}_label").config(text=f"{angle}°")
        self.draw_robot()
        self.update_status(f"Сустав {joint_idx + 1} установлен на {angle}°")

    def toggle_gripper(self):
        """Переключаем состояние захвата"""
        self.gripper_state = not self.gripper_state
        state = "Закрыт" if self.gripper_state else "Открыт"
        self.gripper_label.config(text=f"Захват: {state}")
        self.gripper_btn.config(text="Открыть" if self.gripper_state else "Закрыть")
        self.draw_robot()
        self.update_status(f"Захват {state.lower()}")

    def home_position(self):
        """Возвращаем робота в домашнее положение"""
        for i in range(5):
            getattr(self, f"joint_{i}_scale").set(0)
            self.joint_angles[i] = 0
            getattr(self, f"joint_{i}_label").config(text="0°")

        if self.gripper_state:
            self.toggle_gripper()

        self.draw_robot()
        self.update_status("Робот в домашнем положении")

    def reset_robot(self):
        """Сбрасываем робота"""
        if messagebox.askyesno("Сброс", "Вы уверены, что хотите сбросить робота?"):
            self.home_position()
            self.update_status("Робот сброшен")

    def save_position(self):
        """Сохраняем текущее положение"""
        # В реальном приложении здесь была бы логика сохранения
        self.update_status("Положение сохранено")

    def emergency_stop(self):
        """Аварийная остановка"""
        self.home_position()
        self.update_status("АВАРИЙНАЯ ОСТАНОВКА!", "red")
        self.master.bell()
        messagebox.showerror("Аварийная остановка", "Робот остановлен в аварийном режиме!")

    def update_status(self, message, color="black"):
        """Обновляем строку состояния"""
        self.status_label.config(text=message, foreground=color)

    def draw_robot(self):
        """Рисуем робота на холсте"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Параметры робота
        base_radius = 50
        link_lengths = [80, 120, 80, 40]

        # Начинаем рисовать с основания
        x0, y0 = width // 2, height - 50
        self.canvas.create_oval(x0 - base_radius, y0 - 20,
                                x0 + base_radius, y0 + 20, fill="gray", outline="black")

        # Рисуем манипулятор
        angles = [math.radians(a) for a in self.joint_angles]

        # Сустав 1 (поворот основания)
        x1 = x0 + base_radius * math.cos(angles[0])
        y1 = y0 - base_radius * math.sin(angles[0])
        self.canvas.create_line(x0, y0, x1, y1, width=10, fill="blue")

        # Сустав 2 (плечо)
        x2 = x1 + link_lengths[0] * math.cos(angles[0] + angles[1])
        y2 = y1 - link_lengths[0] * math.sin(angles[0] + angles[1])
        self.canvas.create_line(x1, y1, x2, y2, width=8, fill="green")

        # Сустав 3 (локоть)
        x3 = x2 + link_lengths[1] * math.cos(angles[0] + angles[1] + angles[2])
        y3 = y2 - link_lengths[1] * math.sin(angles[0] + angles[1] + angles[2])
        self.canvas.create_line(x2, y2, x3, y3, width=6, fill="blue")

        # Сустав 4 (запястье)
        x4 = x3 + link_lengths[2] * math.cos(sum(angles[:4]))
        y4 = y3 - link_lengths[2] * math.sin(sum(angles[:4]))
        self.canvas.create_line(x3, y3, x4, y4, width=4, fill="green")

        # Захват
        gripper_width = 30 if self.gripper_state else 60
        angle = sum(angles[:5])

        # Левая часть захвата
        x5_left = x4 + gripper_width * math.cos(angle + math.pi / 2)
        y5_left = y4 - gripper_width * math.sin(angle + math.pi / 2)
        self.canvas.create_line(x4, y4, x5_left, y5_left, width=3, fill="red")

        # Правая часть захвата
        x5_right = x4 + gripper_width * math.cos(angle - math.pi / 2)
        y5_right = y4 - gripper_width * math.sin(angle - math.pi / 2)
        self.canvas.create_line(x4, y4, x5_right, y5_right, width=3, fill="red")

        # Подпись текущих координат
        self.canvas.create_text(width // 2, 20,
                                text=f"Координаты: X={int(x4)}, Y={int(y4)}",
                                font=('Arial', 10))


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = RobotARM_IMR165_GUI(root)
    root.mainloop()