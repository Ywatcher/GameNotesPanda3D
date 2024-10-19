# -*- coding: utf-8-*-

import numpy as np
from PIL import Image
from typing import Tuple
from panda3d.core import PNMImage, Texture

from util.texture import *

## checkerboards



def create_grey_checkerboard(
    size:Tuple[int,int],
    square_size:int,
    color1:int=0,
    color2:int=255
) -> np.ndarray:
    # TODO: assertions

    # size and square_size must be int for indexing
    size = (int(size[0]),int(size[1]))
    square_size = int(square_size)
    # calculate row and col len
    num_squares_x = int(np.ceil(size[0] / square_size))
    num_squares_y = int(np.ceil(size[1] / square_size))

    # create an array as checkerboard
    checkerboard = np.full((size[1], size[0]), color1, dtype=np.uint8)
    # fill checkerboard grids
    for y in range(num_squares_y):
        for x in range(num_squares_x):
            if (x + y) % 2 == 0:
                checkerboard[
                    y*square_size:(y+1)*square_size,
                    x*square_size:(x+1)*square_size
                ] = color2
    return checkerboard


def create_color_checkerboard(
    size, square_size,
    color1 = [0,0,0],
    color2 = [255,255,255]
):
    # FIXME
    size = (int(size[0]),int(size[1]))
    square_size = int(square_size)
    # square_size = size[0] // num_squares
    num_squares_x = int(np.ceil(size[0] / square_size))
    num_squares_y = int(np.ceil(size[1] / square_size))
    checkerboard = np.zeros((size[1], size[0], 3), dtype=np.uint8)

    for y in range(num_squares_y):
        for x in range(num_squares_x):
            color = color2 if (x + y) % 2 == 0 else color1
            checkerboard[y*square_size:(y+1)*square_size, x*square_size:(x+1)*square_size] = color

    return checkerboard




# TODO: torch2pnm


# --------------------------------------------------------

def create_checkerboard_PIL_(size:Tuple[int,int], num_squares) -> Image.Image:
    # size 是图像的尺寸 (width, height)
    # num_squares 是每行和每列的方格数量

    # 计算每个方格的尺寸
    square_size = size[0] // num_squares

    # 创建一个空的 numpy 数组
    checkerboard = np.zeros((size[1], size[0]), dtype=np.uint8)

    # 填充 checkerboard 数组
    for y in range(num_squares):
        for x in range(num_squares):
            if (x + y) % 2 == 0:
                checkerboard[y*square_size:(y+1)*square_size, x*square_size:(x+1)*square_size] = 255

    # 将 numpy 数组转换为 PIL 图像
    image = Image.fromarray(checkerboard, 'L')

    return image

def create_checkerboard_PIL(size:Tuple[int,int], square_size:int) -> Image.Image:
    size = (int(size[0]),int(size[1]))
    square_size = int(square_size)
    # size 是图像的尺寸 (width, height)
    # num_squares 是每行和每列的方格数量

    # 计算每个方格的尺寸
    # square_size = size[0] // num_squares
    num_squares_x = int(np.ceil(size[0] / square_size))
    num_squares_y = int(np.ceil(size[1] / square_size))

    # 创建一个空的 numpy 数组
    checkerboard = np.zeros((size[1], size[0]), dtype=np.uint8)

    # 填充 checkerboard 数组
    for y in range(num_squares_y):
        for x in range(num_squares_x):
            if (x + y) % 2 == 0:
                checkerboard[y*square_size:(y+1)*square_size, x*square_size:(x+1)*square_size] = 255

    # 将 numpy 数组转换为 PIL 图像
    image = Image.fromarray(checkerboard, 'L')

    return image
