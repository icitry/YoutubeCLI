class SearchBarManager:
    def __init__(self):
        self._is_active = False
        self._current_query = ''

    def reset_state(self):
        self._is_active = False
        self._current_query = ''

    def append_to_query(self, ch):
        self._current_query += ch

    def press_backspace(self):
        if len(self._current_query) > 0:
            self._current_query = self._current_query[:-1]

    @property
    def query(self):
        if not self._is_active and self._current_query == '':
            return '[S]earch'
        if self._is_active:
            return f'{self._current_query}_'
        return self._current_query

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value
