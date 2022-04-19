import math
import os
import unicodedata
import time

from PyQt5.QtCore import pyqtSignal, QVariant, QSortFilterProxyModel, Qt, QObject
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication

from PyMediaCenter.pythread import threaded

from PyMediaCenter import pyconfig
from PyMediaCenter.model import ModelTableListDict

class PixmapManager:
    def __init__(self, base_path, server):
        self.server = server
        self.base_path = base_path
        rect = QApplication.desktop().screenGeometry()
        self.pixmap404 = QPixmap(":/rsc/404.jpg").scaledToWidth(400, mode=Qt.SmoothTransformation)

    def get_poster(self, poster_path):
        file_path = os.path.join(self.base_path, poster_path[1:])

        if poster_path is None or len(poster_path) == 0:
            return self.pixmap404

        elif os.path.exists(file_path):
            pixmap = QPixmap()
            if pixmap.load(file_path):
                # self.pixmapDict.add(poster_path, pixmap)
                return pixmap

        self.download_poster_threaded(poster_path)
        return self.pixmap404

    @threaded("poster")
    def download_poster_threaded(self, poster_path):
        self.save_poster(poster_path)

    def save_poster(self, poster_path):
        if poster_path is None or len(poster_path) == 0:
            return

        file_path = os.path.join(self.base_path, poster_path[1:])
        if os.path.exists(file_path):
            return

        pixmap = self.download_rsc(poster_path)
        if not pixmap:
            return

        pixmap.save(file_path)

        print(f"download poster: {poster_path}")

    def download_rsc(self, backdrop_path, original=False):
        pixmap = QPixmap()
        data = self.server.get_rsc(backdrop_path)
        if not data:
            return
        if not pixmap.loadFromData(data):
            return
        if not original:
            pixmap = pixmap.scaled(306, 467, transformMode=Qt.SmoothTransformation)
        return pixmap


