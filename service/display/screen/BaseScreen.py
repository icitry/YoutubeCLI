import sys

from util import get_newline


class BaseScreen:
    def __init__(self):
        self._menu_str = ''

    def render(self, data, menu_str):
        self._menu_str = menu_str

    def write_to_screen(self, data: str):
        data = data + get_newline() if len(data) > 0 and not data.endswith(get_newline()) else data

        clear = '\033c'
        sys.stdout.write(f"{clear}{data}{self._menu_str}{get_newline()}")

