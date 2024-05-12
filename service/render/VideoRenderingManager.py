import time

from service.render.AsciiFrameConverterUtil import AsciiFrameConverterUtil


class VideoRenderingManager:
    def __init__(self, char_aspect_ratio):
        self._ascii_frame_converter_util = AsciiFrameConverterUtil(char_aspect_ratio)

        self._display_callback = None
        self._subtitles_callback = None

        self._cli_cols = 0
        self._cli_rows = 0

        self._last_render_time = None
        self._render_interval = None

        self._scaling_factor = None
        self._max_frame_width = None

        self._total_frames = None
        self._video_title = None
        self._video_view_count = None
        self._video_creator = None
        self._rating = 'none'

        self._is_video_playing = False

    def init_state(self, state_data):
        self._display_callback = state_data['display_callback']
        self._subtitles_callback = state_data['subtitles_callback']

        target_fps = state_data['target_fps']

        self._render_interval = 1. / target_fps
        self._last_render_time = time.time() - self._render_interval

        self._scaling_factor = state_data['scaling_factor']
        self._max_frame_width = state_data['max_frame_width']

        self._total_frames = state_data['total_frames']
        self._video_title = state_data['video_title']
        self._video_view_count = state_data['video_view_count']
        self._video_creator = state_data['video_creator']
        self._rating = state_data['rating']

    def render_frame(self, frame, frame_count):
        current_time = time.time()
        elapsed_time = current_time - self._last_render_time
        time_delta = self._render_interval - elapsed_time

        if time_delta > 0:
            time.sleep(time_delta)
        self._last_render_time = time.time()

        display_frame_data = self._ascii_frame_converter_util.convert_frame_to_ascii(
            frame, self._cli_cols, self._scaling_factor, self._max_frame_width)

        percent_watched = frame_count / self._total_frames

        subtitles = self._subtitles_callback(percent_watched)

        args = {
            'screen_width': display_frame_data['width'],
            'frame_data': display_frame_data,
            'video_title': self._video_title,
            'video_views': self._video_view_count,
            'rating': self._rating,
            'video_creator': self._video_creator,
            'percent_watched': percent_watched,
            'is_playing': self._is_video_playing
        }

        if len(subtitles) > 0:
            args |= {
                'subtitles': subtitles
            }

        self._display_callback(args)

    def update_cli_dimensions(self, cols, rows):
        self._cli_cols = cols
        self._cli_rows = rows

    def set_video_playing_state(self, is_playing):
        self._is_video_playing = is_playing

    def update_video_rating(self, rating):
        self._rating = rating

    @property
    def ascii_converter(self):
        return self._ascii_frame_converter_util
