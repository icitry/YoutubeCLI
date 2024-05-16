import platform


def get_ellipsized_str(input_str: str, max_length: int):
    if len(input_str) <= max_length:
        return input_str
    else:
        return f'{input_str[:max_length - 2]}..'


def get_menu_item_str(title: str):
    if len(title) < 1:
        return ''
    return f'[{title[0].upper()}]{title[1:].lower()}'


def str_list_to_lines(str_list: list[str], max_line_width: int, center_text=False):
    lines = list()
    current_line = ''
    for word in str_list:
        if len(current_line) + len(word) > max_line_width:
            current_line = current_line.rstrip()
            total_padding = max_line_width - len(current_line)
            if center_text:
                padding = int(total_padding / 2)
                lines.append(f"{' ' * padding}{current_line}{' ' * (total_padding - padding)}")
            else:
                lines.append(f"{current_line}{' ' * total_padding}")
            current_line = ''

        if len(word) > max_line_width:
            for i in range(0, len(word), max_line_width):
                line = word[i:i + max_line_width]
                total_padding = max_line_width - len(line)
                if center_text:
                    padding = int(total_padding / 2)
                    line = f"{' ' * padding}{line}{' ' * padding}"
                else:
                    line = f"{line}{' ' * (max_line_width - len(line))}"

                lines.append(line)
        else:
            current_line += word + ' '

    if current_line:
        current_line = current_line.rstrip()
        total_padding = max_line_width - len(current_line)
        if center_text:
            padding = int(total_padding / 2)
            lines.append(f"{' ' * padding}{current_line}{' ' * (total_padding - padding)}")
        else:
            lines.append(f"{current_line}{' ' * total_padding}")

    lines = get_newline().join(lines) + get_newline()

    return lines


def str_to_lines(input_str: str, max_line_width: int):
    return str_list_to_lines(input_str.split(), max_line_width, True)


def create_video_metadata_str(video_views, rating, video_creator, width):
    video_views = f'{video_views} views' if len(video_views) > 1 else ''
    rating_str = f' | [{rating}]' if len(rating) > 0 else ''
    video_creator_max_len = width - len(video_views) - len(rating_str) - 3
    video_creator = get_ellipsized_str(video_creator, video_creator_max_len)

    return (f" {video_creator}{' ' * (width - len(video_creator) - len(video_views) - len(rating_str) - 2)}"
            f"{video_views}{rating_str} {get_newline()}")


def get_abbreviated_view_count(video_views, precision=2):
    view_abbr_suffixes = ['', 'K', 'M', 'B', 'T']
    suffix_index = 0

    video_views = int(video_views)

    while abs(video_views) >= 1000 and suffix_index < len(view_abbr_suffixes) - 1:
        suffix_index += 1
        video_views /= 1000.0

    return f"{video_views:.{precision}f}{view_abbr_suffixes[suffix_index]}"


def create_video_navigation_info_str(width):
    if width < 8:
        return ''

    if width >= 15:
        return f" [P]rev{' ' * (width - 14)}[N]ext {get_newline()}"

    return (f"{(width - 6) / 2}[P]rev{(width - 6) / 2}{get_newline()}"
            f"{(width - 6) / 2}[N]ext{(width - 6) / 2}{get_newline()}")


def get_search_bar_str(query: str, width: int):
    if width < 6:
        return ''

    horizontal_margin = '-' * width + get_newline()
    query = query.split()

    max_line_width = width - 4

    lines = list()
    current_line = ''
    for word in query:
        if len(current_line) + len(word) > max_line_width:
            current_line = current_line.rstrip()
            lines.append(f"| {current_line}{' ' * (max_line_width - len(current_line))} |")
            current_line = ''

        if len(word) > max_line_width:
            for i in range(0, len(word), max_line_width):
                line = word[i:i + max_line_width]
                line = f"| {line}{' ' * (max_line_width - len(line))} |"
                lines.append(line)
        else:
            current_line += word + ' '

    if current_line:
        current_line = current_line.rstrip()
        lines.append(f"| {current_line}{' ' * (max_line_width - len(current_line))} |")

    lines = get_newline().join(lines) + get_newline()

    return f'{horizontal_margin}{lines}{horizontal_margin}'


def get_newline():
    return '\n' if platform.system() == "Windows" else '\r\n'
