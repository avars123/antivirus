import sys
import math
import random
from PySide6.QtCore import (
    Qt, QTimer, QRectF, QEasingCurve, QPropertyAnimation, QPoint
)
from PySide6.QtGui import (
    QColor, QPainter, QBrush, QFont, QLinearGradient, QIcon
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem, QStackedWidget,
    QProgressBar, QRadioButton, QButtonGroup, QFileDialog, QSlider,
    QSpacerItem, QSizePolicy
)


# ---------- Общие стили Tahoe 26 ----------

APP_QSS = """
QMainWindow {
    background-color: #060814;
}

QLabel {
    color: rgba(255,255,255,0.9);
    font-family: -apple-system, system-ui, "SF Pro Display";
}

QPushButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255,255,255,0.18),
        stop:1 rgba(255,255,255,0.04)
    );
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.35);
    color: white;
    padding: 10px 18px;
    font-size: 14px;
}

QPushButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255,255,255,0.30),
        stop:1 rgba(255,255,255,0.12)
    );
}

QPushButton:pressed {
    background: rgba(255,255,255,0.12);
}

QListWidget {
    background: rgba(12,16,40,0.75);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.12);
    color: white;
    padding: 8px;
}

QListWidget::item {
    padding: 6px 4px;
}

QProgressBar {
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 10px;
    background: rgba(10,10,25,0.6);
    text-align: center;
    color: white;
}

QProgressBar::chunk {
    border-radius: 9px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #5ad1ff,
        stop:1 #c86bff
    );
}

QRadioButton {
    color: rgba(255,255,255,0.8);
    font-size: 13px;
}

QSlider::groove:horizontal {
    height: 6px;
    background: rgba(255,255,255,0.25);
    border-radius: 3px;
}
QSlider::handle:horizontal {
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
    background: white;
}
"""


# ---------- Виджет жидких волн (фон) ----------

class LiquidWaveBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance)
        self.timer.start(25)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def advance(self):
        self.phase += 0.04
        if self.phase > 2 * math.pi:
            self.phase -= 2 * math.pi
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Градиентный тёмный фон
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(9, 11, 26))
        gradient.setColorAt(1.0, QColor(4, 6, 14))
        painter.fillRect(self.rect(), gradient)

        # Волны (liquid)
        for i, (amp, height_factor, alpha) in enumerate([
            (18, 0.72, 70),
            (26, 0.65, 55),
            (34, 0.55, 35),
        ]):
            path_color1 = QColor(104, 221, 255, alpha)
            path_color2 = QColor(179, 123, 255, alpha)

            grad = QLinearGradient(0, 0, self.width(), 0)
            grad.setColorAt(0.0, path_color1)
            grad.setColorAt(1.0, path_color2)

            painter.setBrush(grad)
            painter.setPen(Qt.NoPen)

            poly = []
            w = self.width()
            h = self.height()
            base_y = h * height_factor

            step = 8
            for x in range(0, w + step, step):
                y = base_y + math.sin(self.phase + x * 0.015 + i) * amp
                poly.append(QPoint(x, int(y)))

            # замыкаем вниз
            poly.append(QPoint(w, h + 10))
            poly.append(QPoint(0, h + 10))

            painter.drawPolygon(*poly)


# ---------- Стеклянная панель ----------

class GlassPanel(QWidget):
    def __init__(self, radius=22, opacity=0.18, border_opacity=0.40, parent=None):
        super().__init__(parent)
        self.radius = radius
        self.opacity = opacity
        self.border_opacity = border_opacity
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(0, 0, -1, -1)

        # Подложка glow
        glow_color = QColor(120, 180, 255, 35)
        painter.setBrush(glow_color)
        painter.setPen(Qt.NoPen)
        bigger_rect = rect.adjusted(-6, -6, 6, 6)
        painter.drawRoundedRect(bigger_rect, self.radius + 8, self.radius + 8)

        # Основное стекло
        glass_color = QColor(255, 255, 255, int(self.opacity * 255))
        painter.setBrush(glass_color)
        painter.setPen(QColor(255, 255, 255, int(self.border_opacity * 255)))
        painter.drawRoundedRect(rect, self.radius, self.radius)


