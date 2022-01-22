import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from pathlib import Path
import os

# Default font path
# eg. C:\Windows\Fonts
default_font_path = ((Path(os.environ['WINDIR']) / 'Fonts')
                     / 'AlibabaPuHuiTi-2-85-BOLD.ttf')


def smooth_glass_effect(image_frame):
    # The higher the number, the stronger the effect is
    combined = cv2.blur(image_frame, [25, 25])
    return combined


def metaverse_effect(image_frame):
    height, width, channels = image_frame
    rbg_zone = np.random.randint(255, size=(height, width, channels), dtype=np.uint8)
    combined = np.bitwise_xor(rbg_zone, image_frame)
    return combined


def multicam_effect(image_frame):
    # to stack horizontally
    # combined = np.concatenate((rbg_zone, cv2_frame_rgb), axis=1)
    combined = np.concatenate((image_frame, image_frame), axis=1)
    combined = np.concatenate((combined, combined), axis=0)
    return combined


def add_timestamp(image_frame, file_path, font_path=None):
    height, width, channels = image_frame.shape
    cv2_frame_rgb = cv2.cvtColor(image_frame, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv2_frame_rgb)

    draw = ImageDraw.Draw(pil_im)
    font_path = font_path if font_path else default_font_path
    title_font = ImageFont.truetype(str(font_path), 300)
    draw.text((width * 0.618-600, height * 0.382 - 300), '觉知日记', font=title_font)
    timestamp_font = ImageFont.truetype(str(font_path), 200)
    draw.text((width * (1 - 0.618) - 600, height * 0.618 - 100), file_path.stem, font=timestamp_font)

    return cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
