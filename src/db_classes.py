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
            CREATE TABLE IF NOT EXISTS palette (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                palette_string TEXT NOT NULL,
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

    def get_palettes(self):
        """Возвращает список всех палитр"""
        self.cursor.execute("SELECT * FROM palette")
        return self.cursor.fetchall()

    def get_fonts_by_name(self, name):
        """Возвращает шрифт по имени из таблицы font"""
        self.cursor.execute("SELECT * FROM font WHERE name = ?", (name,))
        return self.cursor.fetchall()

    def get_palette_string_by_name(self, name):
        """Получение палитры в виде строки из таблицы pallets по имени"""
        self.cursor.execute(
            "SELECT palette_string FROM palette WHERE name = ?", (name,))
        return self.cursor.fetchall()

    def create_palette(self, name, palette_string):
        """Создание палитры"""
        self.cursor.execute(
            "INSERT INTO palette (name, palette_string) VALUES (?, ?)",
            (name, palette_string))
        self.connection.commit()

    def delete_palette_by_name(self, name):
        """Удаление палитры"""
        self.cursor.execute("DELETE FROM palette WHERE name = ?", (name,))
        self.connection.commit()

    def close(self):
        """Закрывает соединение с базой данных"""
        self.connection.close()