class ModelManager(QObject):
    movie_info = pyqtSignal('PyQt_PyObject')
    tv_info = pyqtSignal('PyQt_PyObject')
    busy = pyqtSignal('PyQt_PyObject')
    playlist_ready = pyqtSignal('PyQt_PyObject')

    def __init__(self, server):
        QObject.__init__(self)
        self.server = server
        self.poster = PixmapManager(pyconfig.get("rsc.poster"), self.server)
        self.tv_model = MediaModel(self.poster)
        self.tv_search = MediaProxy()
        self.tv_search.setSourceModel(self.tv_model)
        self.movie_model = MediaModel(self.poster)
        self.movie_search = MediaProxy()
        self.movie_search.setSourceModel(self.movie_model)
        self.person_model = MediaModel(self.poster, name_index="name", poster_path="profile_path")
        self.person_search = MediaProxy(sort_key="name")
        self.person_search.setSourceModel(self.person_model)

    @threaded("httpCom")
    def refresh_media(self):
        self.refresh_movies()
        self.refresh_tvs()
        self.refresh_persons()
        #self.download_poster()

    def download_poster(self):
        self.busy.emit(True)
        for movie in self.movie_model.list:
            self.poster.save_poster(movie["poster_path"])
            print(f"download poster : {movie['poster_path']}")
        for tv in self.tv_model.list:
            self.poster.save_poster(tv["poster_path"])
            print(f"download poster : {tv['poster_path']}")
        for person in self.person_model.list:
            self.poster.save_poster(person["profile_path"])
            print(f"download poster : {person['profile_path']}")
        self.busy.emit(False)

    def refresh_movies(self):
        #self.busy.emit(True)
        data = []
        for movie in self.server.get_movies():
            movie["type"] = "movie"
            data.append(movie)
        self.movie_model.reset_data(data)
        #self.busy.emit(False)

    def refresh_tvs(self):
        #self.busy.emit(True)
        data = []
        for tv in self.server.get_tvs():
            tv["type"] = "tv"
            data.append(tv)
        self.tv_model.reset_data(data)
        #self.busy.emit(False)

    def refresh_persons(self):
        #self.busy.emit(True)
        data = []
        for person in self.server.get_persons():
            person["type"] = "person"
            data.append(person)
        self.person_model.reset_data(data)
        #self.busy.emit(False)

    def get_movies(self):
        proxy = MediaProxy()
        proxy.setSourceModel(self.movie_model)
        return proxy

    def get_tvs(self):
        proxy = MediaProxy()
        proxy.setSourceModel(self.tv_model)
        return proxy

    def get_persons(self):
        proxy = MediaProxy(sort_key="name")
        proxy.setSourceModel(self.person_model)
        return proxy

    def get_media_info(self, media_id, media_type):
        if media_type == "tv":
            self.get_tv(media_id)
        elif media_type == "movie":
            self.get_movie(media_id)

    @threaded("httpCom")
    def get_movie(self, movie_id, signal):
        self.busy.emit(True)
        movie = self.server.get_movie(movie_id)
        movie["poster"] = self.poster.download_rsc(movie["poster_path"], original=True)
        movie["backdrop"] = self.poster.download_rsc(movie["backdrop_path"], original=True)
        movie["casting"] = MediaProxy(sort_key="ord")
        movie["casting"].setSourceModel(MediaModel(self.poster,
                                                   data=movie["cast"],
                                                   name_index="name",
                                                   custom_fct=cast_and_name,
                                                   poster_path="profile_path"))
        self.busy.emit(False)
        signal.emit(movie)

    @threaded("httpCom")
    def get_person(self, person_id, signal):
        self.busy.emit(True)
        backdrop = None
        person = self.server.get_person(person_id)
        person["profile"] = self.poster.download_rsc(person["profile_path"])
        person["movie"] = MediaProxy(sort_key="release_date")
        person["movie"].setSourceModel(MediaModel(self.poster, data=person["cast_movie"] + person["crew_movie"]))
        person["tv"] = MediaProxy(sort_key="release_date")
        person["tv"].setSourceModel(MediaModel(self.poster, data=person["cast_tv"] + person["crew_tv"]))
        for movie in person["cast_movie"] + person["crew_movie"]:
            backdrop = self.poster.download_rsc(movie["backdrop_path"])
            break
        if backdrop is None:
            for tv in person["cast_tv"] + person["crew_tv"]:
                backdrop = self.poster.download_rsc(tv["backdrop_path"])
                break
        self.busy.emit(False)
        signal.emit(person, backdrop)


    @threaded("httpCom")
    def get_tv(self, tv_id, signal):
        self.busy.emit(True)
        tv = self.server.get_tv(tv_id)
        tv["poster"] = self.poster.download_rsc(tv["poster_path"], original=True)
        tv["backdrop"] = self.poster.download_rsc(tv["backdrop_path"], original=True)
        tv["casting"] = MediaProxy(sort_key="ord")
        tv["casting"].setSourceModel(MediaModel(self.poster,
                                                data=tv["cast"],
                                                name_index="name",
                                                custom_fct=cast_and_name,
                                                poster_path="profile_path"))

        tv["season"] = MediaProxy(sort_key="season_number")
        tv["season"].setSourceModel(MediaModel(self.poster,
                                               data=tv["seasons"],
                                               name_index="title"))
        self.busy.emit(False)
        signal.emit(tv)


    @threaded("httpCom")
    def get_tv_season(self, tv_id, season, signal):
        self.busy.emit(True)
        tv = self.server.get_season(tv_id, season)
        tv["poster"] = self.poster.download_rsc(tv["poster_path"], original=True)
        tv["backdrop"] = self.poster.download_rsc(tv["tv"]["backdrop_path"], original=True)
        tv["episode"] = EpisodeProxy()
        tv["episode"].setSourceModel(EpisodeModel(tv["episodes"]))
        self.busy.emit(False)
        signal.emit(tv)


    @threaded("httpCom")
    def get_home(self, media_type, signal):
        self.busy.emit(True)
        ret = {}
        data = self.server.get_special(media_type, "essential")

        ret["last"] = MediaProxy(sort_key="adding", reverse=True)
        ret["last"].setSourceModel(MediaModel(self.poster, data["last"]))

        ret["recent"] = MediaProxy(sort_key="release_date", reverse=True)
        ret["recent"].setSourceModel(MediaModel(self.poster, data["recent"]))

        genre = self.server.get_special(media_type, "genre")

        ret["genre"] = MediaProxy(sort_key="name")
        ret["genre"].setSourceModel(GenreModel(self.poster, genre, poster_path="name"))

        self.busy.emit(False)
        signal.emit(ret)

    @threaded("httpCom")
    def get_videos(self, data_type, media_id, signal):
        self.busy.emit(True)
        l_video = []
        for video in self.server.get_videos(data_type, media_id):
            l_video.append(self.server.get_video(video["id"]))
        self.busy.emit(False)
        signal.emit("dummy", l_video)

    @threaded("httpCom")
    def update_timestamp(self, video_id, timestamp):
        self.server.set_timestamp(video_id, timestamp)

    @threaded("httpCom")
    def play_movie(self, video):
        self.busy.emit(True)
        media = self.server.get_movie(video["media_id"])
        self.busy.emit(False)
        self.playlist_ready.emit([{
            "id": video["id"],
            "stream_path": f"{self.server.get_stream_path()}/{video['id']}",
            "watch_time": video["watch_time"],
            "info": f"{media['title']} {media['release_date'][:4]}"
        }])

    @threaded("httpCom")
    def play_episode(self, video):
        self.busy.emit(True)
        ret = []
        media = self.server.get_episode(video["media_id"])[0]
        print(media)
        ret.append({
            "id": video["id"],
            "stream_path": f"{self.server.get_stream_path()}/{video['id']}",
            "watch_time": video["watch_time"],
            "info": f"{media['tv_title']} S{media['season_number']:02d}E{media['episode_number']:02d} - {media['title']}"
        })
        while len(ret) < 15:
            media = self.server.get_episode(media['tv_id'], media['season_number'], media['episode_number']+1)
            if media is None:
                break

            video = self.server.get_video(self.server.get_videos("tv", media["id"])[0]["id"])
            ret.append({
                "id": video["id"],
                "stream_path": f"{self.server.get_stream_path()}/{video['id']}",
                "watch_time": video["watch_time"],
                "info": f"{media['tv_title']} S{media['season_number']:02d}E{media['episode_number']:02d} - {media['title']}"
            })
        self.busy.emit(False)
        self.playlist_ready.emit(ret)


