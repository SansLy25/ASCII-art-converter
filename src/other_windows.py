from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, \
    QSpinBox, QPushButton, QWidget


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

class PalletCreateDialog(QDialog):
    """
    Окно для создания палитры
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Pallet Creator')

        uic.loadUi('../designs/pallet_creator.ui', self)

    def get_values(self):
        """
        Получения значени для последующего занесения в бд
        """
        return (
            self.nameEdit.text(),
            self.palletEdit.text(),
        )

    def set_error(self, error_text):
        """
        Просто установка ошибок
        """
        self.errorLabel.setText(error_text)


class BrowsePallets(QWidget):
    def __init__(self, parent=None):
        self.setWindowTitle('Browse Pallets')
