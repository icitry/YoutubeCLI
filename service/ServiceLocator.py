from typing import Optional

from service.auth import AuthManager
from service.display import DisplayManager
from service.render import VideoRenderingManager
from service.search import SearchBarManager
from service.subtitle import VideoSubtitlesManager
from service.video import VideoStreamManager
from service.youtube import YoutubeConnectionManager


class ServiceLocator:
    def __init__(self, char_aspect_ratio, should_use_colors, should_render_high_accuracy, should_invert_colors):
        self._display_manager = DisplayManager()
        self._video_rendering_manager = VideoRenderingManager(char_aspect_ratio, should_use_colors,
                                                              should_render_high_accuracy, should_invert_colors)
        self._video_stream_manager = VideoStreamManager()
        self._video_subtitles_manager = VideoSubtitlesManager()
        self._auth_manager = AuthManager()
        self._search_bar_manager = SearchBarManager()

        self._youtube_connection_manager = None

    def init_youtube_connection(self, credentials):
        self._youtube_connection_manager = YoutubeConnectionManager(credentials,
                                                                    self._auth_manager.signal_session_expired)

    @property
    def display_manager(self) -> DisplayManager:
        return self._display_manager

    @property
    def video_rendering_manager(self) -> VideoRenderingManager:
        return self._video_rendering_manager

    @property
    def video_stream_manager(self) -> VideoStreamManager:
        return self._video_stream_manager

    @property
    def video_subtitles_manager(self) -> VideoSubtitlesManager:
        return self._video_subtitles_manager

    @property
    def auth_manager(self) -> AuthManager:
        return self._auth_manager

    @property
    def search_bar_manager(self) -> SearchBarManager:
        return self._search_bar_manager

    @property
    def youtube_connection_manager(self) -> Optional[YoutubeConnectionManager]:
        return self._youtube_connection_manager