class VideoModel(ModelTableListDict):
    def __init__(self, data):
        ModelTableListDict.__init__(self, [("Path", "path", False, convert_path),
                                           ("Taille", "size", False, convert_size),
                                           ("Durée", "duration", False, convert_duration),
                                           ("Sous titre", "subtitles", False, None),
                                           ("Languages", "audios", False, None)])
        self.reset_data(data)


class EpisodeModel(ModelTableListDict):
    def __init__(self, data):
        ModelTableListDict.__init__(self, [("Watched", None, False, None),
                                           ("Title", "title", False, self.concat_name),
                                           ("Overview", "overview", False, None),
                                           ("Release", "release_date", False, None),
                                           ("Vote", "vote_average", False, None)])
        self.reset_data(data)

    def concat_name(self, value, key):
        return f'{value["episode_number"]}.{value["title"]}'

    def get_decoration_role(self, index):
        if index.column() == 0:
            if self.list[index.row()]["watched"] > 0:
                pixmap = QPixmap(":/rsc/see-full.png")
            else:
                pixmap = QPixmap(":/rsc/see-empty.png")
            icon = QIcon()
            icon.addPixmap(pixmap, QIcon.Normal)
            icon.addPixmap(pixmap, QIcon.Selected)
            return icon
        return QVariant()


class EpisodeProxy(QSortFilterProxyModel):
    def __init__(self):
        QSortFilterProxyModel.__init__(self)
        self.sort_key = "episode_number"
        self.sort(0, order=Qt.AscendingOrder)
        self.invalidate()

    def data(self, index, role=None):
        return self.sourceModel().data(self.mapToSource(index), role)

    def lessThan(self, left_index, right_index):

        left_data = self.sourceModel().data(left_index)
        right_data = self.sourceModel().data(right_index)

        return left_data[self.sort_key] < right_data[self.sort_key]





