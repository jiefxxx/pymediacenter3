from PyQt5.QtCore import QAbstractTableModel, pyqtSignal, Qt, QVariant, QModelIndex

DISPLAY_KEY = 0
DICT_KEY = 1
EDIT_KEY = 2
BEFORE_KEY = 3


class ModelTableListDict(QAbstractTableModel):
    busy = pyqtSignal('PyQt_PyObject')
    refreshed = pyqtSignal()

    def __init__(self, list_key):

        QAbstractTableModel.__init__(self, None)
        self.list = []
        self.list_key = list_key

    def refresh(self):
        pass

    def rowCount(self, parent=None, *args, **kwargs):
        if self.list is None:
            self.list = []
        return len(self.list)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.list_key)

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            try:
                return QVariant(self.get_key(section, role=DISPLAY_KEY))
            except IndexError as e:
                print("headerData:", e, section)

        return QAbstractTableModel.headerData(self, section, orientation, role)

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()

        try:
            if role == Qt.DisplayRole:
                key = self.get_key(index.column())
                if key:
                    before = self.get_key(index.column(), role=BEFORE_KEY)
                    if before:
                        return QVariant(before(self.list[index.row()][key]))
                    else:
                        return QVariant(self.list[index.row()][key])

            elif role == Qt.DecorationRole:
                return self.get_decoration_role(index)

            elif role == Qt.UserRole:
                key = self.get_key(index.column())
                if key:
                    return QVariant(self.list[index.row()][key])
                else:
                    return self.list[index.row()]

            elif role == Qt.ToolTipRole:
                return self.get_toolTip_role(index)

            elif role is None:
                return self.list[index.row()]

        except TypeError:
            return QVariant("#!TYPE_ERROR")

        except IndexError:
            return QVariant("#!INDEX_ERROR")

        except KeyError:
            return QVariant("#!EMPTY")

        return QVariant()

    def setData(self, index, value, role=None):
        if not index.isValid():
            return False

        row = index.row()
        low_index = self.createIndex(row, 0)
        high_index = self.createIndex(row, len(self.list_key))

        try:
            if role is None:
                self.list[row] = value

            elif role == Qt.EditRole:
                key = self.get_key(index.column())
                self.list[row][key] = value

            self.dataChanged.emit(low_index, high_index, [])
            return True

        except TypeError as e:
            print("setData", e)
        except IndexError as e:
            print("setData", e)

        return False

    def flags(self, index):
        if index.isValid():
            if self.get_key(index.column(), role=EDIT_KEY):
                return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled

    def insertRows(self, row, count, parent=None):
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        if row == self.rowCount():
            for i in range(0, count):
                self.list.append({})
        else:
            for i in range(0, count):
                self.list.insert(row + i, {})
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=None):
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self.list[row:row + count]
        self.endRemoveRows()
        return True

    # start custom function

    def get_decoration_role(self, index):
        return QVariant()

    def get_toolTip_role(self, index):
        return QVariant()

    def clear(self):
        self.removeRows(0, self.rowCount())

    def add_data(self, data):
        try:
            row_index = self.rowCount()
            self.insertRow(row_index)
            self.setData(self.createIndex(row_index, 0), data)
        except RuntimeError:
            pass

    def reset_data(self, data):
        self.beginResetModel()
        self.list = data
        self.endResetModel()

    def get_index_of(self, column, value):
        for i in range(0, len(self.list)):
            if self.list[i][column] == value:
                return self.createIndex(i, 0)

    def get_key(self, column, role=DICT_KEY):
        return self.list_key[column][role]

    def get_keys(self, role=DICT_KEY, add=None):
        for i in range(0, len(self.list_key)):
            yield self.get_key(i, role=role)
        if add:
            for el in add:
                yield el

    def begin_busy(self):
        self.busy.emit(True)

    def end_busy(self):
        self.busy.emit(False)

    def end_refreshed(self):
        self.refreshed.emit()

    def close(self):
        pass