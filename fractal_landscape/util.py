import torch
# spherial coordinate conversion
# from x y z to standare spherical coordinate, and vice versa


def angular_spherical_distance(
    phi1: torch.Tensor,
    phi2: torch.Tensor,
    theta1: torch.Tensor,
    theta2: torch.Tensor
) -> torch.Tensor:
    """
    spherical distance
    input: tensors of arbitrary same shape
        phi1: latitude for point 1
        phi2: latitude for point 2
        theta1: longtitude for point 1
        theta2: longtitude for point 2
    output angular distance
    """
    delta_theta = theta1 - theta2
    ret = torch.arccos(
        torch.sin(phi1) * torch.sin(phi2)
        + torch.cos(phi1) * torch.cos(phi2) * torch.cos(delta_theta)
    )
    return ret


# crater heightmap


# split triangles to approximate sphere