class MediaModel(ModelTableListDict):
    def __init__(self, poster, data=None, name_index=None, custom_fct=None, poster_path="poster_path"):
        ModelTableListDict.__init__(self, [("#", name_index, False, custom_fct)])
        self.poster_manager = poster
        self.poster_path = poster_path
        if data:
            self.reset_data(data)

    def get_decoration_role(self, index):
        if index.column() == 0:
            pixmap = self.poster_manager.get_poster(self.list[index.row()][self.poster_path])
            icon = QIcon()
            icon.addPixmap(pixmap, QIcon.Normal)
            icon.addPixmap(pixmap, QIcon.Selected)
            return icon
        return QVariant()


class GenreModel(MediaModel):
    def get_decoration_role(self, index):
        if index.column() == 0:
            pixmap = QPixmap()
            if not pixmap.load(f":rsc/light_poster/{self.list[index.row()][self.poster_path]}.jpg"):
                pixmap.load(":/rsc/404.jpg")
                pixmap = pixmap.scaledToWidth(300, mode=Qt.SmoothTransformation, )

            icon = QIcon()
            icon.addPixmap(pixmap, QIcon.Normal)
            #icon.addPixmap(pixmap, QIcon.Selected)
            return icon
        return QVariant()


class MediaProxy(QSortFilterProxyModel):
    def __init__(self, parent=None, reverse=False, sort_key="title"):
        QSortFilterProxyModel.__init__(self, parent)
        self.sort_key = None
        self.reverse = None
        self.filter_genres = []
        self.filter_string = ""
        self.sort_keys = [("Titre", "title"),
                          ("Date d'ajout", "adding"),
                          ("Date de sortie", "release_date"),
                          ("Vote", "vote_average")]
        self.set_sort_key(sort_key, reverse)

    def get_sort_keys(self):
        return self.sort_keys

    def data(self, index, role=None):
        return self.sourceModel().data(self.mapToSource(index), role)

    def set_sort_key(self, key, reverse=False):
        self.reverse = reverse
        self.sort_key = key
        if reverse:
            self.sort(0, order=Qt.DescendingOrder)
        else:
            self.sort(0, order=Qt.AscendingOrder)
        self.invalidate()

    def set_genres(self, genres=None):
        if genres is None or "Tous" in genres:
            self.filter_genres = []
        else:
            self.filter_genres = genres
        self.setFilterWildcard("")

    def set_search_string(self, string):
        self.filter_string = string
        self.setFilterWildcard("")

    def lessThan(self, left_index, right_index):

        left_data = self.sourceModel().data(left_index)
        right_data = self.sourceModel().data(right_index)

        return left_data[self.sort_key] < right_data[self.sort_key]

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        data = self.sourceModel().data(index)
        if data == QVariant():
            return False

        if "genres" in data:
            for genre in self.filter_genres:
                if genre not in data["genres"]:
                    return False

        if self.filter_string is None:
            return False

        if filter_by_string(data, "title", self.filter_string):
            return True
        elif filter_by_string(data, "original_title", self.filter_string):
            return True
        elif filter_by_string(data, "name", self.filter_string):
            return True
        else:
            return False


def strip_accents(text):
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


def filter_by_string(data, key, value):
    if len(value) == 0:
        return True
    if key not in data:
        return False
    data_value = strip_accents(data[key]).lower()
    value = strip_accents(value).lower()
    for val in value.split(" "):
        if data_value.find(val) < 0 < len(val):
            return False
    return True


def one_value(func):
    print("Inside decorator")

    def inner(*args, **kwargs):

        value = args[0][args[1]]
        return func(value)

    return inner


def cast_and_name(value, key):
    print(value)
    return f"{value['name']} \r\n {value['character']}"


@one_value
def convert_path(path):
    return path.split('/')[-1]


@one_value
def convert_size(size_bytes):
    if size_bytes == 0 or size_bytes is None:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def add_px(pixels):
    return "%s px" % (str(pixels),)


def convert_bit_stream(bit_stream):
    return convert_size(bit_stream)+"/s"


def convert_x(data):
    if data and data > 0:
        return "x"
    return ""


@one_value
def convert_duration(millis):
    seconds = int(millis/1000)
    return time.strftime('%H:%M:%S', time.gmtime(seconds))
