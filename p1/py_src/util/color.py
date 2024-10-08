from typing import Tuple
def hex2rgb(hexstr:str) -> Tuple:
    hexstr = hexstr.lstrip('#')
    return (
        int(hexstr[:2],16),
        int(hexstr[2:4],16),
        int(hexstr[4:6],16)
    )

def hex2rgbastr(hexstr,a=1) -> str:
    rgb_tup = hex2rgb(hexstr)
    return "rgba({},{},{},{})".format(
        rgb_tup[0],
        rgb_tup[1],
        rgb_tup[2],
        a
    )

from PyQt5.QtGui import QPalette, QColor
def hex2pal(hexstr:str) -> QColor:
    hexstr = hexstr.lstrip('#')
    return QColor(
        int(hexstr[:2],16),
        int(hexstr[2:4],16),
        int(hexstr[4:6],16)
    )