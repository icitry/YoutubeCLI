from service.youtube.YoutubeStateBase import YoutubeStateBase


class YoutubeSearchState(YoutubeStateBase):
    def __init__(self, client, on_request_fail, get_thumbnail_callback):
        super().__init__(client, on_request_fail, get_thumbnail_callback, ['id', 'videoId'])

    def init_state(self, **kwargs):
        self._set_fetch_request(self._client.search(), ['part', 'type', 'q'])

        kwargs['q'] = kwargs.pop('query', '')
        kwargs['part'] = 'snippet'
        kwargs['type'] = 'video'
        super().init_state(**kwargs)
