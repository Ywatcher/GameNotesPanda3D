import torch


def compute_uv_normals(
        P: torch.Tensor,
        is_u_loop=False,
        is_v_loop=False,
    ):
    
    dPdu = torch.zeros_like(P)
    dPdv = torch.zeros_like(P)
    
    dPdu[1:-1] = P[2:] - P[:-2]
    if is_u_loop:
        dPdu[0]    = P[1] - P[-1]
        dPdu[-1]   = P[0] - P[-2]
    else: 
        dPdu[0]    = P[1] - P[0]
        dPdu[-1]   = P[-1] - P[-2]

    dPdv[:, 1:-1] = P[:, 2:] - P[:, :-2]
    if is_v_loop:
        dPdv[:, 0]    = P[:, 1] - P[:, -1]
        dPdv[:, -1]   = P[:, 0] - P[:, -2]
    else:
        dPdv[:, 0]    = P[:, 1] - P[:, 0]
        dPdv[:, -1]   = P[:, -1] - P[:, -2]
    N = torch.cross(dPdu, dPdv, dim=-1)
    N = N / (torch.linalg.norm(N, dim=-1, keepdim=True) + 1e-8)
    return N

