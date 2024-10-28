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
def cart2sphr_sp(x,y,z):
    theta=sp.atan(y/x).simplify()
    phi=sp.acos(z/rho).simplify()
    return theta, phi

# crater heightmap


# split triangles to approximate sphere

# spherical midpoints
def spherical_midpoint(
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
    pass

def spherical_midpoint_sp(
    theta1: sp.Expr,
    theta2: sp.Expr,
    phi1: sp.Expr,
    phi2: sp.Expr,
) -> sp.Expr:
    """
    spherical midpoints
    input:
        theta1: longtitude for point 1
        theta2: longtitude for point 2
        phi1: latitude for point 1
        phi2: latitude for point 2

    output midpoint theta and phi
    """
    def xyz(t,p):
        x = sp.sin(t)*sp.cos(p)
        y = sp.sin(t)*sp.sin(p)
        z = sp.cos(t)
        return x,y,z
    x1, y1, z1 = xyz(theta1,phi1)
    x2, y2, z2 = xyz(theta2,phi2)
    x_,y_,z_ = (x1+x2)/2, (y1+y2)/2, (z1+z2)/2
    t_, p_ = cart2sphr_sp(x_,y_,z_)
    return t_, p_
