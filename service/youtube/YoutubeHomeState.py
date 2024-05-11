from service.youtube.YoutubeStateBase import YoutubeStateBase


class YoutubeHomeState(YoutubeStateBase):
    def init_state(self, **kwargs):
        self._set_fetch_request(self._client.videos(), ['part', 'chart'])

        kwargs['part'] = 'snippet'
        kwargs['chart'] = 'mostPopular'
        super().init_state(**kwargs)
