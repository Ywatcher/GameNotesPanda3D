import numpy as np
from PIL import Image
from typing import Tuple
from panda3d.core import PNMImage, Texture



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


def rgba_mpl2pd3d(colors:np.ndarray):
    # matplotlib and vispy: r,g,b,a
    # panda3d: b,g,r,a
    # for rgba
    return np.einsum(
        'ijk, kl -> ijl',
        colors,
        np.array([
            [0,0,1,0],
            [0,1,0,0],
            [1,0,0,0],
            [0,0,0,1]
        ])
    )

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

def texture_load_np(
    texture: Texture, 
    arr: np.ndarray,
    component_type:int = Texture.T_unsigned_byte, # for 0-255
    format_:int=None,
):
    h = arr.shape[1]
    w = arr.shape[0]
    # TODO: assertion
    texture.setup2dTexture(h, w, component_type, format_)
    buffer = arr.tobytes()
    texture.setRamImage(buffer)
    return texture


