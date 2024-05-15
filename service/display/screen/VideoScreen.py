from service.display.screen import BaseScreen
from util import get_ellipsized_str, create_video_metadata_str, str_to_lines, get_newline


class VideoScreen(BaseScreen):
    _PLAYBACK_CONSUMED_CHAR = '='
    _PLAYBACK_NOT_YET_CONSUMED_CHAR = '-'
    _PLAYBACK_CURSOR_CHAR = 'o'

    def _create_video_status_bar(self, width, percent_watched, is_playing):
        playback_bar_len = width - 5
        consumed_len = max(0, int(playback_bar_len * percent_watched) - 1)
        not_consumed_len = playback_bar_len - consumed_len - 1

        status_char = '||' if is_playing else ' >'

        return (
            f' {status_char} '
            f'{self._PLAYBACK_CONSUMED_CHAR * consumed_len}'
            f'{self._PLAYBACK_CURSOR_CHAR}'
            f'{self._PLAYBACK_NOT_YET_CONSUMED_CHAR * not_consumed_len} {get_newline()}')

    def render(self, data, menu_str):
        super().render(data, menu_str)

        screen_width = data.get('screen_width')

        frame_data = data['frame_data']
        percent_watched = data['percent_watched']
        is_playing = data['is_playing']
        video_title = data['video_title']
        video_views = data['video_views']
        video_creator = data['video_creator']
        rating = data['rating']
        subtitles = data.get('subtitles', None)

        if rating == 'like':
            rating = 'L'
        elif rating == 'dislike':
            rating = 'D'
        else:
            rating = ''

        render_str = ''

        # Add current frame.
        render_str += frame_data['content']

        if frame_data['width'] > 5:
            # Add current subtitles.
            if subtitles is not None:
                render_str += str_to_lines(subtitles, screen_width)

            # Add playback bar and status.
            render_str += self._create_video_status_bar(screen_width, percent_watched, is_playing)

            # Add video title, ellipsized if necessary.
            render_str += f" {get_ellipsized_str(video_title, screen_width - 2)} {get_newline()}"

            # Add video metadata.
            render_str += create_video_metadata_str(video_views, rating, video_creator, screen_width)

        self.write_to_screen(render_str)
