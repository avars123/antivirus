import sys
import time
import random
import platform

import psutil
from PyQt6 import QtCore, QtGui, QtWidgets


# -------------------------------
# Вспомогательные сущности
# -------------------------------

THREATS_DASHBOARD = [
    {"name": "Malware.Generic.2024", "severity": "high", "time": "2 мин назад", "status": "quarantined"},
    {"name": "Adware.Installer", "severity": "medium", "time": "1 час назад", "status": "removed"},
    {"name": "PUP.Optional.Bundle", "severity": "low", "time": "3 часа назад", "status": "removed"},
]

QUARANTINE_ITEMS = [
    {
        "name": "suspicious_installer.exe",
        "threat": "Malware.Generic.2024",
        "path": "/Users/admin/Downloads/",
        "date": "2 мин назад",
        "size": "2.4 МБ",
        "risk": "high",
    },
    {
        "name": "crack_tool.exe",
        "threat": "PUP.Optional.Bundle",
        "path": "C:/Games/Cracks/",
        "date": "10 мин назад",
        "size": "5.8 МБ",
        "risk": "medium",
    },
    {
        "name": "email_attachment.scr",
        "threat": "Trojan.Mail.Spam",
        "path": "/Users/admin/Documents/",
        "date": "30 мин назад",
        "size": "1.2 МБ",
        "risk": "high",
    },
]

SETTINGS_DATA = [
    {
        "category": "Защита",
        "items": [
            {"id": "realtime", "label": "Защита в реальном времени", "description": "Постоянный мониторинг системы", "enabled": True},
            {"id": "cloud", "label": "Облачная защита", "description": "Расширенное обнаружение угроз", "enabled": True},
            {"id": "behavioral", "label": "Поведенческий анализ", "description": "Обнаружение подозрительной активности", "enabled": True},
        ],
    },
    {
        "category": "Производительность",
        "items": [
            {"id": "gaming", "label": "Игровой режим", "description": "Минимум уведомлений во время игр", "enabled": False},
            {"id": "battery", "label": "Эко-режим", "description": "Оптимизация для ноутбуков", "enabled": True},
        ],
    },
    {
        "category": "Уведомления",
        "items": [
            {"id": "threats", "label": "Оповещения об угрозах", "description": "Уведомлять при обнаружении угроз", "enabled": True},
            {"id": "updates", "label": "Уведомления об обновлениях", "description": "Сообщать о новых версиях", "enabled": True},
            {"id": "summary", "label": "Еженедельный отчёт", "description": "Отправлять краткий отчет", "enabled": False},
        ],
    },
    {
        "category": "Обновления",
        "items": [
            {"id": "autoUpdate", "label": "Автообновление", "description": "Автоматически загружать обновления", "enabled": True},
            {"id": "beta", "label": "Бета-версии", "description": "Получать ранний доступ к новым функциям", "enabled": False},
        ],
    },
    {
        "category": "Конфиденциальность",
        "items": [
            {"id": "stats", "label": "Отправка статистики", "description": "Помогать улучшать продукт", "enabled": False},
            {"id": "logs", "label": "Отправка логов", "description": "Отправлять анонимные журналы", "enabled": False},
        ],
    },
]

SCAN_HISTORY = [
    {"type": "Быстрое сканирование", "duration": "2 мин", "date": "Сегодня, 10:24", "threats": 0},
    {"type": "Полное сканирование", "duration": "18 мин", "date": "Вчера, 21:10", "threats": 3},
    {"type": "Сканирование папки", "duration": "45 сек", "date": "Вчера, 14:02", "threats": 1},
]

SCAN_THREATS_FAKE = [
    "Trojan.Win32.FakeAlert",
    "Worm.AutoRun.Spread",
    "Adware.Installer.Generic",
    "PUP.Optional.Toolbar",
    "Backdoor.Win32.DarkRat",
    "Riskware.RemoteAdmin",
    "JS.Downloader.Agent",
]


