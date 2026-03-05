import sys
import pandas as pd

from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtWidgets import QApplication, QTableView


class DataFrameModel(QAbstractTableModel):

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