# ---------- Боковая панель (навигация) ----------

class SideNavButton(QPushButton):
    def __init__(self, icon_text: str, label: str, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.setText(f"{icon_text}  {label}")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 14px;
                background: transparent;
                border-radius: 14px;
                border: 1px solid transparent;
                color: rgba(255,255,255,0.75);
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.08);
            }
            QPushButton:checked {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(115,200,255,0.55),
                    stop:1 rgba(195,125,255,0.75)
                );
                border: 1px solid rgba(255,255,255,0.7);
                color: white;
            }
        """)


class SideNav(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        title = QLabel("🛡 Tahoe 26")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")

        subtitle = QLabel("LiquidGlass AV")
        subtitle.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.6);")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        self.btn_dashboard = SideNavButton("🏠", "Главная")
        self.btn_scan = SideNavButton("🔍", "Сканирование")
        self.btn_results = SideNavButton("🧬", "Результаты")
        self.btn_settings = SideNavButton("⚙️", "Настройки")

        self.buttons = [
            self.btn_dashboard,
            self.btn_scan,
            self.btn_results,
            self.btn_settings,
        ]

        for b in self.buttons:
            layout.addWidget(b)

        layout.addStretch()

        status_label = QLabel("Статус: защита включена")
        status_label.setStyleSheet("font-size: 11px; color: rgba(180,255,200,0.8);")
        layout.addWidget(status_label)

        self.setFixedWidth(190)


# ---------- Страница: Главная ----------

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        glass = GlassPanel(radius=22, opacity=0.20, border_opacity=0.4)
        layout = QVBoxLayout(glass)
        layout.setContentsMargins(22, 18, 22, 22)
        layout.setSpacing(16)

        title = QLabel("Общая сводка")
        title.setStyleSheet("font-size: 20px; font-weight: 600;")

        desc = QLabel("Ваш MacOS Tahoe 26 защищён. Последнее сканирование: 3 мин назад.")
        desc.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.7);")

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)

        def stat_card(title_txt, value_txt, accent_color):
            w = GlassPanel(radius=18, opacity=0.20, border_opacity=0.35)
            lv = QVBoxLayout(w)
            lv.setContentsMargins(14, 12, 14, 12)
            t = QLabel(title_txt)
            t.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.6);")
            v = QLabel(value_txt)
            v.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {accent_color};")
            lv.addWidget(t)
            lv.addWidget(v)
            lv.addStretch()
            return w

        stats_row.addWidget(stat_card("Угроз заблокировано", "23", "#8af5c9"))
        stats_row.addWidget(stat_card("Последних сканирований", "5", "#7fd4ff"))
        stats_row.addWidget(stat_card("Подозрительных файлов", "2", "#ffc38a"))

        quick_btn_row = QHBoxLayout()
        quick_btn_row.setSpacing(10)

        full_btn = QPushButton("Полное сканирование")
        fast_btn = QPushButton("Быстрое сканирование")
        folder_btn = QPushButton("Сканировать папку…")

        quick_btn_row.addWidget(full_btn)
        quick_btn_row.addWidget(fast_btn)
        quick_btn_row.addWidget(folder_btn)

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(stats_row)
        layout.addSpacing(6)
        layout.addLayout(quick_btn_row)
        layout.addStretch()

        root.addWidget(glass)

        # Эти кнопки можно связать с реальными действиями из MainWindow
        self.full_btn = full_btn
        self.fast_btn = fast_btn
        self.folder_btn = folder_btn


# ---------- Страница: Сканирование ----------

class ScanPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        top_panel = GlassPanel(radius=22, opacity=0.20, border_opacity=0.4)
        top_layout = QVBoxLayout(top_panel)
        top_layout.setContentsMargins(22, 20, 22, 22)
        top_layout.setSpacing(12)

        title = QLabel("Сканирование системы")
        title.setStyleSheet("font-size: 20px; font-weight: 600;")

        mode_label = QLabel("Режим сканирования")
        mode_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.7);")

        self.mode_group = QButtonGroup(self)

        full = QRadioButton("Полное сканирование")
        fast = QRadioButton("Быстрое сканирование")
        folder = QRadioButton("Сканирование папки")
        custom = QRadioButton("Выборочное (системные области)")

        full.setChecked(True)

        for rb in (full, fast, folder, custom):
            self.mode_group.addButton(rb)

        r_layout = QHBoxLayout()
        r_layout.setSpacing(18)
        r_layout.addWidget(full)
        r_layout.addWidget(fast)
        r_layout.addWidget(folder)
        r_layout.addWidget(custom)
        r_layout.addStretch()

        self.scan_button = QPushButton("Запустить сканирование")
        self.scan_button.setFixedHeight(40)

        # Прогресс
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        self.state_label = QLabel("Ожидание запуска…")
        self.state_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.7);")

        top_layout.addWidget(title)
        top_layout.addWidget(mode_label)
        top_layout.addLayout(r_layout)
        top_layout.addSpacing(8)
        top_layout.addWidget(self.scan_button)
        top_layout.addWidget(self.progress)
        top_layout.addWidget(self.state_label)

        root.addWidget(top_panel)

        # Нижняя панель с логом
        bottom_panel = GlassPanel(radius=22, opacity=0.18, border_opacity=0.3)
        bottom_layout = QVBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(22, 18, 22, 18)
        bottom_layout.setSpacing(8)

        log_title = QLabel("Журнал сканирования")
        log_title.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.75);")

        self.log_box = QListWidget()

        bottom_layout.addWidget(log_title)
        bottom_layout.addWidget(self.log_box)

        root.addWidget(bottom_panel)

        self.folder_radio = folder


# ---------- Страница: Результаты ----------

class ResultsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        panel = GlassPanel(radius=22, opacity=0.22, border_opacity=0.4)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(22, 20, 22, 22)
        layout.setSpacing(10)

        title = QLabel("Результаты последнего сканирования")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")

        subtitle = QLabel("Обнаруженные угрозы и действия.")
        subtitle.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.7);")

        self.threats_list = QListWidget()

        btn_row = QHBoxLayout()
        self.btn_quarantine = QPushButton("Поместить всё в карантин")
        self.btn_ignore = QPushButton("Игнорировать выбранное")
        btn_row.addWidget(self.btn_quarantine)
        btn_row.addWidget(self.btn_ignore)
        btn_row.addStretch()

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.threats_list)
        layout.addLayout(btn_row)

        root.addWidget(panel)


# ---------- Страница: Настройки ----------

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        panel = GlassPanel(radius=22, opacity=0.22, border_opacity=0.4)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(22, 20, 22, 22)
        layout.setSpacing(12)

        title = QLabel("Настройки Tahoe 26")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")

        auto_start_label = QLabel("Автозапуск при входе в систему")
        auto_start_label.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.8);")
        self.auto_start_btn = QPushButton("Включено")
        self.auto_start_btn.setCheckable(True)
        self.auto_start_btn.setChecked(True)
        self.auto_start_btn.clicked.connect(self.toggle_auto_start)

        auto_row = QHBoxLayout()
        auto_row.addWidget(auto_start_label)
        auto_row.addStretch()
        auto_row.addWidget(self.auto_start_btn)

        sens_label = QLabel("Чувствительность детектора")
        sens_label.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.8);")
        self.sens_slider = QSlider(Qt.Horizontal)
        self.sens_slider.setRange(1, 10)
        self.sens_slider.setValue(7)

        layout.addWidget(title)
        layout.addSpacing(6)
        layout.addLayout(auto_row)
        layout.addWidget(sens_label)
        layout.addWidget(self.sens_slider)

        layout.addSpacing(10)

        info = QLabel("Tahoe 26 • LiquidGlass Antivirus — учебная заглушка, "
                      "эмуляция интерфейса без реального антивирусного ядра.")
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.6);")

        layout.addWidget(info)
        layout.addStretch()

        root.addWidget(panel)

    def toggle_auto_start(self):
        if self.auto_start_btn.isChecked():
            self.auto_start_btn.setText("Включено")
        else:
            self.auto_start_btn.setText("Выключено")


# ---------- Главное окно ----------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tahoe 26 • LiquidGlass Antivirus (Mock)")
        self.resize(1050, 640)

        central = QWidget()
        self.setCentralWidget(central)

        # Фон с волнами
        self.background = LiquidWaveBackground(self)
        self.background.lower()

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(14)

        # Боковая стеклянная панель
        self.side_glass = GlassPanel(radius=24, opacity=0.20, border_opacity=0.45)
        side_layout_outer = QVBoxLayout(self.side_glass)
        side_layout_outer.setContentsMargins(0, 0, 0, 0)
        side_layout_outer.setSpacing(0)

        self.side_nav = SideNav()
        side_layout_outer.addWidget(self.side_nav)

        # Основная стеклянная область
        self.main_glass = GlassPanel(radius=26, opacity=0.18, border_opacity=0.38)
        main_gl_layout = QVBoxLayout(self.main_glass)
        main_gl_layout.setContentsMargins(18, 18, 18, 18)
        main_gl_layout.setSpacing(10)

        # Верхушка (заголовок + псевдо macOS-кнопки)
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        # Псевдокнопки окна как в macOS
        circles = QWidget()
        circles_layout = QHBoxLayout(circles)
        circles_layout.setContentsMargins(0, 0, 0, 0)
        circles_layout.setSpacing(6)

        def circle(color):
            w = QWidget()
            w.setFixedSize(12, 12)
            w.setStyleSheet(f"""
                QWidget {{
                    background-color: {color};
                    border-radius: 6px;
                }}
            """)
            return w

        circles_layout.addWidget(circle("#ff5f57"))
        circles_layout.addWidget(circle("#febc2e"))
        circles_layout.addWidget(circle("#28c840"))

        title_label = QLabel("LiquidGlass Antivirus · macOS Tahoe 26")
        title_label.setStyleSheet("font-size: 15px; font-weight: 500;")

        top_bar.addWidget(circles)
        top_bar.addSpacing(8)
        top_bar.addWidget(title_label)
        top_bar.addStretch()

        main_gl_layout.addLayout(top_bar)

        # Страницы
        self.pages = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.scan_page = ScanPage()
        self.results_page = ResultsPage()
        self.settings_page = SettingsPage()

        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.scan_page)
        self.pages.addWidget(self.results_page)
        self.pages.addWidget(self.settings_page)

        main_gl_layout.addWidget(self.pages)

        root_layout.addWidget(self.side_glass)
        root_layout.addWidget(self.main_glass, 1)

        # Связка кнопок навигации
        self.side_nav.btn_dashboard.clicked.connect(
            lambda: self.switch_page(0, self.side_nav.btn_dashboard)
        )
        self.side_nav.btn_scan.clicked.connect(
            lambda: self.switch_page(1, self.side_nav.btn_scan)
        )
        self.side_nav.btn_results.clicked.connect(
            lambda: self.switch_page(2, self.side_nav.btn_results)
        )
        self.side_nav.btn_settings.clicked.connect(
            lambda: self.switch_page(3, self.side_nav.btn_settings)
        )

        # по умолчанию главная
        self.side_nav.btn_dashboard.setChecked(True)
        self.pages.setCurrentIndex(0)

        # Сканирование
        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self.scan_step)
        self.scan_progress = 0
        self.current_fake_threats = []

        self.scan_page.scan_button.clicked.connect(self.start_scan)

        # Быстрые кнопки с главной
        self.dashboard_page.full_btn.clicked.connect(
            lambda: self.start_scan_from_dashboard("full")
        )
        self.dashboard_page.fast_btn.clicked.connect(
            lambda: self.start_scan_from_dashboard("fast")
        )
        self.dashboard_page.folder_btn.clicked.connect(
            lambda: self.start_scan_from_dashboard("folder")
        )

    # --- Навигация страниц ---

    def switch_page(self, index: int, button: SideNavButton):
        self.pages.setCurrentIndex(index)
        for b in self.side_nav.buttons:
            b.setChecked(b is button)

    # --- Логика сканирования ---

    def start_scan_from_dashboard(self, mode: str):
        # Переключаемся на вкладку "Сканирование"
        self.switch_page(1, self.side_nav.btn_scan)

        # Выставляем нужный режим
        for rb in self.scan_page.mode_group.buttons():
            text = rb.text().lower()
            if mode == "full" and "полное" in text:
                rb.setChecked(True)
            elif mode == "fast" and "быстрое" in text:
                rb.setChecked(True)
            elif mode == "folder" and "папки" in text:
                rb.setChecked(True)

        self.start_scan()

    def start_scan(self):
        # Если выбрано сканирование папки — показать диалог
        folder_needed = self.scan_page.folder_radio.isChecked()
        if folder_needed:
            folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сканирования")
            if not folder:
                return
            folder_text = folder
        else:
            folder_text = "Система / Диски"

        self.scan_page.log_box.clear()
        self.scan_page.log_box.addItem(f"Запуск сканирования: {folder_text}")
        self.scan_page.state_label.setText("Сканирование выполняется…")
        self.scan_page.progress.setValue(0)
        self.scan_page.scan_button.setEnabled(False)

        self.scan_progress = 0
        self.current_fake_threats = []

        self.scan_timer.start(120)  # шаг ~0.12 сек

    def scan_step(self):
        if self.scan_progress >= 100:
            self.scan_timer.stop()
            self.scan_page.state_label.setText("Сканирование завершено.")
            self.scan_page.scan_button.setEnabled(True)
            self.populate_results()
            return

        self.scan_progress += random.randint(1, 4)
        if self.scan_progress > 100:
            self.scan_progress = 100

        self.scan_page.progress.setValue(self.scan_progress)

        # Фейковые угрозы
        if random.random() < 0.26:
            threat_name = random.choice([
                "Trojan.Tahoe.Dropper",
                "Backdoor.NebulaShell",
                "Adware.CloudBurst",
                "Worm.LiquidWave",
                "Riskware.KeyInjector",
                "Spyware.GlassEye",
                "Heuristic.MacOS.Tahoe.Fake",
            ])
            path = random.choice([
                "C:/Users/Public/Downloads",
                "C:/Windows/Temp",
                "C:/ProgramData",
                "C:/Users/User/AppData/Roaming",
                "/System/Library/CoreServices",
            ])
            item_txt = f"[Угроза] {threat_name} — {path}"
            self.scan_page.log_box.addItem(item_txt)
            self.scan_page.log_box.scrollToBottom()
            self.current_fake_threats.append(item_txt)

        elif random.random() < 0.25:
            msg = random.choice([
                "Проверка системных библиотек…",
                "Анализ загружаемых модулей…",
                "Сканирование архивов…",
                "Проверка сетевых портов…",
                "Анализ подписей и хэшей…",
            ])
            self.scan_page.log_box.addItem(msg)
            self.scan_page.log_box.scrollToBottom()

    def populate_results(self):
        self.results_page.threats_list.clear()

        if not self.current_fake_threats:
            self.results_page.threats_list.addItem("Угроз не обнаружено. Система в безопасности.")
            return

        for t in self.current_fake_threats:
            item = QListWidgetItem(t)
            self.results_page.threats_list.addItem(item)

        # Переключаемся на вкладку "Результаты"
        self.switch_page(2, self.side_nav.btn_results)

    # --- Адаптация фона/стекла при ресайзе ---

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.background.setGeometry(self.rect())
