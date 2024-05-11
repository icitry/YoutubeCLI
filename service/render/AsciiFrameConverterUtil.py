import cv2


class AsciiFrameConverterUtil:
    _ASCII_CHARS = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjfti*()1[]{}?/\\<>\'\"|*+~=-;:,. '

    def __init__(self, char_aspect_ratio):
        self._char_aspect_ratio = char_aspect_ratio

    def convert_frame_to_ascii(self, frame, cols, scale_factor, max_frame_width):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        width = int(cols * scale_factor)

        if max_frame_width > 0:
            width = min(width, max_frame_width)

        aspect_ratio = frame.shape[1] / frame.shape[0]
        height = int((width / aspect_ratio) * self._char_aspect_ratio)

        resized_frame = cv2.resize(gray_frame, (width, height))

        ascii_frame = ''
        for row in resized_frame:
            for pixel_group in row.reshape(-1, int(1 / scale_factor)):
                intensity = int(pixel_group.mean() / 255 * (len(self._ASCII_CHARS) - 1))
                ascii_frame += self._ASCII_CHARS[intensity]
            ascii_frame += '\n'

        return {
            'content': ascii_frame,
            'width': width
        }

