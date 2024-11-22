from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from db_classes import Database


class CropDialog(QDialog):
    """
    Диалоговое окно для ввода параметров обрезки изображения.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image crop")

        uic.loadUi('../designs/crop.ui', self)

        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    def get_crop_values(self):
        """
        Возвращает значения для обрезки (сверху, снизу, слева, справа).
        """
        return (
            self.topSpinBox.value(),
            self.bottomSpinBox.value(),
            self.leftSpinBox.value(),
            self.rightSpinBox.value(),
        )


class PaletteCreateDialog(QDialog):
    """
    Окно для создания палитры
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('palette Creator')

        uic.loadUi('../designs/palette_creator.ui', self)

    def get_values(self):
        """
        Получения значения для последующего занесения в бд
        """
        return (
            self.nameEdit.text(),
            self.paletteEdit.text(),
        )


class PaletteManager(QDialog):
    def __init__(self, parent=None):
        """
        Окно управления палитрами
        """
        super().__init__(parent)
        uic.loadUi('../designs/palette_manager.ui', self)
        print('asda')
        self.db = Database()

        self.deleteButton.clicked.connect(self.delete_selected_palette)
        self.closeButton.clicked.connect(self.close)

        self.load_palettes()

    def load_palettes(self):
        """Загружает палитры из базы данных и отображает их в таблице"""
        self.tableWidget.setRowCount(0)
        palettes = self.db.get_palettes()

        for row, palette in enumerate(palettes):
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(palette[2]))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(palette[1]))

    def delete_selected_palette(self):
        """Удаляет выбранную палитру из базы данных и таблицы"""
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Ошибка',
                                'Выберите палитру для удаления.')
            return

        palette_name = self.tableWidget.item(selected_row, 0).text()
        confirm = QMessageBox.question(
            self,
            'Подтверждение удаления',
            f'Вы уверены, что хотите удалить палитру "{palette_name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.db.delete_palette_by_name(palette_name)

            self.tableWidget.removeRow(selected_row)
            QMessageBox.information(self, 'Успех',
                                    f'Палитра "{palette_name}" была удалена.')
