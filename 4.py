import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QHBoxLayout, QFileDialog, QRadioButton, QButtonGroup
)
from PySide6.QtGui import QColor, QPainter, QBrush
from PySide6.QtCore import Qt


class GlassWidget(QWidget):
    """Полупрозрачный жидко-стеклянный фон."""
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # LiquidGlass стиль
        glass_color = QColor(255, 255, 255, 60)  # прозрачность
        painter.setBrush(QBrush(glass_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)


class AntivirusUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LiquidGlass Antivirus")
        self.resize(700, 500)

        # Главное боковое оформление
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.glass = GlassWidget()
        self.glass_layout = QVBoxLayout(self.glass)
        self.glass_layout.setSpacing(20)
        self.glass_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("🛡 LiquidGlass Antivirus")
        title.setStyleSheet("font-size: 26px; font-weight: 600; color: white;")

        # Радиокнопки сканирования
        self.scan_group = QButtonGroup()
        full = QRadioButton("Полное сканирование")
        fast = QRadioButton("Быстрое сканирование")
        folder = QRadioButton("Сканирование папки")
        schedule = QRadioButton("По расписанию")

        full.setChecked(True)

        for rb in (full, fast, folder, schedule):
            rb.setStyleSheet("color:white; font-size:16px;")
            self.scan_group.addButton(rb)

        # Кнопка Сканировать
        scan_btn = QPushButton("Сканировать")
        scan_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.25);
                border: 1px solid rgba(255,255,255,0.4);
                border-radius: 15px;
                padding: 12px;
                color: white;
                font-size: 18px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.35);
            }
        """)
        scan_btn.clicked.connect(self.scan)

        # Список результатов
        self.result_box = QListWidget()
        self.result_box.setStyleSheet("""
            QListWidget {
                background: rgba(255,255,255,0.15);
                color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        # Добавление элементов
        self.glass_layout.addWidget(title)
        self.glass_layout.addWidget(full)
        self.glass_layout.addWidget(fast)
        self.glass_layout.addWidget(folder)
        self.glass_layout.addWidget(schedule)
        self.glass_layout.addWidget(scan_btn)
        self.glass_layout.addWidget(QLabel("Обнаруженные угрозы:"))
        self.glass_layout.addWidget(self.result_box)

        self.main_layout.addWidget(self.glass)

        # Фон как macOS blur
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
        """)

    def scan(self):
        """Фейковое сканирование."""
        self.result_box.clear()

        selected = self.scan_group.checkedButton().text()

        fake_viruses = [
            "Trojan.FakeInstaller",
            "Worm.AutoRun.Gen",
            "Adware.SearchBoost",
            "RiskTool.WinKeyGen",
            "Backdoor.DarkGate",
            "Spyware.CookieTracker"
        ]

        if "папки" in selected:
            folder = QFileDialog.getExistingDirectory(self, "Выбрать папку")
            if not folder:
                return

        for v in fake_viruses:
            self.result_box.addItem(f"Обнаружено: {v}")

        self.result_box.addItem("Сканирование завершено ✔")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = AntivirusUI()
    ui.show()
    sys.exit(app.exec())
