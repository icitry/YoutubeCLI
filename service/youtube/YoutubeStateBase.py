import threading

from google.auth.exceptions import RefreshError


class VideoFetchingThread(threading.Thread):
    def __init__(self,
                 add_video_callback,
                 update_page_token_callback,
                 get_thumbnail_callback,
                 on_request_fail_callback,
                 signal_fetch_done,
                 request_method,
                 request_params,
                 video_id_json_path):
        super().__init__()

        self.lock = threading.Lock()

        self._add_video_callback = add_video_callback
        self._update_page_token_callback = update_page_token_callback
        self._request_method = request_method
        self._request_params = request_params
        self._on_request_fail_callback = on_request_fail_callback
        self._video_id_json_path = video_id_json_path
        self._get_thumbnail_callback = get_thumbnail_callback
        self._signal_fetch_done = signal_fetch_done

    def run(self):
        try:
            response = self._request_method.list(**self._request_params).execute()
        except RefreshError:
            self._on_request_fail_callback()
            return

        if "nextPageToken" in response:
            self._update_page_token_callback(response["nextPageToken"])

        for item in response["items"]:
            snippet = item.get('snippet', None)

            video_id = item
            for tag in self._video_id_json_path:
                video_id = video_id[tag]

            to_add = dict()

            if snippet is not None:
                to_add = {
                    'title': snippet["title"],
                    'creator': snippet["channelTitle"],
                    'thumbnail': self._get_thumbnail_callback(snippet["thumbnails"]["medium"]["url"]),
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                }

            skip = False
            for val in to_add.values():
                if val is None:
                    skip = True
                    break
            if not skip:
                self._add_video_callback(to_add)

        self._signal_fetch_done()


class YoutubeStateBase:
    def __init__(self, client, on_request_fail, get_thumbnail_callback, video_id_json_path=None, results_per_fetch=15):
        if video_id_json_path is None:
            video_id_json_path = ['id']

        self._client = client
        self._on_request_fail = on_request_fail
        self._get_thumbnail = get_thumbnail_callback
        self._video_id_json_path = video_id_json_path

        self._videos = list()
        self._index = 0

        self._ratio_viewed_trigger_fetch = 0.8

        self._request_method = None
        self._request_params = None
        self._next_page_token = None
        self._results_per_fetch = results_per_fetch

        self._is_fetching = False
        self._fetching_thread = None

    def _set_fetch_request(self, fetch_request_method, fetch_request_params):
        self._request_method = fetch_request_method
        self._request_params = fetch_request_params

    def _update_page_token_callback(self, page_token):
        self._next_page_token = page_token
        self._request_method.pageToken = self._next_page_token

    def _add_video_callback(self, video_data):
        self._videos.append(video_data)

    def _signal_fetch_done(self):
        self._is_fetching = False

    def _fetch_new(self, should_wait=False):
        if self._request_method is None or self._is_fetching:
            return

        request_params = dict()
        if self._next_page_token is not None:
            request_params |= {'pageToken': self._next_page_token}
        request_params |= {'maxResults': self._results_per_fetch}
        request_params |= {k: getattr(self, f'_fetch_request_param_{k}') for k in self._request_params}

        self._is_fetching = True
        self._fetching_thread = VideoFetchingThread(
            self._add_video_callback,
            self._update_page_token_callback,
            self._get_thumbnail,
            self._on_request_fail,
            self._signal_fetch_done,
            self._request_method,
            request_params,
            self._video_id_json_path
        )
        self._fetching_thread.daemon = True
        self._fetching_thread.start()

        if should_wait:
            self._fetching_thread.join()

    def init_state(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, f'_fetch_request_param_{k}', v)

        self._fetching_thread = None

        self._videos.clear()
        self._index = 0
        self._next_page_token = None

        self._fetch_new(should_wait=True)

    def nav_prev(self):
        if self._index == 0:
            return
        self._index -= 1

    def nav_next(self):
        if self._index == len(self._videos) - 1:
            return
        self._index += 1

        if self._index >= len(self._videos) * self._ratio_viewed_trigger_fetch:
            self._fetch_new()

    @property
    def current(self):
        if self._index >= len(self._videos):
            return None
        return self._videos[self._index]
