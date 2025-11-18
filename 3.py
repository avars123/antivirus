import tkinter as tk
import tkinter.ttk as ttk
import threading
import time
import random

# === Попытаться подключить psutil (не обязательно) ===
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


# === Цвета (приближены к твоему дизайну Tailwind/OKLCH) ===
BG_GRADIENT_TOP = "#eff6ff"   # from-blue-50
BG_GRADIENT_MID = "#f5f3ff"   # via-purple-50
BG_GRADIENT_BOTTOM = "#fdf2ff"  # to-pink-50

SIDEBAR_BG = "#ffffffcc"      # белая «стеклянная» панель
SIDEBAR_BORDER = "#e5e7eb"
SIDEBAR_ACTIVE_BG = "#111827"
SIDEBAR_ACTIVE_FG = "#ffffff"
SIDEBAR_INACTIVE_FG = "#4b5563"

CARD_BG = "#ffffffff"
CARD_BORDER = "#e5e7eb"
CARD_HEADER_FG = "#030213"
CARD_SUBTEXT_FG = "#6b7280"

ACCENT_BLUE = "#2563eb"
ACCENT_GREEN = "#16a34a"
ACCENT_RED = "#dc2626"
ACCENT_AMBER = "#d97706"

TEXT_MUTED = "#6b7280"


# === Фейковые данные (как в макете) ===
DASHBOARD_THREATS = [
    ("Malware.Generic.2024", "Высокий", "2 мин назад", "Перемещено в карантин"),
    ("Adware.Bundle.Installer", "Средний", "1 час назад", "Удалено"),
    ("PUP.Optional.Toolbar", "Низкий", "3 часа назад", "Удалено"),
]

SCAN_HISTORY = [
    ("Быстрое сканирование", "Сегодня, 10:24", "2 мин", "0 угроз"),
    ("Полное сканирование", "Вчера, 21:10", "18 мин", "3 угрозы"),
    ("Сканирование папки", "Вчера, 14:02", "45 сек", "1 угроза"),
]

QUARANTINE_ITEMS = [
    ("suspicious_installer.exe", "Malware.Generic.2024", "C:/Users/Admin/Downloads", "2.4 MB", "Высокий"),
    ("crack_tool.exe", "PUP.Optional.Bundle", "C:/Games/Cracks", "5.8 MB", "Средний"),
    ("invoice_2025.scr", "Trojan.Mail.Spam", "C:/Users/Admin/Documents", "1.2 MB", "Высокий"),
]

SETTINGS_DATA = [
    ("Защита в реальном времени", True, "Постоянный мониторинг системы и файлов в фоне."),
    ("Облачная защита", True, "Обновляемые сигнатуры и онлайн-анализ угроз."),
    ("Поведенческий анализ", True, "Обнаружение аномального поведения приложений."),
    ("Игровой режим", False, "Минимум уведомлений во время игр и полноэкранных приложений."),
    ("Автообновления", True, "Автоматическая установка обновлений защитных баз."),
    ("Отчёты о системе", False, "Отправка анонимной статистики для улучшения продукта."),
]


