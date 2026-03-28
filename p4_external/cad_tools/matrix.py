# def trsf_to_matrix(trsf):
    # return [
        # [trsf.Value(i, j) for j in range(1, 5)]
        # for i in range(1, 4)
    # ] + [[0,0,0,1]]
from panda3d.core import Mat4

def trsf_to_mat4(trsf, transpose=True):
    """
    Convert OCP gp_Trsf to Panda3D Mat4
    Mat 4 is in transpose to trsf
    """
    m = Mat4(
        trsf.Value(1,1), trsf.Value(1,2), trsf.Value(1,3), trsf.Value(1,4),
        trsf.Value(2,1), trsf.Value(2,2), trsf.Value(2,3), trsf.Value(2,4),
        trsf.Value(3,1), trsf.Value(3,2), trsf.Value(3,3), trsf.Value(3,4),
        0.0,              0.0,              0.0,              1.0
    )

    if transpose:
        m.transposeInPlace()
    return m

def trsf_to_torch(trsf, transpose=True):
    import torch
    m = torch.Tensor([
        [trsf.Value(1,1), trsf.Value(1,2), trsf.Value(1,3), trsf.Value(1,4)],
        [trsf.Value(2,1), trsf.Value(2,2), trsf.Value(2,3), trsf.Value(2,4)],
        [trsf.Value(3,1), trsf.Value(3,2), trsf.Value(3,3), trsf.Value(3,4)],
        [0.0,              0.0,              0.0,              1.0]

    ])
    if transpose:
        return m.transpose(0,1)
    else:
        return m
