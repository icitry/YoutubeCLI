import threading

import cv2
import yt_dlp

from util import get_abbreviated_view_count


class VideoStreamHandlerThread(threading.Thread):
    def __init__(self, ):
        super().__init__()

        self.stop_event = threading.Event()
        self.lock = threading.Lock()

        self._stream_url = None
        self._frame_callback = None
        self._cv2_capture = None
        self._frame = None
        self._frame_count = 0

        self._is_playing = False

    def set_video_player(self, stream_url, frame_callback):
        self._stream_url = stream_url
        self._frame_callback = frame_callback

        self._cv2_capture = cv2.VideoCapture(self._stream_url)
        self._frame_count = 0
        self._is_playing = True

    def run(self):
        while not self.stop_event.is_set():
            if not self._is_playing or self._cv2_capture is None:
                continue

            _, self._frame = self._cv2_capture.read()
            if self._frame is None:
                break

            self._frame_count += 1
            self._frame_callback(self._frame, self._frame_count)

        self._cv2_capture.release()
        self._is_playing = False

    def stop(self):
        self.stop_event.set()

    def update_video_state(self, is_playing):
        with self.lock:
            self._is_playing = is_playing

            if not self._is_playing and self._frame_callback is not None:
                self._frame_callback(self._frame, self._frame_count)


class VideoStreamManager:
    class FakeLogger(object):
        # Outta here with that shi-
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            pass

    _yt_dl_opts = {
        'quiet': True,
        'logger': FakeLogger(),
        'retries': 99,
        'noprogress': True,
        'format': 'worst',
    }

    def __init__(self):
        self._video_stream_handler_thread = VideoStreamHandlerThread()
        self._video_stream_handler_thread.daemon = True
        self._video_stream_handler_thread.start()

        self._is_playing = False

    def get_video_metadata(self, video_url):
        ytdl = yt_dlp.YoutubeDL(self._yt_dl_opts)
        video_info = ytdl.extract_info(video_url, download=False)

        return {
            'id': video_info['id'],
            'thumbnail': video_info['thumbnail'],
            'stream_url': video_info['url'],
            'target_fps': video_info['fps'],
            'title': video_info['title'],
            'duration': video_info['duration'],
            'is_live': video_info['is_live'],
            'creator': video_info['uploader'],
            'creator_id': video_info['channel_id'],
            'view_count': get_abbreviated_view_count(video_info['view_count']),
        }

    def parse_video_stream(self, stream_url, frame_callback):
        self._video_stream_handler_thread.set_video_player(stream_url, frame_callback)

    def set_video_state(self, is_playing):
        self._video_stream_handler_thread.update_video_state(is_playing)
