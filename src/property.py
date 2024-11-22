from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import converter_mods


class Art:
    """
    Класс изображения используется для конвертации изображений в текст,
    а также применения настроек изображения
    """

    def __init__(self, image):
        if isinstance(image, Image.Image):
            self.image = image
        else:
            self.image = Image.open(image)

    def convert(self, symb_height, symb_width,
                palette,
                symbols_vertical=None,
                symbols_horizontal=None,
                mode='brightness',
                inverse=False, ):

        """
        Метод конвертации, возвращает строку, представлюящую изображение
        можно указать 1 из двух режимов
        """

        width, height = self.image.size

        if symbols_horizontal and (symbols_vertical is None):
            scale = symbols_horizontal / width
            symbols_vertical = int(height * scale * (symb_width / symb_height))

        elif symbols_vertical and (symbols_horizontal is None):
            scale = symbols_vertical / height
            symbols_horizontal = int(
                width * scale * (symb_height / symb_width)
            )

        image_resized = self.image.convert('L').resize(
            (symbols_horizontal, symbols_vertical),
            Image.Resampling.LANCZOS)

        if mode == 'brightness':
            return converter_mods.image_to_ascii_brightness_mod(image_resized,
                                                                inverse,
                                                                palette)
        elif mode == 'line':
            return converter_mods.image_to_ascii_line_mod(image_resized)

    def apply_contrast(self, value):
        """
        Регулирует контраст изображения через линейное преобразование.
        """
        factor = (value - 50) / 50.0 + 1.0
        img_array = np.array(self.image,
                             dtype=np.float32)
        mean = np.mean(img_array, axis=(0, 1),
                       keepdims=True)
        result = mean + (
                img_array - mean) * factor
        result = np.clip(result, 0, 255).astype(
            np.uint8)
        self.image = Image.fromarray(result)

    def apply_sharpness(self, value):
        """
        Регулирует резкость изображения
        """
        enhancer = ImageEnhance.Sharpness(self.image)
        factor = (((value - 50) / 50.0) * 6) + 1.0
        self.image = enhancer.enhance(factor)

    def apply_brightness(self, value):
        """
        Регулирует яркость изображения через масштабирование значений пикселей
        """
        if self.image.mode != "RGBA":
            self.image = self.image.convert("RGBA")

        factor = (value - 50) / 50.0 + 1.0
        img_array = np.array(self.image, dtype=np.float32)
        result = img_array * factor
        result = np.clip(result, 0, 255).astype(
            np.uint8)
        self.image = Image.fromarray(result)

    def apply_saturation(self, value):
        """
        Регулирует насыщенность изображения через преобразование RGB в HSL
        """
        if self.image.mode != "RGB":
            self.image = self.image.convert("RGB")
        img_array = np.array(self.image,
                             dtype=np.float32) / 255.0

        r, g, b = img_array[..., 0], img_array[..., 1], img_array[..., 2]
        max_val = np.max(img_array, axis=2)
        min_val = np.min(img_array, axis=2)
        delta = max_val - min_val

        l = (max_val + min_val) / 2.0
        s = np.where(delta == 0, 0, delta / (1 - abs(2 * l - 1)))

        factor = (value - 50) / 50.0 + 1.0
        s = np.clip(s * factor, 0, 1)

        new_img = np.stack([r * s, g * s, b * s], axis=2)
        new_img = np.clip(new_img * 255, 0, 255).astype(np.uint8)
        self.image = Image.fromarray(new_img, "RGB")

    def apply_blur(self, value):
        """
        Регулирует степень размытия изображения
        """
        max_radius = 15
        radius = (value / 100.0) * max_radius
        self.image = self.image.filter(ImageFilter.GaussianBlur(radius=radius))

    def apply_inversion(self):
        """
        Инвертирует изображение формата RGBA
        """
        img_array = np.array(self.image, dtype=np.uint8)

        img_array[..., :3] = 255 - img_array[..., :3]

        self.image = Image.fromarray(img_array, 'RGBA')
