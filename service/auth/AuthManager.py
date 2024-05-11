import os
import pickle
from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


class AuthManager:
    _SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    _auth_creds_path = "./data/auth_creds.pkl"
    _client_secret_path = './auth/client_secret.json'

    def __init__(self):
        self._current_user = None
        self._on_credentials_expired_callback = None

        self._try_load_current_user()

    def _try_load_current_user(self):
        if os.path.exists(self._auth_creds_path):
            with open(self._auth_creds_path, "rb") as token:
                self._current_user = pickle.load(token)

    def _refresh_access_token(self):
        try:
            self._current_user.refresh(Request())
        except RefreshError:
            flow = InstalledAppFlow.from_client_secrets_file(
                self._client_secret_path, self._SCOPES)
            self._current_user = flow.run_local_server(port=0)

        with open(self._auth_creds_path, "wb+") as token:
            pickle.dump(self._current_user, token)

    def authenticate(self):
        self._try_load_current_user()

        if not self._current_user or not self._current_user.valid:
            if self._current_user and self._current_user.expired and self._current_user.refresh_token:
                self._refresh_access_token()
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self._client_secret_path, self._SCOPES)
                self._current_user = flow.run_local_server(port=0)

            if self._current_user is None:
                return None

            if not os.path.exists(self._auth_creds_path):
                auth_creds_path = Path(self._auth_creds_path)
                auth_creds_path.parent.mkdir(exist_ok=True, parents=True)

            with open(self._auth_creds_path, "wb+") as token:
                pickle.dump(self._current_user, token)
        return self._current_user
    
    def is_authenticated(self):
        return self._current_user is not None

    def set_on_credentials_expired(self, callback):
        self._on_credentials_expired_callback = callback

    def signal_session_expired(self):
        self._on_credentials_expired_callback()

    @property
    def current_user(self):
        return self._current_user
