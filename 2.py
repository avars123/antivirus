import tkinter as tk
import tkinter.ttk as ttk
import threading
import time
import random

# ------- Пытаемся подключить psutil (не обязателен) -------
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


# ---------------------------------
# ДАННЫЕ ДЛЯ ПРИЛОЖЕНИЯ
# ---------------------------------

DASHBOARD_THREATS = [
    ("Malware.Generic.2024", "Высокий", "2 мин назад", "Карантин"),
    ("Adware.Installer", "Средний", "1 час назад", "Удалено"),
    ("Trojan.Email.Spam", "Высокий", "30 мин назад", "Удалено"),
]

QUARANTINE_ITEMS = [
    ("virus1.exe", "Malware.Generic.2024", "C:/Users/Admin/Downloads", "2.4 MB", "Высокий"),
    ("installer_ad.exe", "Adware.Installer", "C:/Temp", "5.8 MB", "Средний"),
    ("mail_scr.scr", "Trojan.Email.Spam", "C:/Users/Admin/Documents", "1.2 MB", "Высокий"),
]

SETTINGS_DATA = {
    "Защита в реальном времени": True,
    "Облачная защита": True,
    "Поведенческий анализ": True,
    "Игровой режим": False,
    "Обновления": True,
    "Отчёты о системе": False,
}


# ---------------------------------
# ОСНОВНОЕ ОКНО
# ---------------------------------

class AntivirusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Antivirus Pro — Tkinter Edition")
        self.geometry("1000x650")
        self.resizable(False, False)
        self.configure(bg="#0f0f0f")

        # --------- Боковое меню ----------
        self.sidebar = tk.Frame(self, bg="#1a1a1a", width=200)
        self.sidebar.pack(side="left", fill="y")

        tk.Label(
            self.sidebar, text="Antivirus Pro",
            fg="white", bg="#1a1a1a",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=15)

        # кнопки бокового меню
        menu_items = [
            ("Панель", self.show_dashboard),
            ("Сканер", self.show_scanner),
            ("Карантин", self.show_quarantine),
            ("Настройки", self.show_settings),
        ]

        for text, cmd in menu_items:
            tk.Button(
                self.sidebar,
                text=text,
                command=cmd,
                bg="#2b2b2b",
                fg="white",
                font=("Segoe UI", 12),
                activebackground="#444",
                activeforeground="white",
                relief="flat",
                padx=10,
                pady=8
            ).pack(fill="x", padx=15, pady=5)

        # ---------- Основная область ----------
        self.main_area = tk.Frame(self, bg="#0f0f0f")
        self.main_area.pack(side="right", fill="both", expand=True)

        self.current_frame = None
        self.show_dashboard()

    # ------------------------------
    # Смена страниц
    # ------------------------------

    def switch_page(self, page):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = page(self.main_area)
        self.current_frame.pack(fill="both", expand=True)

    def show_dashboard(self):
        self.switch_page(DashboardPage)

    def show_scanner(self):
        self.switch_page(ScannerPage)

    def show_quarantine(self):
        self.switch_page(QuarantinePage)

    def show_settings(self):
        self.switch_page(SettingsPage)


# ---------------------------------
# 1. Панель
# ---------------------------------

class DashboardPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#0f0f0f")

        tk.Label(self, text="Панель управления", bg="#0f0f0f", fg="white",
                 font=("Segoe UI", 22, "bold")).pack(pady=15)

        # CPU & RAM
        if HAS_PSUTIL:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
        else:
            cpu = 41
            ram = 63

        tk.Label(self, text=f"CPU: {cpu}%   |   RAM: {ram}%",
                 fg="#bbbbbb", bg="#0f0f0f", font=("Segoe UI", 13)).pack(pady=5)

        # таблица угроз
        table = ttk.Treeview(self, columns=("t1", "t2", "t3", "t4"), show="headings", height=18)
        for col, name in zip(table["columns"], ["Угроза", "Уровень", "Обнаружено", "Статус"]):
            table.heading(col, text=name)

        for item in DASHBOARD_THREATS:
            table.insert("", "end", values=item)

        table.pack(expand=True, fill="both", padx=20, pady=20)


# ---------------------------------
# 2. Сканер
# ---------------------------------

class ScannerPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#0f0f0f")

        tk.Label(self, text="Сканер системы", bg="#0f0f0f", fg="white",
                 font=("Segoe UI", 22, "bold")).pack(pady=15)

        self.start_btn = tk.Button(
            self, text="Запустить сканирование", bg="#306dff", fg="white",
            font=("Segoe UI", 13), relief="flat", padx=20, pady=10,
            command=self.start_scan
        )
        self.start_btn.pack(pady=10)

        self.progress = ttk.Progressbar(self, length=700)
        self.progress.pack(pady=10)

        self.log = tk.Text(self, bg="#181818", fg="white", height=18)
        self.log.pack(padx=20, pady=20, fill="both", expand=True)

    # Фейковое сканирование
    def start_scan(self):
        self.start_btn.config(state="disabled")
        t = threading.Thread(target=self.scan_process)
        t.start()

    def scan_process(self):
        self.progress["value"] = 0
        self.log.delete("1.0", "end")

        for i in range(101):
            time.sleep(0.05)
            self.progress["value"] = i

            if i % 17 == 0 and i > 3:
                threat = random.choice(DASHBOARD_THREATS)[0]
                self.log.insert("end", f"⚠ Найдена угроза: {threat}\n")

            self.update_idletasks()

        self.log.insert("end", "\nСканирование завершено!\n")
        self.start_btn.config(state="normal")


# ---------------------------------
# 3. Карантин
# ---------------------------------

class QuarantinePage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#0f0f0f")

        tk.Label(self, text="Карантин", bg="#0f0f0f", fg="white",
                 font=("Segoe UI", 22, "bold")).pack(pady=15)

        table = ttk.Treeview(
            self,
            columns=("f", "t", "p", "s", "r"),
            show="headings",
            height=18
        )

        headers = ["Файл", "Угроза", "Путь", "Размер", "Риск"]
        for col, name in zip(table["columns"], headers):
            table.heading(col, text=name)

        for item in QUARANTINE_ITEMS:
            table.insert("", "end", values=item)

        table.pack(expand=True, fill="both", padx=20, pady=20)


# ---------------------------------
# 4. Настройки
# ---------------------------------

class SettingsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#0f0f0f")

        tk.Label(self, text="Настройки", bg="#0f0f0f", fg="white",
                 font=("Segoe UI", 22, "bold")).pack(pady=15)

        for key, val in SETTINGS_DATA.items():
            var = tk.BooleanVar(value=val)
            chk = tk.Checkbutton(
                self, text=key, variable=var,
                bg="#0f0f0f", fg="white",
                activebackground="#0f0f0f",
                selectcolor="#202020",
                font=("Segoe UI", 12)
            )
            chk.pack(anchor="w", padx=30, pady=5)


# ---------------------------------
# ЗАПУСК ПРИЛОЖЕНИЯ
# ---------------------------------

if __name__ == "__main__":
    app = AntivirusApp()
    app.mainloop()
