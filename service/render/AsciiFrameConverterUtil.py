import cv2

from util import get_newline


class ANSIConstants:
    # Approximate colors, used for fast mappings.
    COLORS = {
        (0, 0, 0): '\033[30m',
        (255, 0, 0): '\033[31m',
        (0, 255, 0): '\033[32m',
        (255, 255, 0): '\033[33m',
        (0, 0, 255): '\033[34m',
        (255, 0, 255): '\033[35m',
        (0, 255, 255): '\033[36m',
        (255, 255, 255): '\033[37m',
    }

    RESET = '\033[0m'

    @staticmethod
    def closest_ansi_color(pixel):
        min_distance = float('inf')
        closest_ansi_color = '\033[37m'
        for mapped_rgb, ansi_color in ANSIConstants.COLORS.items():
            distance = sum(abs(a - b) for a, b in zip(pixel, mapped_rgb))
            if distance < min_distance:
                min_distance = distance
                closest_ansi_color = ansi_color
        return closest_ansi_color


class AsciiFrameConverterUtil:
    _ASCII_CHARS = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjfti*()1[]{}?/\\<>\'\"|*+~=-;:,. '

    def __init__(self, char_aspect_ratio, should_use_color):
        self._char_aspect_ratio = char_aspect_ratio
        self._should_use_color = should_use_color

    def _get_color_char(self, pixel_group, char):
        closest_ansi_color = ANSIConstants.closest_ansi_color(pixel_group)
        return f'{closest_ansi_color}{char}{ANSIConstants.RESET}'

    def convert_frame_to_ascii(self, frame, cols, scale_factor, max_frame_width):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        width = int(cols * scale_factor)

        if max_frame_width > 0:
            width = min(width, max_frame_width)

        aspect_ratio = frame.shape[1] / frame.shape[0]
        height = int((width / aspect_ratio) * self._char_aspect_ratio)

        resized_frame = cv2.resize(gray_frame, (width, height))

        if self._should_use_color:
            frame = cv2.resize(frame, (width, height))

        ascii_frame = ''
        for x, row in enumerate(resized_frame):
            for y, pixel_group in enumerate(row):
                intensity = int(pixel_group.mean() / 255 * (len(self._ASCII_CHARS) - 1))
                if self._should_use_color:
                    char = self._get_color_char(frame[x][y], self._ASCII_CHARS[intensity])
                else:
                    char = self._ASCII_CHARS[intensity]
                ascii_frame += char
            ascii_frame += get_newline()

        return {
            'content': ascii_frame,
            'width': width
        }
