import sys

from PyQt6 import uic
from PyQt6.QtGui import QPixmap, QImage, QFontDatabase, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, \
    QFileDialog, QMessageBox, QDialog

from PyQt6 import QtCore
from PIL import Image

from property import Art
from db_classes import Database
from other_windows import CropDialog, PalletCreateDialog

DEFAULT_PAllET = '@%&#*/(,. '


class MainWindow(QMainWindow):
    """
    Класс основного окна
    """

    def __init__(self):
        super().__init__()
        uic.loadUi('../designs/main.ui', self)

        self.setWindowTitle('ASCII Art Converter')
        self.db = Database()

        self.pallet = DEFAULT_PAllET
        self.pixmap = QPixmap('')

        self.actionLoadImage.triggered.connect(self.load_image)
        self.actionBrightnessMode.triggered.connect(self.set_brightness_mode)
        self.actionInverting.triggered.connect(self.invert_action_handler)
        self.actionCrop.triggered.connect(self.crop_action_handler)
        self.actionLineMode.triggered.connect(self.set_line_mode)
        self.actionCreatePallet.triggered.connect(self.create_pallet)

        self.convert_button.clicked.connect(self.convert_btn_handler)
        self.proportionalCheckBox.clicked.connect(self.proportional_handler)
        self.autoSizesButton.clicked.connect(self.set_auto_sizes_handler)
        self.inverting = False

        self.filename = None
        self.original_image = None
        self.art = None
        self.mode = 'brightness'

        self.spin_box_height.setValue(100)
        self.spin_box_width.setValue(200)

        self.brightnessSlider.sliderMoved.connect(self.effect_handler)
        self.contrastSlider.sliderMoved.connect(self.effect_handler)
        self.blurSlider.sliderMoved.connect(self.effect_handler)
        self.opasitySlider.sliderMoved.connect(self.effect_handler)

        self.brightnessSlider.sliderPressed.connect(self.effect_handler)
        self.contrastSlider.sliderPressed.connect(self.effect_handler)
        self.blurSlider.sliderPressed.connect(self.effect_handler)
        self.opasitySlider.sliderPressed.connect(self.effect_handler)

        self.reset_sliders(False)

        self.resetImageButton.clicked.connect(self.image_reset_handler)
        self.populate_font_combo_box()
        self.populate_pallet_combo_box()
        self.fontComboBox.currentIndexChanged.connect(self.font_change_handler)
        self.palletComboBox.currentIndexChanged.connect(self.pallet_change_handler)

    def effect_handler(self):
        """
        Обработчик измененения параметров констраста, яркости, прозрачности, размытия
        вызывает соответсвующие методы изображения, все параметры кроме размытия можно
        менять в отрицательную сторону
        """
        self.art = Art(self.original_image)
        self.art.apply_brightness(self.brightnessSlider.value())
        self.art.apply_contrast(self.contrastSlider.value())
        self.art.apply_transparency(self.opasitySlider.value())
        self.art.apply_blur(self.blurSlider.value())

        self.set_image()

    def set_image(self):
        """Отображение изображения в Qimage"""
        qimage = QImage(self.art.image.tobytes("raw", "RGBA"),
                        self.art.image.width,
                        self.art.image.height, QImage.Format.Format_RGBA8888)

        if self.displayCheckBox.isChecked():
            pixmap = QPixmap.fromImage(qimage)
            self.image_art.setPixmap(pixmap.scaled(self.image_art.size(),
                                                   QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        if self.autoConvertCheckBox.isChecked():
            self.convert_btn_handler()

    def set_brightness_mode(self):
        """
        Смена режима
        """
        self.mode = 'brightness'

    def set_line_mode(self):
        """
        Смена режима
        """
        self.mode = 'line'

    def image_reset_handler(self):
        """
        Возвращает изображение в исходный вид, и ставит значения
        слайдеров параметров в изначальное положение
        """

        self.reset_sliders(True)

    def reset_sliders(self, change_image):
        """
        Ставит значения
        слайдеров параметров в изначальное положение
        """
        self.brightnessSlider.setValue(50)
        self.contrastSlider.setValue(50)
        self.opasitySlider.setValue(50)
        self.blurSlider.setValue(0)
        if change_image:
            self.effect_handler()

    def load_image(self):
        """
        Загрузка изображения, если изображение слишком большое то появляется диалоговое окно
        """
        self.reset_sliders(False)

        self.filename, _ = QFileDialog.getOpenFileName(self, "Select Image",
                                                       "",
                                                       "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")

        if self.filename:
            self.original_image = Image.open(self.filename).convert('RGBA')

            width, height = self.original_image.size

            if width > 1000 or height > 1000:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Изображение слишком большое!")
                msg.setInformativeText(
                    f"Ширина: {width}px, Высота: {height}px.\n"
                    "Хотите уменьшить изображение до 700px по большой стороне?")
                msg.setWindowTitle("Предупреждение")
                msg.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                ret = msg.exec()

                if ret == QMessageBox.StandardButton.Yes:
                    if width > height:
                        new_width = 700
                        new_height = int((700 / width) * height)
                    else:
                        new_height = 700
                        new_width = int((700 / height) * width)

                    self.original_image = self.original_image.resize(
                        (new_width, new_height), Image.Resampling.LANCZOS)

            self.art = Art(self.original_image)
            pixmap = QPixmap(self.filename)
            self.image_art.setPixmap(pixmap.scaled(self.image_art.size(),
                                                   QtCore.Qt.AspectRatioMode.KeepAspectRatio))

    def convert_btn_handler(self):
        """
        Конвертирует изображение по нажатию на кнопку
        """
        if self.filename:
            width = self.spin_box_width.value() if self.spin_box_width.value() > 0 else None
            height = self.spin_box_height.value() if self.spin_box_height.value() > 0 else None

            self.ascii_output.setText(
                self.art.convert(20, 10, self.pallet, height, width, mode=self.mode))

    def populate_font_combo_box(self):
        """Заполняет fontComboBox шрифтами из базы данных"""
        fonts = self.db.get_fonts()
        for font in fonts:
            font_name = font[1]
            self.fontComboBox.addItem(font_name)

    def populate_pallet_combo_box(self):
        """Заполняет pallete ComboBox палитрами из базы данных"""
        pallets = self.db.get_pallets()
        for pallet in pallets:
            self.palletComboBox.addItem(pallet[2])

    def pallet_change_handler(self):
        """
        Смена палитры
        """
        pallet_name = self.palletComboBox.currentText()
        pallet = self.db.get_pallet_string_by_name(pallet_name)[0]
        self.pallet = pallet[0]


    def font_change_handler(self):
        """Обрабатывает изменение выбранного шрифта в fontComboBox"""
        font_name = self.fontComboBox.currentText()

        fonts = self.db.get_fonts_by_name(font_name)

        if fonts:
            font_path = fonts[0][2]

            if font_path == "system":
                font = QFont(font_name)
            else:
                font = QFont(font_path)

            self.ascii_output.setFont(font)

    def proportional_handler(self):
        """
        Переводит ширину и длину в режим пропорции, для изменения
        становится доступна только ширина
        """
        if self.proportionalCheckBox.isChecked():
            self.spin_box_height.setValue(0)
            self.spin_box_height.setReadOnly(True)
        else:
            self.spin_box_height.setReadOnly(False)

    def set_auto_sizes_handler(self):
        """
        Задает автоматически подобранные размеры изображения
        в символах
        """
        if self.proportionalCheckBox.isChecked():
            self.spin_box_width.setValue(int(self.original_image.width // 3))
        else:
            self.spin_box_width.setValue(
                int(self.original_image.width // 3 * 1.5))
            self.spin_box_height.setValue(
                int(self.original_image.height // 3 * 0.5))

    def invert_action_handler(self):
        """
        Для инвертирования изображения (кнопка во вкладке ImageEdit)
        """
        self.reset_sliders(True)
        self.art.apply_inversion()
        self.original_image = self.art.image
        self.set_image()

    def crop_action_handler(self):
        """
        Открывает диалоговое окно для обрезки изображения и применяет изменения.
        """
        if not self.original_image:
            QMessageBox.warning(self, "Ошибка",
                                "Сначала загрузите изображение!")
            return

        crop_dialog = CropDialog(self)
        if crop_dialog.exec() == QDialog.DialogCode.Accepted:
            top, bottom, left, right = crop_dialog.get_crop_values()

            width, height = self.original_image.size
            cropped_image = self.original_image.crop((
                left,
                top,
                width - right,
                height - bottom,
            ))

            self.original_image = cropped_image
            self.art = Art(self.original_image)
            self.set_image()

    def create_pallet(self):
        """
        Создания палитры с помощью отдельного диалога
        """
        pallet_dialog = PalletCreateDialog(self)

        if pallet_dialog.exec() == QDialog.DialogCode.Accepted:

            pallet_name, pallet_as_string = pallet_dialog.get_values()
            if not self.db.get_pallet_string_by_name(pallet_name):
                self.db.create_pallet(
                    pallet_name,
                    pallet_as_string,
                )
                self.palletComboBox.clear()
                self.populate_pallet_combo_box()
            else:
                pallet_dialog.set_error(
                    'ПАЛИТРА С ТАКИМ ИМЕНЕМ УЖЕ СУЩЕСТВУЕТ')



def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
