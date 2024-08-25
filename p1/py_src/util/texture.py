import numpy as np
from PIL import Image
from typing import Tuple
from panda3d.core import PNMImage, Texture

# TODO： colors
# TODO: put this outside util


# def np2pnm(arr: np.ndarray) -> PNMImage:
#     # create PNMImage object
#     if len(arr.shape) == 3:
#         # if arr.shape[2] == 3:
#         #     # 3 rgb channels
            
#         # coloured image
#         assert arr.shape[2] == 3 \
#             or arr.shape[2] == 4, \
#             f"must have three or four colour channels i.e. shape[2]==3or4, got arr shape:{arr.shape}" 
#         # FIXME: case when there is alpha
#         if arr.shape[2] == 4:
#             raise NotImplementedError
#         pnm_image = PNMImage(arr.shape[1], arr.shape[0], 3)  # FIXME
#     else:
#         assert len(arr.shape) == 2, f"arr expected to have 2 or 3 axis, got shape:{arr.shape}"
#         pnm_image = PNMImage(arr.shape[1], arr.shape[0])
#     # fill array into PNMImage
#     pnm_image.setXelVal(arr.flatten())
#     return pnm_image

# def npm2np
# def npm2pil

def np2texture(
    arr: np.ndarray,
    component_type:int = Texture.T_unsigned_byte, # for 0-255
    format_:int=None,
    name:str=None
) -> Texture:
    # TODO: optimize texture t
    h = arr.shape[1]
    w = arr.shape[0]
    # FIMXE: autodetect format
    if format_ == Texture.F_rgb:
        assert len(arr.shape) == 3 \
            and arr.shape[2] == 3
        # TODO: fix rgb order
    elif format_ == Texture.F_rgba:
        assert len(arr.shape) == 3 \
            and arr.shape[2] == 4
    elif format_ in [
        Texture.F_luminance, Texture.F_red,
        Texture.F_green, Texture.F_blue,
        Texture.F_alpha, Texture.F_depth_component       
    ]:
        assert len(arr.shape) == 2 \
            or (len(arr.shape)==3 \
                and arr.shape[2]==1)
    elif format_ in [
        Texture.F_luminance_alpha,
        Texture.F_rg
    ]:
        assert len(arr.shape) == 3 \
            and arr.shape[2] == 2
    else:
        return NotImplemented
    if name is not None:
        tex = Texture(name)
    else:
        tex = Texture()
    tex.setup2dTexture(h, w, component_type, format_)
    buffer = arr.tobytes()
    tex.setRamImage(buffer)
    return tex
    
    


# example textures --------------
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