# -------------------------------
# Поток сканирования
# -------------------------------

class ScanWorker(QtCore.QThread):
    progress_changed = QtCore.pyqtSignal(int)
    files_changed = QtCore.pyqtSignal(int)
    log_message = QtCore.pyqtSignal(str)
    scan_finished = QtCore.pyqtSignal(int)  # число найденных "угроз"

    def __init__(self, scan_type: str, parent=None):
        super().__init__(parent)
        self.scan_type = scan_type

    def run(self):
        # разные "объемы" для разных типов
        if self.scan_type == "quick":
            total_files = 3500
            delay = 0.03
        elif self.scan_type == "full":
            total_files = 12000
            delay = 0.06
        else:  # custom
            total_files = 6000
            delay = 0.045

        files = 0
        threats_found = 0

        for p in range(101):
            time.sleep(delay)
            files += random.randint(80, 260)
            if files > total_files:
                files = total_files

            self.progress_changed.emit(p)
            self.files_changed.emit(files)

            # иногда "находим" угрозы
            if p > 10 and p % 13 == 0:
                threat = random.choice(SCAN_THREATS_FAKE)
                threats_found += 1
                self.log_message.emit(f"Обнаружен подозрительный объект: {threat}")

        self.scan_finished.emit(threats_found)


# -------------------------------
# Страница Dashboard
# -------------------------------

class DashboardPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(16)

        # Заголовок
        header_layout = QtWidgets.QHBoxLayout()
        header_text = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("Панель безопасности")
        title.setStyleSheet("font-size: 20px; font-weight: 600; color: #ffffff;")
        subtitle = QtWidgets.QLabel("Статус защиты в реальном времени")
        subtitle.setStyleSheet("color: #a0aec0;")
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header_layout.addLayout(header_text)

        status_label = QtWidgets.QLabel("● ЗАЩИЩЕНО")
        status_label.setStyleSheet(
            "background-color: rgba(56, 161, 105, 0.15);"
            "border-radius: 12px;"
            "padding: 6px 12px;"
            "color: #9ae6b4;"
            "font-weight: 600;"
        )
        header_layout.addWidget(status_label, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(header_layout)

        # Карточки статуса
        cards_layout = QtWidgets.QHBoxLayout()
        cards_layout.setSpacing(12)

        self.card_protection = self._create_status_card(
            "Защита в реальном времени",
            "Активна",
            "Ежедневная блокировка угроз",
            progress_value=98,
            extra="98% угроз блокируется автоматически",
        )
        self.card_last_scan = self._create_status_card(
            "Последнее сканирование",
            "Вчера, 21:10",
            "Полное сканирование системы",
            progress_value=100,
            extra="3 угрозы были нейтрализованы",
        )
        self.card_incidents = self._create_status_card(
            "Последний инцидент",
            "2 мин назад",
            "Угроза перемещена в карантин",
            progress_value=100,
            extra="Все угрозы в безопасной зоне",
        )

        cards_layout.addWidget(self.card_protection)
        cards_layout.addWidget(self.card_last_scan)
        cards_layout.addWidget(self.card_incidents)

        main_layout.addLayout(cards_layout)

        # Системная информация
        self.system_info_label = QtWidgets.QLabel()
        self.system_info_label.setStyleSheet("color: #a0aec0; margin-top: 8px;")
        main_layout.addWidget(self.system_info_label)

        # Заголовок таблицы угроз
        threats_header_layout = QtWidgets.QHBoxLayout()
        th_title = QtWidgets.QLabel("Недавние угрозы")
        th_title.setStyleSheet("font-size: 16px; color: #ffffff; font-weight: 500;")
        th_subtitle = QtWidgets.QLabel("Последние действия по защите")
        th_subtitle.setStyleSheet("color: #a0aec0;")
        th_text_layout = QtWidgets.QVBoxLayout()
        th_text_layout.addWidget(th_title)
        th_text_layout.addWidget(th_subtitle)
        threats_header_layout.addLayout(th_text_layout)
        main_layout.addLayout(threats_header_layout)

        # Таблица угроз
        self.threats_table = QtWidgets.QTableWidget()
        self.threats_table.setColumnCount(4)
        self.threats_table.setHorizontalHeaderLabels(["Угроза", "Уровень", "Время", "Статус"])
        self.threats_table.verticalHeader().setVisible(False)
        self.threats_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.threats_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.threats_table.setShowGrid(False)
        self.threats_table.setStyleSheet(
            "QTableWidget { background-color: #111827; color: #e5e7eb; border: 1px solid #1f2937; }"
            "QHeaderView::section { background-color: #111827; color: #9ca3af; border: none; }"
        )
        self._fill_threats_table()
        self.threats_table.horizontalHeader().setStretchLastSection(True)
        self.threats_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

        main_layout.addWidget(self.threats_table)

        # Таймер обновления CPU/RAM
        self.sys_timer = QtCore.QTimer(self)
        self.sys_timer.timeout.connect(self.update_system_info)
        self.sys_timer.start(800)
        self.update_system_info()

    def _create_status_card(self, title: str, status: str, desc: str, progress_value: int, extra: str):
        frame = QtWidgets.QFrame()
        frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        frame.setStyleSheet(
            "QFrame {"
            "background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            " stop:0 #1d4ed8, stop:1 #4f46e5);"
            "border-radius: 16px;"
            "padding: 14px;"
            "}"
        )
        layout = QtWidgets.QVBoxLayout(frame)

        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("color: #ffffff; font-weight: 600;")
        layout.addWidget(title_label)

        status_label = QtWidgets.QLabel(status)
        status_label.setStyleSheet("color: #d1fae5;")
        layout.addWidget(status_label)

        desc_label = QtWidgets.QLabel(desc)
        desc_label.setStyleSheet("color: #bfdbfe;")
        layout.addWidget(desc_label)

        progress = QtWidgets.QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(progress_value)
        progress.setTextVisible(False)
        progress.setStyleSheet(
            "QProgressBar {"
            "background-color: rgba(15, 23, 42, 0.5);"
            "border-radius: 6px;"
            "}"
            "QProgressBar::chunk {"
            "background-color: #22c55e;"
            "border-radius: 6px;"
            "}"
        )
        layout.addWidget(progress)

        extra_label = QtWidgets.QLabel(extra)
        extra_label.setStyleSheet("color: #e5e7eb; font-size: 11px;")
        layout.addWidget(extra_label)

        layout.addStretch()
        return frame

    def _fill_threats_table(self):
        self.threats_table.setRowCount(len(THREATS_DASHBOARD))
        for row, threat in enumerate(THREATS_DASHBOARD):
            self.threats_table.setItem(row, 0, QtWidgets.QTableWidgetItem(threat["name"]))
            sev = threat["severity"]
            if sev == "high":
                sev_text = "Высокий"
            elif sev == "medium":
                sev_text = "Средний"
            else:
                sev_text = "Низкий"
            self.threats_table.setItem(row, 1, QtWidgets.QTableWidgetItem(sev_text))
            self.threats_table.setItem(row, 2, QtWidgets.QTableWidgetItem(threat["time"]))

            status = "В карантине" if threat["status"] == "quarantined" else "Удалено"
            self.threats_table.setItem(row, 3, QtWidgets.QTableWidgetItem(status))

    def update_system_info(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        os_name = platform.system()
        self.system_info_label.setText(f"CPU: {cpu:.0f}%   RAM: {ram:.0f}%   ОС: {os_name}")
        # Можно сюда же добавить hostname, если нужно.


# -------------------------------
# Страница Scanner
# -------------------------------

class ScannerPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.scanning = False
        self.scan_worker = None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(16)

        # Заголовок
        header_layout = QtWidgets.QHBoxLayout()
        header_text = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("Сканер")
        title.setStyleSheet("font-size: 20px; font-weight: 600; color: #ffffff;")
        subtitle = QtWidgets.QLabel("Выберите тип сканирования и проверьте систему на угрозы")
        subtitle.setStyleSheet("color: #a0aec0;")
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header_layout.addLayout(header_text)
        main_layout.addLayout(header_layout)

        # Кнопки типов сканирования
        scan_buttons_layout = QtWidgets.QHBoxLayout()

        self.btn_quick = QtWidgets.QPushButton("Быстрое сканирование")
        self.btn_full = QtWidgets.QPushButton("Полное сканирование")
        self.btn_custom = QtWidgets.QPushButton("Сканирование папки")

        for btn in (self.btn_quick, self.btn_full, self.btn_custom):
            btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet(
                "QPushButton {"
                "background-color: #1f2937;"
                "border-radius: 10px;"
                "padding: 10px 16px;"
                "color: #e5e7eb;"
                "border: 1px solid #374151;"
                "}"
                "QPushButton:hover {"
                "background-color: #111827;"
                "}"
            )

        self.btn_quick.clicked.connect(lambda: self.start_scan("quick"))
        self.btn_full.clicked.connect(lambda: self.start_scan("full"))
        self.btn_custom.clicked.connect(lambda: self.start_scan("custom"))

        scan_buttons_layout.addWidget(self.btn_quick)
        scan_buttons_layout.addWidget(self.btn_full)
        scan_buttons_layout.addWidget(self.btn_custom)
        main_layout.addLayout(scan_buttons_layout)

        # Прогресс
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(
            "QProgressBar {"
            "background-color: #111827;"
            "border-radius: 8px;"
            "border: 1px solid #1f2937;"
            "color: #e5e7eb;"
            "}"
            "QProgressBar::chunk {"
            "background-color: #3b82f6;"
            "border-radius: 8px;"
            "}"
        )
        main_layout.addWidget(self.progress_bar)

        # Инфо снизу прогресса
        info_layout = QtWidgets.QHBoxLayout()
        self.label_progress_text = QtWidgets.QLabel("Прогресс: 0%")
        self.label_files_text = QtWidgets.QLabel("Файлов просканировано: 0")

        for lbl in (self.label_progress_text, self.label_files_text):
            lbl.setStyleSheet("color: #e5e7eb;")

        info_layout.addWidget(self.label_progress_text)
        info_layout.addStretch()
        info_layout.addWidget(self.label_files_text)
        main_layout.addLayout(info_layout)

        # Лог сканирования
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet(
            "QTextEdit {"
            "background-color: #020617;"
            "border-radius: 10px;"
            "border: 1px solid #1f2937;"
            "color: #e5e7eb;"
            "}"
        )
        main_layout.addWidget(self.log, stretch=2)

        # История сканирований (как в правой/нижней части интерфейса)
        history_group = QtWidgets.QGroupBox("История сканирования")
        history_group.setStyleSheet(
            "QGroupBox {"
            "border: 1px solid #1f2937;"
            "border-radius: 10px;"
            "margin-top: 8px;"
            "color: #e5e7eb;"
            "}"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }"
        )
        history_layout = QtWidgets.QVBoxLayout(history_group)

        self.history_list = QtWidgets.QTableWidget()
        self.history_list.setColumnCount(4)
        self.history_list.setHorizontalHeaderLabels(["Тип", "Длительность", "Дата", "Угроз"])
        self.history_list.verticalHeader().setVisible(False)
        self.history_list.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.history_list.setShowGrid(False)
        self.history_list.setStyleSheet(
            "QTableWidget { background-color: #020617; color: #e5e7eb; border: none; }"
            "QHeaderView::section { background-color: #020617; color: #9ca3af; border: none; }"
        )
        self._fill_history()
        self.history_list.horizontalHeader().setStretchLastSection(True)
        self.history_list.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

        history_layout.addWidget(self.history_list)
        main_layout.addWidget(history_group, stretch=1)

    def _fill_history(self):
        self.history_list.setRowCount(len(SCAN_HISTORY))
        for row, item in enumerate(SCAN_HISTORY):
            self.history_list.setItem(row, 0, QtWidgets.QTableWidgetItem(item["type"]))
            self.history_list.setItem(row, 1, QtWidgets.QTableWidgetItem(item["duration"]))
            self.history_list.setItem(row, 2, QtWidgets.QTableWidgetItem(item["date"]))
            self.history_list.setItem(row, 3, QtWidgets.QTableWidgetItem(str(item["threats"])))

    def start_scan(self, scan_type: str):
        if self.scanning:
            return

        self.scanning = True
        self.progress_bar.setValue(0)
        self.label_progress_text.setText("Прогресс: 0%")
        self.label_files_text.setText("Файлов просканировано: 0")
        self.log.clear()
        self.log.append("🔍 Запуск сканирования...\n")

        self.scan_worker = ScanWorker(scan_type)
        self.scan_worker.progress_changed.connect(self.on_progress_changed)
        self.scan_worker.files_changed.connect(self.on_files_changed)
        self.scan_worker.log_message.connect(self.on_log_message)
        self.scan_worker.scan_finished.connect(self.on_scan_finished)
        self.scan_worker.start()

    def on_progress_changed(self, value: int):
        self.progress_bar.setValue(value)
        self.label_progress_text.setText(f"Прогресс: {value}%")

    def on_files_changed(self, files: int):
        self.label_files_text.setText(f"Файлов просканировано: {files}")

    def on_log_message(self, message: str):
        self.log.append(message)

    def on_scan_finished(self, threats_found: int):
        self.scanning = False
        self.log.append("\n✅ Сканирование завершено.")
        if threats_found == 0:
            self.log.append("Угроз не обнаружено.\n")
        else:
            self.log.append(f"Обнаружено угроз: {threats_found}. Рекомендуется переместить их в карантин.\n")


# -------------------------------
# Страница Quarantine
# -------------------------------

class QuarantinePage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.items = list(QUARANTINE_ITEMS)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(16)

        header_layout = QtWidgets.QHBoxLayout()
        header_text = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("Карантин")
        title.setStyleSheet("font-size: 20px; font-weight: 600; color: #ffffff;")
        subtitle = QtWidgets.QLabel("Подозрительные файлы, изолированные от системы")
        subtitle.setStyleSheet("color: #a0aec0;")
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header_layout.addLayout(header_text)
        main_layout.addLayout(header_layout)

        # Таблица
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Файл", "Угроза", "Путь", "Дата", "Размер", "Риск"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(
            "QTableWidget { background-color: #020617; color: #e5e7eb; border: 1px solid #1f2937; }"
            "QHeaderView::section { background-color: #020617; color: #9ca3af; border: none; }"
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table, stretch=2)

        # Кнопки действий
        actions_layout = QtWidgets.QHBoxLayout()
        self.btn_delete = QtWidgets.QPushButton("Удалить")
        self.btn_restore = QtWidgets.QPushButton("Восстановить")
        self.btn_clear = QtWidgets.QPushButton("Очистить карантин")

        for btn in (self.btn_delete, self.btn_restore, self.btn_clear):
            btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet(
                "QPushButton {"
                "background-color: #1f2937;"
                "border-radius: 8px;"
                "padding: 8px 14px;"
                "color: #e5e7eb;"
                "border: 1px solid #374151;"
                "}"
                "QPushButton:hover {"
                "background-color: #111827;"
                "}"
            )

        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_restore.clicked.connect(self.restore_selected)
        self.btn_clear.clicked.connect(self.clear_quarantine)

        actions_layout.addWidget(self.btn_delete)
        actions_layout.addWidget(self.btn_restore)
        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_clear)
        main_layout.addLayout(actions_layout)

        # Итоговый блок
        self.summary_label = QtWidgets.QLabel()
        self.summary_label.setStyleSheet("color: #a0aec0; margin-top: 8px;")
        main_layout.addWidget(self.summary_label)

        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.items))
        total_size = 0.0
        for row, item in enumerate(self.items):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(item["name"]))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(item["threat"]))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(item["path"]))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(item["date"]))
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(item["size"]))
            risk = item["risk"]
            if risk == "high":
                risk_text = "Высокий"
            elif risk == "medium":
                risk_text = "Средний"
            else:
                risk_text = "Низкий"
            self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(risk_text))

            # примитив: вытащим число из "2.4 МБ"
            try:
                size_num = float(item["size"].split()[0].replace(",", "."))
            except Exception:
                size_num = 0.0
            total_size += size_num

        if self.items:
            self.summary_label.setText(
                f"Файлов в карантине: {len(self.items)}   |   Общий размер: {total_size:.1f} МБ"
            )
        else:
            self.summary_label.setText("Карантин пуст. Все системы защищены.")

    def _selected_indexes(self):
        rows = set()
        for idx in self.table.selectedIndexes():
            rows.add(idx.row())
        return sorted(rows)

    def delete_selected(self):
        rows = self._selected_indexes()
        if not rows:
            return
        for row in reversed(rows):
            del self.items[row]
        self.refresh_table()

    def restore_selected(self):
        rows = self._selected_indexes()
        if not rows:
            return
        for row in reversed(rows):
            del self.items[row]
        self.refresh_table()

    def clear_quarantine(self):
        self.items.clear()
        self.refresh_table()


