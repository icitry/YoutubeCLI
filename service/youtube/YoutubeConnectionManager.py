from enum import Enum

import cv2
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build

from service.youtube.YoutubeCreatorPageState import YoutubeCreatorPageState
from service.youtube.YoutubeHomeState import YoutubeHomeState
from service.youtube.YoutubeSearchState import YoutubeSearchState


class YoutubeResultNav(Enum):
    FIRST = 0
    PREV = -1
    NEXT = 1
    CURRENT = 2


class YoutubeConnectionManager:
    def __init__(self, credentials, on_request_fail):
        self._client = build("youtube", "v3", credentials=credentials)
        self._on_request_fail = on_request_fail

        self._home_page_state = YoutubeHomeState(self._client, on_request_fail, self._get_thumbnail)
        self._creator_page_state = YoutubeCreatorPageState(self._client, on_request_fail, self._get_thumbnail)
        self._search_page_state = YoutubeSearchState(self._client, on_request_fail, self._get_thumbnail)

    def _get_thumbnail(self, url):
        cv2_capture = cv2.VideoCapture(url)
        _, frame = cv2_capture.read()
        if frame is None:
            return None
        return frame.copy()

    def get_home_result(self, nav: YoutubeResultNav):
        if nav == YoutubeResultNav.FIRST:
            self._home_page_state.init_state()
        if nav == YoutubeResultNav.PREV:
            self._home_page_state.nav_prev()
        if nav == YoutubeResultNav.NEXT:
            self._home_page_state.nav_next()

        return self._home_page_state.current

    def get_creator_page_result(self, nav: YoutubeResultNav, creator_id=None):
        if nav == YoutubeResultNav.FIRST:
            if creator_id is None:
                return None
            self._creator_page_state.init_state(creator_id=creator_id)
        if nav == YoutubeResultNav.PREV:
            self._creator_page_state.nav_prev()
        if nav == YoutubeResultNav.NEXT:
            self._creator_page_state.nav_next()

        return self._creator_page_state.current

    def get_search_result(self, nav: YoutubeResultNav, query=None):
        if nav == YoutubeResultNav.FIRST:
            if query is None:
                return None
            self._search_page_state.init_state(query=query)
        if nav == YoutubeResultNav.PREV:
            self._search_page_state.nav_prev()
        if nav == YoutubeResultNav.NEXT:
            self._search_page_state.nav_next()

        return self._search_page_state.current

    def _get_subscriptions_list(self):
        try:
            request = self._client.subscriptions().list(part='snippet', mine=True)
            response = request.execute()
            return response.get('items', [])
        except RefreshError:
            self._on_request_fail()
            return list()

    def _unsubscribe_from_channel(self, channel_id):
        subscriptions = self._get_subscriptions_list()

        for subscription in subscriptions:
            if subscription['snippet']['resourceId']['channelId'] == channel_id:
                subscription_id = subscription['id']
                request = self._client.subscriptions().delete(id=subscription_id)
                request.execute()
                return

    def change_subscription_status(self, creator_id, is_subscribed):
        try:
            if is_subscribed:
                self._client.subscriptions().insert(
                    part='snippet',
                    body={
                        'snippet': {
                            'resourceId': {
                                'kind': 'youtube#channel',
                                'channelId': creator_id
                            }
                        }
                    }
                ).execute()
            else:
                self._unsubscribe_from_channel(creator_id)
        except RefreshError:
            self._on_request_fail()

    def is_subscribed_to_channel(self, channel_id):
        subscriptions = self._get_subscriptions_list()

        for subscription in subscriptions:
            if subscription['snippet']['resourceId']['channelId'] == channel_id:
                return True
        return False

    def change_rating_status(self, video_id, rating):
        if rating not in ['like', 'dislike', 'none']:
            return

        request = self._client.videos().rate(
            id=video_id,
            rating=rating
        )

        try:
            request.execute()
        except RefreshError:
            self._on_request_fail()

    def get_video_rating(self, video_id):
        try:
            request = self._client.videos().getRating(id=video_id)
            response = request.execute()
            return response.get('rating')
        except RefreshError:
            self._on_request_fail()
