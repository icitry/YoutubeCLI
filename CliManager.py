import platform
import shutil
import threading
import time
from enum import Enum
from typing import Optional

from service import ServiceLocator
from service.display.DisplayManager import ScreenTags
from service.youtube import YoutubeResultNav

if platform.system() == "Windows":
    import msvcrt
    import sys


    def _getch():
        return msvcrt.getwch()
else:
    import tty
    import termios
    import sys


    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def getch():
    ch = _getch()
    if ch.encode() == b'\x03' or ch.encode() == b'\x1a':
        sys.exit(0)
    return ch


class CliDimensionsChangeHandlerThread(threading.Thread):
    def __init__(self):
        super().__init__()

        self.stop_event = threading.Event()
        self.lock = threading.Lock()

        self._cli_cols = 0
        self._cli_rows = 0
        self._handlers = list()

    def _check_cli_window_size(self):
        cols, rows = shutil.get_terminal_size()

        if self._cli_cols != cols or self._cli_rows != rows:
            self._cli_cols = cols
            self._cli_rows = rows

            for handler in self._handlers:
                handler(self._cli_cols, self._cli_rows)

    def run(self):
        while not self.stop_event.is_set():
            self._check_cli_window_size()
            time.sleep(0.2)

    def stop(self):
        self.stop_event.set()

    def add_handler(self, handler):
        with self.lock:
            self._handlers.append(handler)


class CliInputs(Enum):
    HOME = 72
    CREATOR = 67
    SEARCH = 83
    VIDEO = 86
    SPACE = 32
    BACKSPACE = 8
    ENTER = 13
    ESC = 27
    QUIT = 81
    NAV_PREV = 80
    NAV_NEXT = 78
    NAV_TO_CREATOR = 75
    LIKE = 76
    DISLIKE = 68
    UPDATE_SUBSCRIPTION = 85

    def matches_input(self, keycode):
        return ord(keycode.upper()) == self.value