# === Вспомогательный виджет: градиентный фон с «шарами» ===
class GradientBackground(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, highlightthickness=0, **kwargs)
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self.draw_gradient()

    def draw_gradient(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 0 or h <= 0:
            return

        # Простой вертикальный градиент (приближение)
        steps = 80
        for i in range(steps):
            ratio = i / max(steps - 1, 1)
            if ratio < 0.5:
                # от top к mid
                sub = ratio / 0.5
                color = self._mix_color(BG_GRADIENT_TOP, BG_GRADIENT_MID, sub)
            else:
                sub = (ratio - 0.5) / 0.5
                color = self._mix_color(BG_GRADIENT_MID, BG_GRADIENT_BOTTOM, sub)
            y1 = int(h * ratio)
            y2 = int(h * (ratio + 1 / steps))
            self.create_rectangle(0, y1, w, y2, outline="", fill=color)

        # «размытые шары» (просто большие овалы)
        self.create_oval(-150, -150, 250, 250, fill="#60a5fa33", outline="")
        self.create_oval(w - 350, h * 0.1, w + 50, h * 0.7, fill="#a855f733", outline="")
        self.create_oval(w * 0.2, h - 250, w * 0.8, h + 150, fill="#ec489933", outline="")

    @staticmethod
    def _mix_color(c1, c2, t):
        # c1, c2: "#rrggbb"
        t = max(0.0, min(1.0, t))
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"


# === Основное приложение ===
class AntivirusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Antivirus App Design — Tkinter")
        self.geometry("1120x720")
        self.minsize(980, 640)

        # Фон
        self.bg_canvas = GradientBackground(self)
        self.bg_canvas.pack(fill="both", expand=True)

        # «стеклянная» основная панель
        self.main_container = tk.Frame(self, bg="", bd=0)
        self.main_container.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Обёртка, чтобы отступы были как в макете (p-8)
        self.inner = tk.Frame(self.main_container, bg="", bd=0)
        self.inner.pack(expand=True, fill="both", padx=32, pady=32)

        # Flex: sidebar + main content
        self.root_row = tk.Frame(self.inner, bg="", bd=0)
        self.root_row.pack(expand=True, fill="both")

        # Sidebar
        self.sidebar = Sidebar(self.root_row, on_change_view=self.change_view)
        self.sidebar.pack(side="left", fill="y")

        # Main content
        self.content_frame = tk.Frame(self.root_row, bg="", bd=0)
        self.content_frame.pack(side="left", fill="both", expand=True, padx=(24, 0))

        self.current_view = None
        self.change_view("dashboard")

    def change_view(self, view_id: str):
        if self.current_view:
            self.current_view.destroy()

        if view_id == "dashboard":
            self.current_view = DashboardView(self.content_frame)
        elif view_id == "scanner":
            self.current_view = ScannerView(self.content_frame)
        elif view_id == "quarantine":
            self.current_view = QuarantineView(self.content_frame)
        else:
            self.current_view = SettingsView(self.content_frame)

        self.current_view.pack(fill="both", expand=True)
        self.sidebar.set_active(view_id)


# === Sidebar ===
class Sidebar(tk.Frame):
    def __init__(self, master, on_change_view):
        super().__init__(master, bg=SIDEBAR_BG, bd=0)
        self.on_change_view = on_change_view
        self.config(highlightthickness=1, highlightbackground=SIDEBAR_BORDER)

        self.active_id = None
        self.buttons = {}

        # Заголовок
        header = tk.Frame(self, bg=SIDEBAR_BG)
        header.pack(fill="x", padx=16, pady=(16, 12))

        title = tk.Label(
            header,
            text="Antivirus Pro",
            bg=SIDEBAR_BG,
            fg=CARD_HEADER_FG,
            font=("Segoe UI", 14, "bold"),
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Защита системы в реальном времени",
            bg=SIDEBAR_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # Кнопки навигации
        nav = tk.Frame(self, bg=SIDEBAR_BG)
        nav.pack(fill="x", padx=8, pady=(8, 16))

        items = [
            ("dashboard", "Панель управления"),
            ("scanner", "Сканер"),
            ("quarantine", "Карантин"),
            ("settings", "Настройки"),
        ]

        for vid, text in items:
            btn = tk.Label(
                nav, text=text,
                bg=SIDEBAR_BG,
                fg=SIDEBAR_INACTIVE_FG,
                font=("Segoe UI", 11),
                padx=12, pady=8,
                anchor="w",
            )
            btn.pack(fill="x", pady=4)
            btn.bind("<Button-1>", lambda e, v=vid: self.on_change_view(v))
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e5e7eb80"))
            btn.bind("<Leave>", lambda e, b=btn, v=vid: self._on_leave(b, v))
            self.buttons[vid] = btn

        # Нижний блок статуса
        bottom = tk.Frame(self, bg=SIDEBAR_BG)
        bottom.pack(fill="x", side="bottom", padx=16, pady=16)

        status = tk.Label(
            bottom,
            text="Статус: защищено",
            bg=SIDEBAR_BG,
            fg=ACCENT_GREEN,
            font=("Segoe UI", 10, "bold"),
        )
        status.pack(anchor="w")

        small = tk.Label(
            bottom,
            text="Последнее сканирование: вчера, 21:10",
            bg=SIDEBAR_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 8),
        )
        small.pack(anchor="w", pady=(2, 0))

    def _on_leave(self, btn: tk.Label, view_id: str):
        if self.active_id == view_id:
            btn.config(bg=SIDEBAR_ACTIVE_BG, fg=SIDEBAR_ACTIVE_FG)
        else:
            btn.config(bg=SIDEBAR_BG, fg=SIDEBAR_INACTIVE_FG)

    def set_active(self, view_id: str):
        self.active_id = view_id
        for vid, btn in self.buttons.items():
            if vid == view_id:
                btn.config(bg=SIDEBAR_ACTIVE_BG, fg=SIDEBAR_ACTIVE_FG)
            else:
                btn.config(bg=SIDEBAR_BG, fg=SIDEBAR_INACTIVE_FG)


# === Базовый «карточный» фрейм ===
class Card(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=CARD_BG, bd=0, **kwargs)
        self.config(highlightthickness=1, highlightbackground=CARD_BORDER)


# === Dashboard View ===
class DashboardView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="", bd=0)

        # Заголовок
        header = tk.Frame(self, bg="", bd=0)
        header.pack(fill="x", pady=(0, 16))

        title = tk.Label(
            header,
            text="Общая панель безопасности",
            bg="",
            fg=CARD_HEADER_FG,
            font=("Segoe UI", 18, "bold"),
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Сводка состояния защиты, последних сканирований и инцидентов.",
            bg="",
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        # Верхний ряд карточек (3 штуки)
        cards_row = tk.Frame(self, bg="", bd=0)
        cards_row.pack(fill="x")

        cards_row.grid_columnconfigure(0, weight=1, uniform="cards")
        cards_row.grid_columnconfigure(1, weight=1, uniform="cards")
        cards_row.grid_columnconfigure(2, weight=1, uniform="cards")

        # Карточка: защита
        c1 = Card(cards_row)
        c1.grid(row=0, column=0, padx=(0, 12), pady=(0, 16), sticky="nsew")

        tk.Label(c1, text="Статус защиты", bg=CARD_BG, fg=CARD_HEADER_FG,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(c1, text="В реальном времени", bg=CARD_BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=12)

        chip = tk.Label(
            c1,
            text="● Защита активна",
            bg="#dcfce7",
            fg="#166534",
            font=("Segoe UI", 9, "bold"),
            padx=8, pady=4,
        )
        chip.pack(anchor="w", padx=12, pady=(10, 8))

        tk.Label(
            c1,
            text="98% угроз блокируется автоматически до того, как повлиять на систему.",
            wraplength=260,
            justify="left",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=12, pady=(0, 12))

        # Карточка: последнее сканирование
        c2 = Card(cards_row)
        c2.grid(row=0, column=1, padx=6, pady=(0, 16), sticky="nsew")

        tk.Label(c2, text="Последнее сканирование", bg=CARD_BG, fg=CARD_HEADER_FG,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(c2, text="Полное сканирование • 18 мин", bg=CARD_BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=12)

        tk.Label(
            c2, text="Вчера, 21:10 • Обнаружено 3 угрозы",
            bg=CARD_BG, fg="#f97316", font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=12, pady=(10, 8))

        # Карточка: последние инциденты
        c3 = Card(cards_row)
        c3.grid(row=0, column=2, padx=(12, 0), pady=(0, 16), sticky="nsew")

        tk.Label(c3, text="Недавний инцидент", bg=CARD_BG, fg=CARD_HEADER_FG,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(c3, text="2 мин назад • Malware.Generic.2024", bg=CARD_BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=12)

        tk.Label(
            c3,
            text="Угроза была перемещена в карантин. Рекомендуется выполнить полное сканирование.",
            wraplength=260,
            justify="left",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=12, pady=(10, 12))

        # Нижний блок: таблица угроз и информация о системе
        bottom_row = tk.Frame(self, bg="", bd=0)
        bottom_row.pack(fill="both", expand=True)

        bottom_row.grid_columnconfigure(0, weight=2, uniform="bottom")
        bottom_row.grid_columnconfigure(1, weight=1, uniform="bottom")

        # Таблица угроз
        table_card = Card(bottom_row)
        table_card.grid(row=0, column=0, sticky="nsew", pady=(0, 0), padx=(0, 12))

        tk.Label(
            table_card,
            text="Недавние угрозы и действия",
            bg=CARD_BG,
            fg=CARD_HEADER_FG,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=12, pady=(10, 2))

        tk.Label(
            table_card,
            text="Обзор последних обнаруженных угроз и предпринятых действий.",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=12, pady=(0, 8))

        cols = ("threat", "level", "time", "status")
        tree = ttk.Treeview(table_card, columns=cols, show="headings", height=6)
        tree.pack(fill="both", expand=True, padx=12, pady=(4, 12))

        headings = ["Угроза", "Уровень риска", "Обнаружено", "Действие"]
        for col, text in zip(cols, headings):
            tree.heading(col, text=text)
            tree.column(col, width=120, anchor="w")

        for item in DASHBOARD_THREATS:
            tree.insert("", "end", values=item)

        # Карточка: системная информация
        sys_card = Card(bottom_row)
        sys_card.grid(row=0, column=1, sticky="nsew", pady=(0, 0), padx=(12, 0))

        tk.Label(
            sys_card,
            text="Состояние системы",
            bg=CARD_BG,
            fg=CARD_HEADER_FG,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=12, pady=(10, 2))

        # CPU/RAM
        if HAS_PSUTIL:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
        else:
            cpu = random.randint(12, 45)
            ram = random.randint(30, 70)

        cpu_label = tk.Label(
            sys_card,
            text=f"CPU: {cpu} %",
            bg=CARD_BG,
            fg=ACCENT_BLUE,
            font=("Segoe UI", 10, "bold"),
        )
        cpu_label.pack(anchor="w", padx=12, pady=(8, 2))

        ram_label = tk.Label(
            sys_card,
            text=f"Память: {ram} %",
            bg=CARD_BG,
            fg=ACCENT_BLUE,
            font=("Segoe UI", 10, "bold"),
        )
        ram_label.pack(anchor="w", padx=12, pady=(0, 8))

        tk.Label(
            sys_card,
            text="Защита файловой системы и сетевой активности включена.",
            wraplength=220,
            justify="left",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=12, pady=(4, 12))


# === Scanner View ===
class ScannerView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="", bd=0)

        self.scanning = False

        header = tk.Frame(self, bg="", bd=0)
        header.pack(fill="x", pady=(0, 16))

        tk.Label(
            header,
            text="Сканер угроз",
            bg="",
            fg=CARD_HEADER_FG,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Выберите тип сканирования и просмотрите подробный лог.",
            bg="",
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        # Основная карточка со сканером
        main_card = Card(self)
        main_card.pack(fill="both", expand=True)

        top_row = tk.Frame(main_card, bg=CARD_BG)
        top_row.pack(fill="x", padx=12, pady=(12, 8))

        # Кнопки типов скана
        btn_style = {
            "font": ("Segoe UI", 10),
            "bd": 0,
            "padx": 12,
            "pady": 6,
        }

        self.btn_quick = tk.Button(
            top_row, text="Быстрое сканирование",
            bg="#e0f2fe", fg="#1d4ed8", **btn_style,
            command=lambda: self.start_scan("quick"),
        )
        self.btn_quick.pack(side="left", padx=(0, 8))

        self.btn_full = tk.Button(
            top_row, text="Полное сканирование",
            bg="#eef2ff", fg="#4f46e5", **btn_style,
            command=lambda: self.start_scan("full"),
        )
        self.btn_full.pack(side="left", padx=8)

        self.btn_custom = tk.Button(
            top_row, text="Сканирование папки",
            bg="#faf5ff", fg="#7e22ce", **btn_style,
            command=lambda: self.start_scan("custom"),
        )
        self.btn_custom.pack(side="left", padx=8)

        # Прогресс и статус
        progress_frame = tk.Frame(main_card, bg=CARD_BG)
        progress_frame.pack(fill="x", padx=12, pady=(4, 8))

        self.progress = ttk.Progressbar(progress_frame, length=400)
        self.progress.pack(fill="x", pady=(4, 4))

        info_row = tk.Frame(progress_frame, bg=CARD_BG)
        info_row.pack(fill="x")

        self.lbl_status = tk.Label(
            info_row,
            text="Сканирование не запущено",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        self.lbl_status.pack(side="left")

        self.lbl_files = tk.Label(
            info_row,
            text="Файлов проверено: 0",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        self.lbl_files.pack(side="right")

        # Лог
        log_label = tk.Label(
            main_card,
            text="Журнал сканирования",
            bg=CARD_BG,
            fg=CARD_HEADER_FG,
            font=("Segoe UI", 10, "bold"),
        )
        log_label.pack(anchor="w", padx=12, pady=(8, 2))

        self.log = tk.Text(main_card, bg="#020617", fg="#e5e7eb", height=12, wrap="word")
        self.log.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # История сканов (в отдельной карточке снизу)
        history_card = Card(self)
        history_card.pack(fill="x", pady=(12, 0))

        tk.Label(
            history_card,
            text="История сканирования",
            bg=CARD_BG,
            fg=CARD_HEADER_FG,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=12, pady=(8, 2))

        tree = ttk.Treeview(history_card, columns=("type", "date", "duration", "threats"), show="headings", height=4)
        tree.pack(fill="x", expand=True, padx=12, pady=(0, 10))

        for col, text in zip(("type", "date", "duration", "threats"),
                             ["Тип", "Дата", "Длительность", "Угрозы"]):
            tree.heading(col, text=text)
            tree.column(col, width=120, anchor="w")

        for row in SCAN_HISTORY:
            tree.insert("", "end", values=row)

    def start_scan(self, scan_type):
        if self.scanning:
            return
        self.scanning = True
        self.progress["value"] = 0
        self.lbl_status.config(text="Идёт сканирование…")
        self.lbl_files.config(text="Файлов проверено: 0")
        self.log.delete("1.0", "end")
        self.log.insert("end", f"Запуск {scan_type} сканирования...\n")

        t = threading.Thread(target=self._scan_thread, args=(scan_type,), daemon=True)
        t.start()

    def _scan_thread(self, scan_type):
        total_files = {"quick": 3500, "full": 12000, "custom": 6000}.get(scan_type, 5000)
        delay = {"quick": 0.02, "full": 0.05, "custom": 0.03}.get(scan_type, 0.03)

        scanned = 0
        for i in range(101):
            time.sleep(delay)
            self.progress["value"] = i
            scanned += random.randint(80, 250)
            if scanned > total_files:
                scanned = total_files

            self.lbl_files.config(text=f"Файлов проверено: {scanned}")

            if i > 10 and i % 17 == 0:
                threat = random.choice(DASHBOARD_THREATS)[0]
                self.log.insert("end", f"⚠ Обнаружен подозрительный объект: {threat}\n")
                self.log.see("end")

            self.update_idletasks()

        self.log.insert("end", "\n✅ Сканирование завершено.\n")
        self.lbl_status.config(text="Сканирование завершено")
        self.scanning = False


# === Quarantine View ===
class QuarantineView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="", bd=0)

        header = tk.Frame(self, bg="", bd=0)
        header.pack(fill="x", pady=(0, 16))

        tk.Label(
            header,
            text="Карантин",
            bg="",
            fg=CARD_HEADER_FG,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Файлы, изолированные от системы. Вы можете удалить или восстановить их.",
            bg="",
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        main_card = Card(self)
        main_card.pack(fill="both", expand=True)

        cols = ("file", "threat", "path", "size", "risk")
        self.tree = ttk.Treeview(main_card, columns=cols, show="headings", height=10)
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)

        for col, text in zip(cols, ["Файл", "Угроза", "Путь", "Размер", "Риск"]):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=120, anchor="w")

        for row in QUARANTINE_ITEMS:
            self.tree.insert("", "end", values=row)

        # Кнопки действий
        actions = tk.Frame(main_card, bg=CARD_BG)
        actions.pack(fill="x", padx=12, pady=(0, 12))

        btn_delete = tk.Button(
            actions,
            text="Удалить выбранные",
            bg=ACCENT_RED,
            fg="white",
            font=("Segoe UI", 10),
            bd=0,
            padx=10, pady=6,
            command=self.delete_selected,
        )
        btn_delete.pack(side="left")

        btn_restore = tk.Button(
            actions,
            text="Восстановить выбранные",
            bg="#e0f2fe",
            fg="#1d4ed8",
            font=("Segoe UI", 10),
            bd=0,
            padx=10, pady=6,
            command=self.restore_selected,
        )
        btn_restore.pack(side="left", padx=(8, 0))

        self.summary_label = tk.Label(
            actions,
            text="Файлов в карантине: 3",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        self.summary_label.pack(side="right")

        self.update_summary()

    def delete_selected(self):
        for item in self.tree.selection():
            self.tree.delete(item)
        self.update_summary()

    def restore_selected(self):
        # Для заглушки поведение такое же (просто удаляем из списка)
        for item in self.tree.selection():
            self.tree.delete(item)
        self.update_summary()

    def update_summary(self):
        count = len(self.tree.get_children())
        self.summary_label.config(text=f"Файлов в карантине: {count}")


# === Settings View ===
class SettingsView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="", bd=0)

        header = tk.Frame(self, bg="", bd=0)
        header.pack(fill="x", pady=(0, 16))

        tk.Label(
            header,
            text="Настройки защиты",
            bg="",
            fg=CARD_HEADER_FG,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Управляйте параметрами защиты, уведомлений и производительности.",
            bg="",
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        main_card = Card(self)
        main_card.pack(fill="both", expand=True)

        inner = tk.Frame(main_card, bg=CARD_BG)
        inner.pack(fill="both", expand=True, padx=12, pady=12)

        for title, default, desc in SETTINGS_DATA:
            row = tk.Frame(inner, bg=CARD_BG)
            row.pack(fill="x", pady=6)

            txt = tk.Frame(row, bg=CARD_BG)
            txt.pack(side="left", fill="x", expand=True)

            tk.Label(
                txt, text=title,
                bg=CARD_BG, fg=CARD_HEADER_FG,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w")

            tk.Label(
                txt, text=desc,
                bg=CARD_BG, fg=TEXT_MUTED,
                font=("Segoe UI", 9),
                wraplength=420,
                justify="left",
            ).pack(anchor="w")

            var = tk.BooleanVar(value=default)
            chk = tk.Checkbutton(
                row,
                variable=var,
                bg=CARD_BG,
                activebackground=CARD_BG,
                onvalue=True,
                offvalue=False,
            )
            chk.pack(side="right")


# === Точка входа ===
if __name__ == "__main__":
    app = AntivirusApp()
    app.mainloop()
