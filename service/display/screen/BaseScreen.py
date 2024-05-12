import sys


class BaseScreen:
    def __init__(self):
        self._menu_str = ''

    def render(self, data, menu_str):
        self._menu_str = menu_str

    def write_to_screen(self, data: str):
        data = data + '\n' if len(data) > 0 and data[-1] != '\n' else data

        clear = '\033c'
        sys.stdout.write(f"{clear}{data}{self._menu_str}\n")