class CliManager:
    def __init__(self,
                 service_locator: ServiceLocator,
                 scaling_factor,
                 max_frame_width,
                 should_use_subtitles,
                 subtitles_lang):
        self._service_locator = service_locator

        self._scaling_factor = scaling_factor
        self._max_frame_width = max_frame_width

        self._should_use_subtitles = should_use_subtitles
        self._subtitles_lang = subtitles_lang

        self._current_video_id = None
        self._current_video_creator_id = None
        self._current_video_rating = 'none'

        self._is_video_playing = False

        self._current_creator_id = None
        self._current_creator_subscription_status = False

        self._cli_cols = 0
        self._cli_rows = 0

        self._cli_dimensions_change_thread = CliDimensionsChangeHandlerThread()
        self._cli_dimensions_change_thread.daemon = True
        self._cli_dimensions_change_thread.add_handler(self._cli_dimensions_on_change_handler)

        self._cli_dimensions_change_thread.start()

    def _cli_dimensions_on_change_handler(self, cli_cols, cli_rows):
        self._cli_cols = cli_cols
        self._cli_rows = cli_rows
        self._service_locator.video_rendering_manager.update_cli_dimensions(cli_cols, cli_rows)

        self._service_locator.display_manager.set_display_dimensions(cli_cols, cli_rows)

        if self._service_locator.display_manager.current_screen_tag == ScreenTags.HOME:
            self._navigate_to_other_video(
                self._service_locator.youtube_connection_manager.get_home_result, YoutubeResultNav.CURRENT)
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.CREATOR:
            self._navigate_to_other_video(
                self._service_locator.youtube_connection_manager.get_creator_page_result, YoutubeResultNav.CURRENT)
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.SEARCH:
            additional_screen_data = {
                'query': self._service_locator.search_bar_manager.query
            }
            self._navigate_to_other_video(
                self._service_locator.youtube_connection_manager.get_search_result,
                YoutubeResultNav.CURRENT, additional_screen_data)

    def run(self, video_url=None):
        self._service_locator.auth_manager.set_on_credentials_expired(
            self._handle_login_flow
        )

        if video_url is None:
            self._handle_login_flow()
        else:
            if self._service_locator.auth_manager.is_authenticated():
                self._service_locator.init_youtube_connection(self._service_locator.auth_manager.current_user)

            self._service_locator.display_manager.set_screen_visibility(ScreenTags.HOME, True)
            self._service_locator.display_manager.set_screen_visibility(ScreenTags.SEARCH, True)
            self._service_locator.display_manager.set_screen_visibility(ScreenTags.VIDEO, True)
            self._service_locator.display_manager.set_active_screen(ScreenTags.VIDEO)
            self._display_current_screen({
                'video_url': video_url
            })

        while True:
            ch = getch()
            self._on_ch_callback(ch)

    def _handle_login_flow(self):
        if not self._service_locator.auth_manager.is_authenticated():
            self._service_locator.display_manager.issue_message_to_screen(
                'Not authenticated. Log in to access full functionality.')
            self._service_locator.auth_manager.authenticate()

        if not self._service_locator.auth_manager.is_authenticated():
            quit()

        self._service_locator.init_youtube_connection(self._service_locator.auth_manager.current_user)

        self._service_locator.search_bar_manager.reset_state()

        self._service_locator.display_manager.reset_state()
        self._service_locator.display_manager.set_screen_visibility(ScreenTags.HOME, True)
        self._service_locator.display_manager.set_screen_visibility(ScreenTags.SEARCH, True)

        screen_data = self._service_locator.youtube_connection_manager.get_home_result(YoutubeResultNav.FIRST)
        self._service_locator.display_manager.set_active_screen(ScreenTags.HOME)
        self._display_current_screen(screen_data)

    def _display_current_screen(self, screen_data: Optional[dict] = None):
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.VIDEO:
            if screen_data is None:
                self._set_video_playing_state(True)
                return

            self._set_video_playing_state(False)
            self._service_locator.display_manager.set_screen_visibility(ScreenTags.VIDEO, True)
            self._service_locator.display_manager.set_active_screen(ScreenTags.VIDEO)

            current_video_metadata = self._service_locator.video_stream_manager.get_video_metadata(
                screen_data['video_url'], self._should_use_subtitles, self._subtitles_lang)

            self._current_video_id = current_video_metadata['id']
            self._current_video_creator_id = current_video_metadata['creator_id']

            self._service_locator.video_subtitles_manager.set_subtitles_resource(
                current_video_metadata['subtitles'], current_video_metadata['duration'])

            if self._service_locator.auth_manager.is_authenticated():
                self._current_video_rating = self._service_locator.youtube_connection_manager.get_video_rating(
                    self._current_video_id)
            else:
                self._current_video_rating = 'none'

            self._service_locator.video_rendering_manager.init_state({
                'display_callback': self._service_locator.display_manager.render_screen,
                'subtitles_callback': self._service_locator.video_subtitles_manager.current_subtitle,
                'target_fps': current_video_metadata['target_fps'],
                'scaling_factor': self._scaling_factor,
                'max_frame_width': self._max_frame_width,
                'total_frames': current_video_metadata['target_fps'] * current_video_metadata['duration'],
                'video_title': current_video_metadata['title'],
                'video_view_count': current_video_metadata['view_count'],
                'video_creator': current_video_metadata['creator'],
                'rating': self._current_video_rating
            })

            self._set_video_playing_state(True)

            self._service_locator.video_stream_manager.parse_video_stream(
                stream_url=current_video_metadata['stream_url'],
                frame_callback=self._service_locator.video_rendering_manager.render_frame)
        else:
            screen_data = screen_data if screen_data is not None else dict()
            screen_data['screen_width'] = min(self._max_frame_width, self._cli_cols)
            if 'thumbnail' in screen_data:
                screen_data[
                    'rendered_thumbnail'] = (
                    self._service_locator.video_rendering_manager.ascii_converter.convert_frame_to_ascii(
                        screen_data['thumbnail'], self._cli_cols, self._scaling_factor, self._max_frame_width
                    ))
            self._set_video_playing_state(False)
            self._service_locator.display_manager.render_screen(screen_data=screen_data)

    def _set_video_playing_state(self, is_playing):
        self._is_video_playing = is_playing
        self._service_locator.video_rendering_manager.set_video_playing_state(is_playing)
        self._service_locator.video_stream_manager.set_video_state(self._is_video_playing)

    def _on_ch_callback(self, ch):
        if self._service_locator.search_bar_manager.is_active:
            self._on_key_pressed_search_query(ch)
        elif CliInputs.HOME.matches_input(ch):
            self._on_key_home_pressed()
        elif CliInputs.CREATOR.matches_input(ch):
            self._on_key_creator_pressed()
        elif CliInputs.SEARCH.matches_input(ch):
            self._on_key_search_pressed()
        elif CliInputs.VIDEO.matches_input(ch):
            self._on_key_video_pressed()
        elif CliInputs.SPACE.matches_input(ch):
            self._on_key_space_pressed()
        elif CliInputs.ENTER.matches_input(ch):
            self._on_key_enter_pressed()
        elif CliInputs.NAV_PREV.matches_input(ch):
            self._on_key_nav_prev_pressed()
        elif CliInputs.NAV_NEXT.matches_input(ch):
            self._on_key_nav_next_pressed()
        elif CliInputs.NAV_TO_CREATOR.matches_input(ch):
            self._on_key_nav_to_creator_pressed()
        elif CliInputs.LIKE.matches_input(ch):
            self._on_key_like_pressed()
        elif CliInputs.DISLIKE.matches_input(ch):
            self._on_key_dislike_pressed()
        elif CliInputs.UPDATE_SUBSCRIPTION.matches_input(ch):
            self._on_key_subscribe_pressed()
        elif CliInputs.QUIT.matches_input(ch):
            quit()

    def _update_search_query_display_state(self, nav_state: YoutubeResultNav, nav_args=None):
        if nav_args is None:
            nav_args = dict()
        screen_data = self._service_locator.youtube_connection_manager.get_search_result(nav_state, **nav_args)

        screen_data = screen_data if screen_data is not None else dict()
        screen_data |= {
            'query': self._service_locator.search_bar_manager.query
        }
        self._display_current_screen(screen_data)

    def _on_key_pressed_search_query(self, key):
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.SEARCH:
            if CliInputs.BACKSPACE.matches_input(key):
                self._service_locator.search_bar_manager.press_backspace()
                self._update_search_query_display_state(YoutubeResultNav.CURRENT)
            elif CliInputs.ENTER.matches_input(key):
                self._service_locator.search_bar_manager.is_active = False
                self._update_search_query_display_state(YoutubeResultNav.FIRST, {
                    'query': self._service_locator.search_bar_manager.query
                })
            elif CliInputs.ESC.matches_input(key):
                self._service_locator.search_bar_manager.is_active = False
                self._update_search_query_display_state(YoutubeResultNav.CURRENT)
            else:
                self._service_locator.search_bar_manager.append_to_query(key)
                self._update_search_query_display_state(YoutubeResultNav.CURRENT)

    def _on_key_home_pressed(self):
        if not self._service_locator.auth_manager.is_authenticated():
            self._handle_login_flow()

        if self._service_locator.display_manager.current_screen_tag == ScreenTags.HOME:
            return
        if not self._service_locator.display_manager.can_navigate_to_screen(ScreenTags.HOME):
            return

        screen_data = self._service_locator.youtube_connection_manager.get_home_result(
            YoutubeResultNav.CURRENT)
        if screen_data is None:
            screen_data = self._service_locator.youtube_connection_manager.get_home_result(
                YoutubeResultNav.FIRST)
        self._service_locator.display_manager.set_active_screen(ScreenTags.HOME)
        self._display_current_screen(screen_data)

    def _on_key_creator_pressed(self):
        if not self._service_locator.auth_manager.is_authenticated():
            self._handle_login_flow()

        if self._service_locator.display_manager.current_screen_tag == ScreenTags.CREATOR:
            return
        if self._current_creator_id is None:
            return
        if not self._service_locator.display_manager.can_navigate_to_screen(ScreenTags.CREATOR):
            return

        screen_data = self._service_locator.youtube_connection_manager.get_creator_page_result(
            YoutubeResultNav.CURRENT)
        screen_data['is_subscribed'] = self._current_creator_subscription_status
        self._service_locator.display_manager.set_active_screen(ScreenTags.CREATOR)
        self._display_current_screen(screen_data)

    def _on_key_search_pressed(self):
        if not self._service_locator.auth_manager.is_authenticated():
            self._handle_login_flow()

        if self._service_locator.display_manager.current_screen_tag == ScreenTags.SEARCH:
            self._service_locator.search_bar_manager.is_active = True
            self._update_search_query_display_state(YoutubeResultNav.CURRENT)
            return
        if not self._service_locator.display_manager.can_navigate_to_screen(ScreenTags.SEARCH):
            return
        self._service_locator.display_manager.set_active_screen(ScreenTags.SEARCH)
        self._update_search_query_display_state(YoutubeResultNav.CURRENT)

    def _on_key_video_pressed(self):
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.VIDEO:
            return
        if not self._service_locator.display_manager.can_navigate_to_screen(ScreenTags.VIDEO):
            return

        self._service_locator.display_manager.set_active_screen(ScreenTags.VIDEO)
        self._display_current_screen()

    def _on_key_space_pressed(self):
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.VIDEO:
            self._set_video_playing_state(not self._is_video_playing)

    def _on_key_enter_pressed(self):
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.HOME:
            self._navigate_to_current_video_screen(self._service_locator.youtube_connection_manager.get_home_result)
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.CREATOR:
            self._navigate_to_current_video_screen(
                self._service_locator.youtube_connection_manager.get_creator_page_result)
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.SEARCH:
            self._navigate_to_current_video_screen(self._service_locator.youtube_connection_manager.get_search_result)

    def _navigate_to_current_video_screen(self, get_video_data_callback):
        current_video_data = get_video_data_callback(YoutubeResultNav.CURRENT)
        self._service_locator.display_manager.set_screen_visibility(ScreenTags.VIDEO, True)
        self._service_locator.display_manager.set_active_screen(ScreenTags.VIDEO)
        self._display_current_screen({
            'video_url': current_video_data['url']
        })

    def _navigate_to_other_video(self, get_video_data_callback, direction, additional_video_data=None):
        current_video_data = get_video_data_callback(direction)
        if current_video_data is None:
            return
        if additional_video_data is None:
            self._display_current_screen(current_video_data)
        else:
            current_video_data |= additional_video_data
            self._display_current_screen(current_video_data)

    def _on_key_nav_prev_pressed(self):
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.HOME:
            self._navigate_to_other_video(
                self._service_locator.youtube_connection_manager.get_home_result, YoutubeResultNav.PREV)
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.CREATOR:
            additional_screen_data = {
                'is_subscribed': self._current_creator_subscription_status
            }
            self._navigate_to_other_video(self._service_locator.youtube_connection_manager.get_creator_page_result,
                                          YoutubeResultNav.PREV, additional_screen_data)
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.SEARCH:
            additional_screen_data = {
                'query': self._service_locator.search_bar_manager.query
            }
            self._navigate_to_other_video(
                self._service_locator.youtube_connection_manager.get_search_result,
                YoutubeResultNav.PREV, additional_screen_data)

    def _on_key_nav_next_pressed(self):
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.HOME:
            self._navigate_to_other_video(
                self._service_locator.youtube_connection_manager.get_home_result, YoutubeResultNav.NEXT)
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.CREATOR:
            additional_screen_data = {
                'is_subscribed': self._current_creator_subscription_status
            }
            self._navigate_to_other_video(self._service_locator.youtube_connection_manager.get_creator_page_result,
                                          YoutubeResultNav.NEXT, additional_screen_data)
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.SEARCH:
            additional_screen_data = {
                'query': self._service_locator.search_bar_manager.query
            }
            self._navigate_to_other_video(
                self._service_locator.youtube_connection_manager.get_search_result,
                YoutubeResultNav.NEXT, additional_screen_data)

    def _on_key_nav_to_creator_pressed(self):
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.VIDEO:
            self._current_creator_id = self._current_video_creator_id

            screen_data = self._service_locator.youtube_connection_manager.get_creator_page_result(
                YoutubeResultNav.FIRST, self._current_creator_id)

            self._current_creator_subscription_status = (
                self._service_locator.youtube_connection_manager.is_subscribed_to_channel(
                    self._current_creator_id))

            screen_data['is_subscribed'] = self._current_creator_subscription_status

            self._service_locator.display_manager.set_screen_visibility(ScreenTags.CREATOR, True)
            self._service_locator.display_manager.set_active_screen(ScreenTags.CREATOR)
            self._display_current_screen(screen_data)

    def _on_key_like_pressed(self):
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.VIDEO:
            if self._current_video_rating == 'like':
                rating = 'none'
            else:
                rating = 'like'

            self._service_locator.youtube_connection_manager.change_rating_status(
                self._current_video_id, rating)
            self._current_video_rating = rating
            self._service_locator.video_rendering_manager.update_video_rating(rating)

    def _on_key_dislike_pressed(self):
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.VIDEO:
            if self._current_video_rating == 'dislike':
                rating = 'none'
            else:
                rating = 'dislike'

            self._service_locator.youtube_connection_manager.change_rating_status(
                self._current_video_id, rating)
            self._current_video_rating = rating
            self._service_locator.video_rendering_manager.update_video_rating(rating)

    def _on_key_subscribe_pressed(self):
        if self._service_locator.display_manager.current_screen_tag == ScreenTags.CREATOR:
            self._current_creator_subscription_status = not self._current_creator_subscription_status
            self._service_locator.youtube_connection_manager.change_subscription_status(
                self._current_creator_id, self._current_creator_subscription_status)

            screen_data = self._service_locator.youtube_connection_manager.get_creator_page_result(
                YoutubeResultNav.CURRENT)
            screen_data['is_subscribed'] = self._current_creator_subscription_status
            self._display_current_screen(screen_data)
