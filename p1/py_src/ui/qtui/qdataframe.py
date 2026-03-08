# -*- coding: utf-8-*-
import sys
import pandas as pd
from util.env.qt_env import QtWidgets, QtCore, Qt 
QAbstractTableModel = QtCore.QAbstractTableModel
QApplication = QtWidgets.QApplication
QTableView   = QtWidgets.QTableView
# from PyQt5.QtCore import Qt, QAbstractTableModel
# from PyQt5.QtWidgets import QApplication, QTableView
import weakref

class DataFrameModel(QAbstractTableModel):
    # map dataframe ids to models
    _df_models:  "weakref.WeakValueDictionary[int, DataFrameModel]"= weakref.WeakValueDictionary()

    def __init__(self, df):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._df.iloc[index.row(), index.column()]
            return str(value)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:

            if orientation == Qt.Orientation.Horizontal:
                return str(self._df.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._df.index[section])

    @classmethod
    def get_model(cls, df: pd.DataFrame) -> "DataFrameModel":
        df_id = id(df)
        if df_id not in cls._df_models:
            model = cls(df)
            cls._df_models[df_id] = model
        return cls._df_models[df_id]

    @classmethod
    def refresh(cls, df: pd.DataFrame):
        df_id = id(df)
        if df_id in cls._df_models:
            model = cls._df_models[df_id]
            model.layoutChanged.emit()

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, new_df: pd.DataFrame):
        self.setDataFrame(new_df)

    def setDataFrame(self, df: pd.DataFrame):
        """
        替换 DataFrame，并更新模型。
        """
        # 如果旧的 df 存在于 _df_models 中，先移除旧条目
        old_id = id(self._df)
        if old_id in self.__class__._df_models:
            del self.__class__._df_models[old_id]

        # 替换 DataFrame
        self.beginResetModel()
        self._df = df
        self.endResetModel()

        # 将新 df 注册到弱引用字典
        self.__class__._df_models[id(df)] = self


if __name__ == "__main__":
    app = QApplication(sys.argv)

    df = pd.DataFrame({
        "A": [1,2,3],
        "B": [4,5,6],
        "C": ["x","y","z"]
    })

    view = QTableView()
    model = DataFrameModel(df)

    view.setModel(model)
    view.show()

    sys.exit(app.exec())

