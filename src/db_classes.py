import sqlite3
from PyQt6.QtGui import QFontDatabase


class Database:
    """
    Класс для работы с бд, чтобы не писать SQL в других файлах
    """

    def __init__(self, db_name="app_data.db"):
        """Создает или подключается к базе данных и инициализирует таблицы."""
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pallet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pallet_string TEXT NOT NULL,
                name TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS font (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                font_path TEXT NOT NULL
            )
        ''')

        self.populate_fonts_table()

    def populate_fonts_table(self):
        """
        Добавляет все доступные шрифты в таблицу font, если она пустая
        """

        self.cursor.execute("SELECT COUNT(*) FROM font")
        if self.cursor.fetchone()[0] == 0:  # Если таблица пуста
            font_families = QFontDatabase.families()
            for font_name in font_families:
                self.cursor.execute(
                    "INSERT INTO font (name, font_path) VALUES (?, ?)",
                    (font_name, "system"))
            self.connection.commit()

    def add_custom_font(self, font_path, font_name=None):
        """
        Добавляет пользовательский шрифт в базу данных и загружает его в систему
        """
        if not font_name:
            font_name = font_path.split("/")[
                -1]

        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            return

        self.cursor.execute("INSERT INTO font (name, font_path) VALUES (?, ?)",
                            (font_name, font_path))
        self.connection.commit()

    def get_fonts(self):
        """Возвращает список всех шрифтов"""
        self.cursor.execute("SELECT * FROM font")
        return self.cursor.fetchall()

    def get_pallets(self):
        """Возвращает список всех палитр"""
        self.cursor.execute("SELECT * FROM pallet")
        return self.cursor.fetchall()

    def get_fonts_by_name(self, name):
        """Возвращает шрифт по имени из таблицы font."""
        self.cursor.execute("SELECT * FROM font WHERE name = ?", (name,))
        return self.cursor.fetchall()

    def get_pallet_string_by_name(self, name):
        self.cursor.execute("SELECT pallet_string FROM pallet WHERE name = ?", (name,))
        return self.cursor.fetchall()

    def create_pallet(self, name, pallet_string):
        self.cursor.execute(
            "INSERT INTO pallet (name, pallet_string) VALUES (?, ?)",
            (name, pallet_string))
        self.connection.commit()

    def close(self):
        """Закрывает соединение с базой данных"""
        self.connection.close()
