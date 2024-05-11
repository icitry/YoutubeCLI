import os
import sys
from enum import Enum
from typing import Optional

from service.display.screen import HomeScreen, CreatorScreen, SearchScreen, VideoScreen, BaseScreen
from util import str_list_to_lines, get_menu_item_str


class ScreenTags(Enum):
    HOME = 'HOME'
    CREATOR = 'CREATOR'
    SEARCH = 'SEARCH'
    VIDEO = 'VIDEO'
    NONE = 'NONE'

    def __str__(self):
        return '%s' % self.value


class DisplayManager:
    def __init__(self):
        self._active_screen_tag: ScreenTags = ScreenTags.NONE
        self._active_screen: Optional[BaseScreen] = None

        self._display_height = 0
        self._display_width = 0
        self._display_menu_str = ''

        self._video_has_played = False
        self._creator_was_shown = False

        # Dict where values are the screen and whether it's visible
        self._registered_screens: dict[ScreenTags, [BaseScreen, bool]] = {
            ScreenTags.NONE: [None, False],
            ScreenTags.HOME: [HomeScreen(), False],
            ScreenTags.CREATOR: [CreatorScreen(), False],
            ScreenTags.SEARCH: [SearchScreen(), False],
            ScreenTags.VIDEO: [VideoScreen(), False],
        }

    def _update_menu_str(self):
        self._display_menu_str = str_list_to_lines(
            [get_menu_item_str(str(item)) if item != self._active_screen_tag
             else '{' + get_menu_item_str(str(item)) + '}'
             for item in sorted(self._registered_screens.keys(), key=lambda x: str(x))
             if self._registered_screens[item][1]],
            self._display_width)

    def reset_state(self):
        for screen in self._registered_screens.keys():
            self.set_screen_visibility(screen, False)

    def set_display_dimensions(self, height, width):
        self._display_height = height
        self._display_width = width
        self._update_menu_str()

    def set_active_screen(self, screen_tag: ScreenTags):
        if not self._registered_screens[screen_tag][1]:
            return

        # Hard clear screen depending on os.
        os.system('cls' if os.name == 'nt' else 'clear')

        self._active_screen_tag = screen_tag
        self._active_screen = self._registered_screens[screen_tag][0]
        self._update_menu_str()

    def set_screen_visibility(self, screen_tag: ScreenTags, visible: bool):
        self._registered_screens[screen_tag][1] = visible

    def render_screen(self, screen_data):
        self._active_screen.render(screen_data, self._display_menu_str)

    def issue_message_to_screen(self, msg):
        os.system('cls' if os.name == 'nt' else 'clear')

        clear = '\033c'
        sys.stdout.write(f"{clear}{msg}\n")

    def can_navigate_to_screen(self, screen_tag: ScreenTags):
        return self._registered_screens[screen_tag][1]

    @property
    def current_screen_tag(self):
        return self._active_screen_tag
