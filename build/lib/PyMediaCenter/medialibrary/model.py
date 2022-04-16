import os
import sys
import unicodedata

from PyQt5.QtCore import pyqtSignal, QVariant, QSortFilterProxyModel, Qt, QObject
from PyQt5.QtGui import QIcon, QPixmap

from PyMediaCenter.pythread import threaded

from PyMediaCenter import pyconfig
from PyMediaCenter.medialibrary import MEDIA_TYPE_MOVIE, MEDIA_TYPE_TV
from PyMediaCenter.model import ModelTableListDict


class DictLimit:
    def __init__(self, limit=700):
        self.list = []
        self.dict = {}
        self.limit = limit

    def add(self, key, value):
        if key not in self.list:
            self.list.append(key)
        self.dict[key] = value
        if len(self.list) > self.limit:
            key = self.list.pop(0)
            del self.dict[key]

    def is_in(self, key):
        if key in self.list:
            return True
        return False

    def get(self, key):
        return self.dict[key]


class PixmapManager:
    def __init__(self, base_path, server):
        self.server = server
        self.base_path = base_path
        self.pixmapDict = DictLimit()
        self.pixmap404 = QPixmap(":/rsc/404.jpg")

    def get_poster(self, poster_path):
        file_path = os.path.join(self.base_path, poster_path[1:])

        if poster_path is None:
            return self.pixmap404

        if self.pixmapDict.is_in(poster_path):
            return self.pixmapDict.get(poster_path)

        elif os.path.exists(file_path):
            pixmap = QPixmap(file_path)
            self.pixmapDict.add(poster_path, pixmap)
            return pixmap
        else:
            print(file_path, 404)
            self.download_poster(poster_path)
            return self.pixmap404

    @threaded("poster")
    def download_poster(self, poster_path):
        original_path = os.path.join(self.base_path, poster_path[1:])
        if not os.path.exists(original_path) and self.server:
            self.server.get_poster(poster_path, original_path)

    def download_backdrop(self, backdrop_path):
        pixmap = QPixmap()
        data = self.server.get_backdrop(backdrop_path)
        if data:
            pixmap.loadFromData(data)
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
        self.mediaModel = MediaModel(self.poster)
        self.genreModel = GenreModel(self.poster)

    @threaded("httpCom")
    def refresh_media(self):
        self.busy.emit(True)
        data = []
        for media in self.server.get_medias({"columns": list(self.mediaModel.get_keys(add=["ID"]))}):
            #self.poster.get_poster(media["PosterPath"])
            if "Genres" in media and media["Genres"]:
                for genre in media["Genres"]:
                    self.genreModel.add(genre)
            else:
                media["Genres"] = []
            data.append(media)
        self.mediaModel.reset_data(data)
        self.busy.emit(False)

    @threaded("httpCom")
    def get_media_info(self, media_id, media_type):
        self.busy.emit(True)
        media = self.server.get_media(media_id, media_type)
        media["Poster"] = self.poster.get_poster(media["PosterPath"])
        media["Backdrop"] = self.poster.download_backdrop(media["BackdropPath"])
        if media_type == MEDIA_TYPE_MOVIE:
            media["Videos"] = self.server.get_movie_videos(media_id)
            self.movie_info.emit(media)
        elif media_type == MEDIA_TYPE_TV:
            episodes = self.server.get_tv_episodes(media_id)
            media["Seasons"] = {}
            for season in episodes.keys():
                media["Seasons"][season] = TvEpisodeModel(episodes[season]).get_proxy()
                media["Seasons"][season].do_sort()
            self.tv_info.emit(media)
        self.busy.emit(False)

    @threaded("httpCom")
    def get_videos_info(self, video_list):
        self.busy.emit(True)
        ret = []
        for video_id in video_list:
            video_info = self.server.get_videos_info(video_id, ["VideoID",
                                                                "Timestamp",
                                                                "MediaType",
                                                                "Title",
                                                                "ReleaseDate",
                                                                "SeasonNumber",
                                                                "EpisodeNumber",
                                                                "EpisodeTitle"])
            if video_info is not None:
                ret.append(video_info)

        if len(ret) > 0:
            self.playlist_ready.emit(ret)

        self.busy.emit(False)

    @threaded("httpCom")
    def update_timestamp(self, video_id, timestamp):
        self.server.set_timestamp(video_id, timestamp)


    def get_all_media(self, genre=None):
        proxy = MediaProxy()
        if genre:
            proxy.set_genres([genre])
        proxy.setSourceModel(self.mediaModel)
        return proxy

    def get_movie(self):
        proxy = MediaProxy()
        proxy.set_media_type(MEDIA_TYPE_MOVIE)
        proxy.setSourceModel(self.mediaModel)
        return proxy

    def get_tv(self):
        proxy = MediaProxy()
        proxy.set_media_type(MEDIA_TYPE_TV)
        proxy.setSourceModel(self.mediaModel)
        return proxy

    def get_genre(self):
        return self.genreModel


