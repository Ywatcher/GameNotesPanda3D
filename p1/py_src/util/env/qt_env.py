# import importlib
from importlib.util import find_spec



USE_QTPY = True  # 是否优先使用 QtPy

if USE_QTPY:
    if find_spec("qtpy"):
        from qtpy import QtCore, QtGui, QtWidgets, QtOpenGL
        from qtpy.QtCore import Qt
        QT_BINDING = "QtPy"
    else:
        USE_QTPY = False  # qtpy 不存在，退回下面手动绑定

def choose_qt_binding():
    # 按优先级选择
    bindings = [
        ("PySide6", "PySide6"),
        ("PyQt5", "PyQt5"),
        ("PyQt6", "PyQt6"),


        ("PySide2", "PySide2"),
    ]
    for name, prefix in bindings:
        if find_spec(name):
            return prefix
    raise ImportError("No supported Qt bindings found (PyQt5/6, PySide2/6).")

# QT_BINDING = "PySide6"
if not USE_QTPY:
    QT_BINDING = choose_qt_binding()


if QT_BINDING == "QtPy":
    from qtpy import QtCore, QtGui, QtWidgets, QtOpenGL
    from qtpy.QtCore import Qt
elif QT_BINDING == "PySide6":
    from PySide6 import QtCore, QtGui, QtWidgets, QtOpenGL
    from PySide6.QtCore import Qt
elif QT_BINDING == "PyQt6":
    from PyQt6 import QtCore, QtGui, QtWidgets, QtOpenGL
    from PyQt6.QtCore import Qt

elif QT_BINDING == "PyQt5":
    from PyQt5 import QtCore, QtGui, QtWidgets, QtOpenGL
    from PyQt5.QtCore import Qt
elif QT_BINDING == "PySide2":
    from PySide2 import QtCore, QtGui, QtWidgets, QtOpenGL
    from PySide2.QtCore import Qt

# widgets = [
    # "QWidget", "QApplication", "QMainWindow",
    # "QDockWidget", "QTextEdit", "QPlainTextEdit"
# ]

# globals().update({name: getattr(QtWidgets, name) for name in widgets})
if __name__ == "__main__":
    print(f"[qt_adapter] Using Qt binding: {QT_BINDING}")