# -------------------------------
# Страница Settings
# -------------------------------

class SettingsPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(16)

        header_layout = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("Настройки")
        title.setStyleSheet("font-size: 20px; font-weight: 600; color: #ffffff;")
        subtitle = QtWidgets.QLabel("Настройте параметры защиты и уведомлений")
        subtitle.setStyleSheet("color: #a0aec0;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)

        # Категории с переключателями
        for category in SETTINGS_DATA:
            group = QtWidgets.QGroupBox(category["category"])
            group.setStyleSheet(
                "QGroupBox {"
                "border: 1px solid #1f2937;"
                "border-radius: 10px;"
                "margin-top: 8px;"
                "color: #e5e7eb;"
                "}"
                "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }"
            )
            vbox = QtWidgets.QVBoxLayout(group)

            for item in category["items"]:
                row = QtWidgets.QHBoxLayout()
                txt = QtWidgets.QVBoxLayout()

                label = QtWidgets.QLabel(item["label"])
                label.setStyleSheet("color: #e5e7eb; font-weight: 500;")
                desc = QtWidgets.QLabel(item["description"])
                desc.setStyleSheet("color: #9ca3af; font-size: 11px;")
                txt.addWidget(label)
                txt.addWidget(desc)

                toggle = QtWidgets.QCheckBox()
                toggle.setChecked(item["enabled"])
                toggle.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
                toggle.setStyleSheet(
                    "QCheckBox::indicator { width: 34px; height: 18px; }"
                    "QCheckBox::indicator:unchecked {"
                    "  border-radius: 9px;"
                    "  background-color: #1f2937;"
                    "  border: 1px solid #4b5563;"
                    "}"
                    "QCheckBox::indicator:checked {"
                    "  border-radius: 9px;"
                    "  background-color: #22c55e;"
                    "  border: 1px solid #16a34a;"
                    "}"
                )

                row.addLayout(txt)
                row.addStretch()
                row.addWidget(toggle)
                vbox.addLayout(row)

            main_layout.addWidget(group)

        main_layout.addStretch()


# -------------------------------
# Основное окно (App + Sidebar)
# -------------------------------

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Antivirus UI (Python)")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        root_layout = QtWidgets.QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Фон
        palette = self.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#020617"))
        self.setPalette(palette)

        # Sidebar
        sidebar = QtWidgets.QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(
            "QFrame {"
            "background-color: #020617;"
            "border-right: 1px solid #111827;"
            "}"
        )
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 16, 16, 16)

        app_title = QtWidgets.QLabel("Antivirus Pro")
        app_title.setStyleSheet("color: #e5e7eb; font-size: 18px; font-weight: 700;")
        sidebar_layout.addWidget(app_title)
        sidebar_layout.addSpacing(8)

        app_version = QtWidgets.QLabel("Версия 1.0 • Защита активна")
        app_version.setStyleSheet("color: #6b7280; font-size: 11px;")
        sidebar_layout.addWidget(app_version)
        sidebar_layout.addSpacing(16)

        self.buttons = {}
        self.current_button_id = None

        self.buttons["dashboard"] = self._create_sidebar_button("Панель управления")
        self.buttons["scanner"] = self._create_sidebar_button("Сканер")
        self.buttons["quarantine"] = self._create_sidebar_button("Карантин")
        self.buttons["settings"] = self._create_sidebar_button("Настройки")

        for key in ["dashboard", "scanner", "quarantine", "settings"]:
            sidebar_layout.addWidget(self.buttons[key])

        sidebar_layout.addStretch()

        footer_label = QtWidgets.QLabel("Статус: защищено")
        footer_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        sidebar_layout.addWidget(footer_label)

        root_layout.addWidget(sidebar)

        # Основная область
        self.stack = QtWidgets.QStackedWidget()
        root_layout.addWidget(self.stack)

        self.page_dashboard = DashboardPage()
        self.page_scanner = ScannerPage()
        self.page_quarantine = QuarantinePage()
        self.page_settings = SettingsPage()

        self.stack.addWidget(self.page_dashboard)   # index 0
        self.stack.addWidget(self.page_scanner)     # index 1
        self.stack.addWidget(self.page_quarantine)  # index 2
        self.stack.addWidget(self.page_settings)    # index 3

        # Привязка кнопок
        self.buttons["dashboard"].clicked.connect(lambda: self.set_view("dashboard"))
        self.buttons["scanner"].clicked.connect(lambda: self.set_view("scanner"))
        self.buttons["quarantine"].clicked.connect(lambda: self.set_view("quarantine"))
        self.buttons["settings"].clicked.connect(lambda: self.set_view("settings"))

        self.set_view("dashboard")

    def _create_sidebar_button(self, text: str) -> QtWidgets.QPushButton:
        btn = QtWidgets.QPushButton(text)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn.setCheckable(True)
        btn.setStyleSheet(
            "QPushButton {"
            "background-color: transparent;"
            "border-radius: 10px;"
            "padding: 10px 12px;"
            "text-align: left;"
            "color: #9ca3af;"
            "font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "background-color: #020617;"
            "}"
            "QPushButton:checked {"
            "background-color: #111827;"
            "color: #ffffff;"
            "}"
        )
        return btn

    def set_view(self, view_id: str):
        if self.current_button_id == view_id:
            return

        # сброс кнопок
        for key, btn in self.buttons.items():
            btn.setChecked(key == view_id)

        if view_id == "dashboard":
            self.stack.setCurrentWidget(self.page_dashboard)
        elif view_id == "scanner":
            self.stack.setCurrentWidget(self.page_scanner)
        elif view_id == "quarantine":
            self.stack.setCurrentWidget(self.page_quarantine)
        elif view_id == "settings":
            self.stack.setCurrentWidget(self.page_settings)

        self.current_button_id = view_id


# -------------------------------
# Запуск приложения
# -------------------------------

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Antivirus Pro")

    # Глобальный стиль (немного «tailwind-dark»)
    app.setStyleSheet("""
        QWidget {
            background-color: #020617;
            color: #e5e7eb;
            font-family: Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            font-size: 13px;
        }
        QScrollBar:vertical {
            background: #020617;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #4b5563;
            border-radius: 4px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
