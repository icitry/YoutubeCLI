from service.display.screen import BaseScreen
from util import get_ellipsized_str, create_video_navigation_info_str, get_newline


class CreatorScreen(BaseScreen):
    def render(self, data, menu_str):
        super().render(data, menu_str)

        screen_width = data.get('screen_width')

        if 'thumbnail' not in data.keys():
            self.write_to_screen('Could not load creator screen.')
            return

        title = data['title']
        creator = data['creator']
        thumbnail = data['rendered_thumbnail']
        is_subscribed = data['is_subscribed']

        render_str = ''

        if thumbnail['width'] > 5:
            # Add creator name.
            subscription_status = 'Y' if is_subscribed else 'N'
            render_str += (f" {get_ellipsized_str(f'Creator: {creator}', screen_width - 14)} "
                           f"| Subscribed: {subscription_status} {get_newline()}")

        # Add nav controls info.
        render_str += create_video_navigation_info_str(screen_width)

        # Add thumbnail.
        render_str += thumbnail['content']

        if thumbnail['width'] > 5:
            # Add video title, ellipsized if necessary.
            render_str += f" {get_ellipsized_str(title, screen_width - 2)} {get_newline()}"

        self.write_to_screen(render_str)
