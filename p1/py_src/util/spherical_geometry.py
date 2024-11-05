from typing import Union, Dict, Tuple, List
import torch
import sympy as sp
# spherial coordinate conversion
# from x y z to standare spherical coordinate, and vice versa


def angular_spherical_distance(
    theta1: torch.Tensor,
    theta2: torch.Tensor,
    phi1: torch.Tensor,
    phi2: torch.Tensor,

) -> torch.Tensor:
    """
    spherical distance
    input: tensors of arbitrary same shape
        theta1: longtitude for point 1
        theta2: longtitude for point 2
        phi1: latitude for point 1
        phi2: latitude for point 2

    output angular distance
    """
    delta_theta = theta1 - theta2
    ret = torch.arccos(
        torch.sin(phi1) * torch.sin(phi2)
        + torch.cos(phi1) * torch.cos(phi2) * torch.cos(delta_theta)
    )
    return ret


def cart2sphr_sp(x, y, z, rho=None):
    if rho is None:
        rho = sp.sqrt(x**2 + y**2 + z**2)
    phi = sp.atan(y / x).simplify()
    theta = sp.acos(z / rho).simplify()
    return theta, phi


def cart2sphr_pt(xyz, rho=None):
    if rho is None:
        rho = torch.norm(xyz, p=2, dim=1)
    phi = torch.atan2(xyz[:, 1], xyz[:, 0])
    theta = torch.acos(xyz[:, 2] / rho)
    # if any(torch.isnan(phi)) :
    # nan = torch.isnan(phi)
    # print("xyz",xyz[nan], "theta",theta[nan], "phi",phi[nan])
    # if any(torch.isnan(theta)) :
    # nan = torch.isnan(theta)
    # print("xyz",xyz[nan], "theta",theta[nan], "phi",phi[nan])
    return theta, phi


def sphr2cart_sp(
    theta: sp.Expr, phi: sp.Expr
) -> Tuple[sp.Expr, sp.Expr, sp.Expr]:
    x = sp.sin(theta) * sp.cos(phi)
    y = sp.sin(theta) * sp.sin(phi)
    z = sp.cos(theta)
    return x, y, z


def sphr2cart_pt(
    theta: torch.Tensor, phi: torch.Tensor
) -> torch.Tensor:
    x = (torch.sin(theta) * torch.cos(phi)).unsqueeze(-1)
    y = (torch.sin(theta) * torch.sin(phi)).unsqueeze(-1)
    z = (torch.cos(theta)).unsqueeze(-1)
    return torch.concat([x, y, z], dim=-1)
    # return x, y, z


# crater heightmap


# split triangles to approximate sphere

# spherical midpoints
def spherical_midpoint_pt(
    theta1: torch.Tensor,
    theta2: torch.Tensor,
    phi1: torch.Tensor,
    phi2: torch.Tensor,
) -> torch.Tensor:
    """
    spherical midpoints
    input:
        theta1: longtitude for point 1
        theta2: longtitude for point 2
        phi1: latitude for point 1
        phi2: latitude for point 2

    output midpoint theta and phi
    """
    def xyz(t, p):
        # t and p are of [N]; return [N, 3]
        x = (torch.sin(t) * torch.cos(p)).unsqueeze(-1)
        y = (torch.sin(t) * torch.sin(p)).unsqueeze(-1)
        z = (torch.cos(t)).unsqueeze(-1)
        return torch.concat([x, y, z], dim=-1)
    xyz1 = xyz(theta1, phi1)
    xyz2 = xyz(theta2, phi2)
    xyz_new = (xyz1 + xyz2) / 2
    t_, p_ = cart2sphr_pt(xyz_new)
    return t_, p_


def spherical_midpoint_sp(
    theta1: sp.Expr,
    theta2: sp.Expr,
    phi1: sp.Expr,
    phi2: sp.Expr,
) -> Tuple[sp.Expr, sp.Expr]:
    """
    spherical midpoints
    input:
        theta1: longtitude for point 1
        theta2: longtitude for point 2
        phi1: latitude for point 1
        phi2: latitude for point 2

    output midpoint theta and phi
    """
    def xyz(t, p):
        x = sp.sin(t)*sp.cos(p)
        y = sp.sin(t)*sp.sin(p)
        z = sp.cos(t)
        return x, y, z
    x1, y1, z1 = xyz(theta1, phi1)
    x2, y2, z2 = xyz(theta2, phi2)
    x_, y_, z_ = (x1+x2)/2, (y1+y2)/2, (z1+z2)/2
    t_, p_ = cart2sphr_sp(x_, y_, z_)
    return t_, p_


def is_clockwise_on_sphr(
    theta1, theta2, theta3,
    phi1, phi2, phi3
) -> bool:
    # TODO: calc xyz
    # TODO: cross product
    # TODO: dot product
    pass
