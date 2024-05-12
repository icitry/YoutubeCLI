from datetime import datetime
from io import StringIO

import requests
import webvtt


class VideoSubtitlesManager:
    def __init__(self):
        self._src = list()
        self._index = 0
        self._video_duration = 0

    def _parse_timestamp_str(self, timestamp_str):
        try:
            dt = datetime.strptime(timestamp_str, '%H:%M:%S.%f')
            seconds = (dt.hour * 3600) + (dt.minute * 60) + dt.second + (dt.microsecond / 1000000)
            return seconds
        except ValueError:
            return None

    def set_subtitles_resource(self, subtitles_info, video_duration):
        self._video_duration = video_duration
        self._src.clear()
        self._index = 0

        if subtitles_info is None:
            return

        url = subtitles_info['url']
        response = requests.get(url)
        if not response.ok:
            return

        buffer = StringIO(response.text)

        for caption in webvtt.read_buffer(buffer):
            start = self._parse_timestamp_str(caption.start)
            end = self._parse_timestamp_str(caption.end)

            if start is None or end is None:
                continue

            self._src.append({
                'start': start,
                'end': end,
                'content': caption.text.replace('\t', ' ' * 4)
            })

    def current_subtitle(self, progress):
        timestamp = progress * self._video_duration

        if self._index >= len(self._src):
            return ''

        if self._src[self._index]['end'] < timestamp:
            self._index += 1

        if self._index >= len(self._src):
            return ''

        if self._src[self._index]['start'] > timestamp:
            return ''

        return self._src[self._index]['content']
