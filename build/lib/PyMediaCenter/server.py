import requests

from PyQt5.QtCore import QObject, pyqtSignal

from PyMediaCenter import pythread

from PyMediaCenter.medialibrary import MEDIA_TYPE_MOVIE, MEDIA_TYPE_TV


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

    def __init__(self, address, port=4242):
        QObject.__init__(self)

        self.address, self.port = address, port
        self.session = requests.Session()

    def _server_address(self):
        return "http://" + self.address + ":" + str(self.port)

    def get(self, path, **kwargs):
        try:
            response = self.session.get(self._server_address() + path, **kwargs)
            if response.status_code == 200:
                return response
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
                self.fatal_error.emit(self._server_address() + " get " + path + " --> " + str(response.status_code))
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
        return []

    def get_stream_path(self, video):
        return self._server_address() + "/stream/" + str(video["VideoID"])

    @pythread.threaded("httpCom")
    def update_last_time(self, video_id, last_time):
        self.post("/media/edit", json={"Timestamp": [{"VideoID": video_id,
                                                      "Timestamp": last_time}]})

    def get_medias(self, kwargs):
        for el in self.get_json("/media" + url_param(kwargs)):
            yield el

    def get_videos(self, kwargs):
        print(kwargs, self.get_json("/video" + url_param(kwargs)))
        for el in self.get_json("/video" + url_param(kwargs)):
            yield el

    def get_poster(self, poster_path, storage_path):
        response = requests.get(self._server_address() + "/poster/500" + poster_path, stream=True)
        if response.status_code == 200:
            with open(storage_path, 'wb') as f:
                for chunk in response:
                    f.write(chunk)

    def get_backdrop(self, backdrop_path):
        response = requests.get(self._server_address() + "/backdrop" + backdrop_path)
        if response.status_code == 200:
            return response.content
        return None

    def set_timestamp(self, video_id, timestamp):
        self.post("/media/edit", json={"Timestamp": [{"VideoID": video_id,
                                                      "Timestamp": timestamp}]})

    def get_videos_info(self, video_id, columns):
        videos = list(self.get_videos({"columns": columns,
                                     "VideoID": video_id}))
        if len(videos) == 0:
            return None
        videos[0]["Filename"] = self._server_address()+"/stream/"+str(videos[0]["VideoID"])
        return videos[0]

    def get_movie_videos(self, media_id):
        return list(self.get_videos({"columns": ["VideoID", "Duration", "Path", "Size", "Timestamp", "Audios", "Subtitles"],
                                         "VideoMediaID": media_id,
                                         "videos.VideoMediaType": MEDIA_TYPE_MOVIE}))

    def get_tv_episodes(self, media_id):
        seasons = {}
        for episode in self.get_videos({"columns": ["VideoID",
                                                    "Duration",
                                                    "Path",
                                                    "Size",
                                                    "Timestamp",
                                                    "SeasonNumber",
                                                    "EpisodeNumber",
                                                    "EpisodeTitle",
                                                    "EpisodeOverview",
                                                    "Audios",
                                                    "Subtitles"],
                                        "TvShowID": media_id,
                                        "VideoMediaType": MEDIA_TYPE_TV}):
            if episode["SeasonNumber"] in seasons:
                seasons[episode["SeasonNumber"]].append(episode)
            else:
                seasons[episode["SeasonNumber"]] = [episode]
        return seasons

    def get_media(self, media_id, media_type):
        return list(self.get_medias({"ID": media_id,
                                     "medias.MediaType": media_type,
                                     "columns": ["ID",
                                                 "Title",
                                                 "MediaType",
                                                 "PosterPath",
                                                 "Genres",
                                                 "OriginalTitle",
                                                 "VoteAverage",
                                                 "ReleaseDate",
                                                 "BackdropPath",
                                                 "Overview"]}))[0]
