import requests
from PyQt5.QtCore import QObject, pyqtSignal

from PyMediaCenter import pythread


def url_param(kwargs):
    param = "?"

    for kwarg in kwargs:
        if type(kwargs[kwarg]) == list:
            param += str(kwarg) + "="
            for el in kwargs[kwarg]:
                if el:
                    param += str(el) + ","
            param = param[:-1] + ";"
        else:
            param += str(kwarg) + "=" + str(kwargs[kwarg])
            param += ";"

    if param[-1] == ";":
        param = param[:-1]

    if len(param) == 1:
        param = ""

    return param


class ServerNotConnected(Exception):
    def __init__(self, message):
        Exception.__init__(self, message + "is not connected")


class Server(QObject):
    task = pyqtSignal('PyQt_PyObject')
    fatal_error = pyqtSignal('PyQt_PyObject')

    def __init__(self, address, port=3000):
        QObject.__init__(self)

        self.address, self.port = address, port
        self.session = requests.Session()
        self.connect("jief", "...")

    def _server_address(self):
        return "http://" + self.address + ":" + str(self.port)

    def connect(self, user, password):
        self.post("/connect", json={"login": user, "password": password})

    def get(self, path, **kwargs):
        try:
            response = self.session.get(self._server_address() + path, **kwargs)
            if response.status_code == 200:
                return response
            elif response.status_code == 404:
                return None
            else:
                self.fatal_error.emit(self._server_address() + " get " + path + " --> " + str(response.status_code))
        except requests.exceptions.ConnectionError:
            self.fatal_error.emit(self._server_address() + " not connected")

    def post(self, path, **kwargs):
        try:
            response = self.session.post(self._server_address() + path, timeout=20, **kwargs)
            if response.status_code == 200:
                return True
            else:
                self.fatal_error.emit(self._server_address() + " post" + path + " --> " + str(response.status_code))
                return False
        except requests.exceptions.ConnectionError:
            self.fatal_error.emit(self._server_address() + " not connected")
            return False

        except requests.exceptions.Timeout:
            return None

    def put(self, path, **kwargs):
        try:
            response = self.session.put(self._server_address() + path, timeout=20, **kwargs)
            if response.status_code == 200:
                return True
            else:
                self.fatal_error.emit(self._server_address() + " post" + path + " --> " + str(response.status_code))
                return False
        except requests.exceptions.ConnectionError:
            self.fatal_error.emit(self._server_address() + " not connected")
            return False

        except requests.exceptions.Timeout:
            return None

    def get_json(self, path):
        raw = self.get(path)
        if raw:
            json = raw.json()
            if json:
                return json
        return None

    def get_stream_path(self):
        return self._server_address() + "/mediaserver/stream"

    @pythread.threaded("httpCom")
    def update_last_time(self, video_id, last_time):
        self.post(f"/api/video/{video_id}", json={"current_time": last_time})

    def get_movies(self):
        for el in self.get_json("/mediaserver/api/movie"):
            yield el

    def get_tvs(self):
        for el in self.get_json("/mediaserver/api/tv"):
            yield el

    def get_persons(self):
        for el in self.get_json("/mediaserver/api/person"):
            yield el

    def get_movie(self, movie_id):
        return self.get_json(f"/mediaserver/api/movie/{movie_id}")

    def get_tv(self, tv_id):
        return self.get_json(f"/mediaserver/api/tv/{tv_id}")

    def get_season(self, tv_id, season):
        return self.get_json(f"/mediaserver/api/tv/{tv_id}/season/{season}")

    def get_episode(self, tv_id, season=None, episode=None):
        if season is None or episode is None:
            return self.get_json(f"/mediaserver/api/tv?episode_id={tv_id}")
        return self.get_json(f"/mediaserver/api/tv/{tv_id}/season/{season}/episode/{episode}")

    def get_person(self, person_id):
        return  self.get_json(f"/mediaserver/api/person/{person_id}")

    def get_video(self, video_id):
        return self.get_json(f"/mediaserver/api/video/{video_id}")

    def get_videos(self, media_type, media_id):
        return self.get_json(f"/mediaserver/api/video?media_type={media_type};media_id={media_id}")

    def get_special(self, media_type, data_type):
        return self.get_json(f"/mediaserver/api/{media_type}/{data_type}")

    def store_rsc(self, path, storage_path):
        response = requests.get(self._server_address() + f"/mediaserver/rsc/original/{path}", stream=True)
        if response.status_code == 200:
            with open(storage_path, 'wb') as f:
                for chunk in response:
                    f.write(chunk)

    def get_rsc(self, path):
        response = requests.get(self._server_address() + f"/mediaserver/rsc/original/{path}")
        if response.status_code == 200:
            return response.content
        return None

    def set_watch_time(self, video_id, watch_time):
        self.put(f"/mediaserver/api/video/{video_id}", json={"watch_time": watch_time})
