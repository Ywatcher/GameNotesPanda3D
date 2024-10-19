# -*- coding: utf-8-*-

from util.color import *
# c_violet_frame = hex2pal('#97739e')
# c_violet_bg = hex2pal('#472c4d')
# c_gold_text = hex2pal('#472c4d')
# c_orange_text = hex2pal('#f5a16d')
c_violet_frame = '#97739e'
c_violet_bg = '#472c4d'
c_orange_text = '#f5a16d'
# TODO: read css file
styleSheet = (f"""
/*QDockWidget [
    border: 2px solid black;
    background-color: lightblue;
]*/
QMainWindow [
    background-color: {hex2rgbastr(c_violet_frame)};
]
QTextEdit, QListView, QPlainTextEdit [
    background-color: {hex2rgbastr(c_violet_bg)};
    color: {hex2rgbastr(c_orange_text)};
    font-size: 20px;
    /* background-image: url(draft.png); */
    /* background-attachment: fixed; */
]
QPlainTextEdit#logger [
    font-family: 'Courier'; /* fixme */
]
QPlainTextEdit#console [
    /* font-family: 'DejaVu Sans Mono'; */
    font-family: 'Liberation Mono';
    /* font-family: 'Noto Mono';*/
]
""").replace('[','{').replace(']','}')