class GenreModel(ModelTableListDict):
    def __init__(self, poster, **kwargs):
        ModelTableListDict.__init__(self, [("Name", "Name", False, None)])
        self.poster_manager = poster

    def check_in(self, name):
        for el in self.list:
            if el['Name'] == name:
                return True
        return False

    def add(self, genre):
        if not self.check_in(genre):
            self.list.append({"Name": genre})
        self.reset_data(self.list)

    def get_decoration_role(self, index):
        if index.column() == 0:
            return QIcon(self.poster_manager.get_poster("/" + self.list[index.row()]["Name"] + ".jpg"))
        return QVariant()


class MediaModel(ModelTableListDict):
    def __init__(self, poster):
        ModelTableListDict.__init__(self, [("#", None, False, None),
                                           ("Title", "Title", False, None),
                                           ("Original Title", "OriginalTitle", False, None),
                                           ("Genres", "Genres", False, None),
                                           ("Release date", "ReleaseDate", False, None),
                                           ("Vote", "VoteAverage", False, None),
                                           ("Poster", "PosterPath", False, None),
                                           ("Media type", "MediaType", False, None)])
        self.poster_manager = poster

    def get_decoration_role(self, index):
        if index.column() == 0:
            pixmap = self.poster_manager.get_poster(self.list[index.row()]["PosterPath"])
            icon = QIcon()
            icon.addPixmap(pixmap, QIcon.Normal)
            icon.addPixmap(pixmap, QIcon.Selected)
            return icon
        return QVariant()


class MediaProxy(QSortFilterProxyModel):
    def __init__(self, parent=None, *args):
        QSortFilterProxyModel.__init__(self, parent)
        self.sort_key = "Title"
        self.reverse = False
        self.media_type = None
        self.filter_genres = []
        self.filter_string = ""
        self.sort_keys = [("Titre", "Title"),
                          ("Date de sortie", "ReleaseDate"),
                          ("Vote", "VoteAverage"),
                          ("Titre Original", "OriginalTitle")]
        self.do_sort()

    def reset(self):
        self.sort_key = "Title"
        self.reverse = False
        self.media_type = None
        self.filter_genres = []
        self.filter_string = ""
        self.do_sort()

    def get_sort_keys(self):
        return self.sort_keys

    def data(self, index, role=None):
        return self.sourceModel().data(self.mapToSource(index), role)

    def set_sort_key(self, key):
        self.sort_key = key

    def set_reverse(self, reverse):
        self.reverse = reverse

    def set_media_type(self, media_type):
        self.media_type = media_type

    def do_sort(self):
        if self.reverse:
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

        if self.media_type and data["MediaType"] != self.media_type:
            return False

        for genre in self.filter_genres:
            if genre not in data["Genres"]:
                return False

        if not filter_by_string(data, "Title", self.filter_string):
            return filter_by_string(data, "OriginalTitle", self.filter_string)

        return True


class TvEpisodeModel(ModelTableListDict):
    info = pyqtSignal('PyQt_PyObject')

    def __init__(self, data):
        ModelTableListDict.__init__(self, [("", "Timestamp", False, convert_x),
                                           ("E", "EpisodeNumber", False, None),
                                           ("Title", "EpisodeTitle", False, None),
                                           ("Overview", "EpisodeOverview", False, None)])
        self.reset_data(data)

    def get_proxy(self):
        proxy = SortEpisode()
        proxy.setSourceModel(self)
        return proxy


class SortEpisode(QSortFilterProxyModel):
    def __init__(self):
        QSortFilterProxyModel.__init__(self, None)
        self.tv_id = 0
        self.reverse = False

    def lessThan(self, left, right):
        left_data = self.sourceModel().data(left)
        right_data = self.sourceModel().data(right)
        if left_data["SeasonNumber"] < right_data["SeasonNumber"]:
            return True
        elif left_data["SeasonNumber"] == right_data["SeasonNumber"]:
            return left_data["EpisodeNumber"] < right_data["EpisodeNumber"]
        else:
            return False

    def do_sort(self):
        if self.reverse:
            self.sort(0, order=Qt.DescendingOrder)
        else:
            self.sort(0, order=Qt.AscendingOrder)
        self.invalidate()

def strip_accents(text):
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


def filter_by_string(data, key, value):
    if len(value) == 0:
        return True
    data_value = strip_accents(data[key]).lower()
    value = strip_accents(value).lower()
    for val in value.split(" "):
        if data_value.find(val) < 0 < len(val):
            return False
    return True

def convert_x(data):
    if data and data > 0:
        return "V"
    return "O"