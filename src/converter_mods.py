import numpy as np
import cv2


def image_to_ascii_brightness_mod(image, inverse, pallet):
    """
    Режим конвертации, использует простую яркость пикселей, чтобы определить
    какому символу палитры он соответствует
    """
    if inverse:
        pallet = pallet[::-1]
    else:
        pallet = pallet

    pixels = image.load()
    art_string = ''

    for j in range(image.height):
        for i in range(image.width):
            color = pixels[i, j]
            pallet_color = max(round((color / 255) * len(pallet) - 1), 0)
            art_string += pallet[pallet_color]
        art_string += '\n'

    return art_string


def image_to_ascii_line_mod(image, low_threshold=50,
                            high_threshold=150):

    """
    Режим конвертации, использует направления границ на изображении, для нахождения
    границ применяется библиотека компьютерного зрения opencv
    """
    SYMBOLS = {
        'horizontal': '-',
        'vertical': '|',
        'diag_up': '/',
        'diag_down': '\\',
        'none': ' '
    }

    image_array = np.array(image)
    edges = cv2.Canny(image_array, low_threshold, high_threshold)

    ascii_art = []

    for i in range(1, image.height - 1):
        line = ""
        for j in range(1, image.width - 1):
            if edges[i, j] == 0:
                line += SYMBOLS['none']
            else:

                region = edges[i - 1:i + 2, j - 1:j + 2]

                gx = (region[0, 2] + region[1, 2] + region[2, 2]) - (
                        region[0, 0] + region[1, 0] + region[2, 0])
                gy = (region[2, 0] + region[2, 1] + region[2, 2]) - (
                        region[0, 0] + region[0, 1] + region[0, 2])

                if abs(gx) > abs(gy):
                    line += SYMBOLS['horizontal']
                elif abs(gy) > abs(gx):
                    line += SYMBOLS['vertical']
                elif gx > 0 and gy > 0:
                    line += SYMBOLS['diag_down']
                else:
                    line += SYMBOLS['diag_up']
        ascii_art.append(line)

    return "\n".join(ascii_art)
