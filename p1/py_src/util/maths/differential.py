import torch


def compute_uv_normals(
        P: torch.Tensor,
        is_u_loop=False,
        is_v_loop=False,
    ):
    """
    Compute vertex normals for a UV-parameterized curve surface.

    Parameters
    ----------
    P : torch.Tensor of shape (M, N, 3)
        3D coordinates of the surface grid. Each element P[i,j] represents
        a point in 3D space with coordinates (x, y, z) corresponding to
        the (u, v) parameter grid indices:
            P[i, j] = (x, y, z)

    is_u_loop : bool, optional (default=False)
        Whether the surface is periodic/looping in the U direction. If True,
        finite differences at the boundaries wrap around.

    is_v_loop : bool, optional (default=False)
        Whether the surface is periodic/looping in the V direction. If True,
        finite differences at the boundaries wrap around.

    Returns
    -------
    N : torch.Tensor of shape (M, N, 3)
        Normal vectors at each vertex. Each row corresponds to the normalized
        3D normal vector (nx, ny, nz) at P[i,j], computed as the cross product
        of finite differences along U and V directions:

            dPdu = derivative along U
            dPdv = derivative along V
            N[i,j] = normalize(cross(dPdu[i,j], dPdv[i,j]))

    Notes
    -----
    - The function uses central differences for interior points and forward/backward
      differences for boundary points unless the surface is looping.
    - A small epsilon (1e-8) is added during normalization to prevent division by zero.
    """
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


def compute_vertex_normals_torch(vertices: torch.Tensor, triangles: torch.Tensor):
    """
    Parameters
    ----------
    vertices : torch.Tensor of shape (N, 3)
        Vertex position matrix. Each row represents one vertex in 3D space:
        (x, y, z).

    triangles : torch.Tensor of shape (M, 3)
        Triangle index matrix. Each row represents one triangle face and
        contains three integer indices (i, j, k). These indices refer to
        rows in `vertices`, meaning the triangle is formed by the three
        vertices:
            vertices[i], vertices[j], vertices[k].

    Returns
    -------
    normals : torch.Tensor of shape (N, 3)
        Vertex normal matrix. Each row corresponds to a vertex in `vertices`
        and stores the normalized 3D normal vector (nx, ny, nz). The normal
        is computed by averaging the normals of all faces sharing that vertex.
    """

    normals = torch.zeros_like(vertices)

    for tri in triangles:
        a, b, c = tri

        p0 = vertices[a]
        p1 = vertices[b]
        p2 = vertices[c]

        e1 = p1 - p0
        e2 = p2 - p0

        face_normal = torch.cross(e1, e2)

        normals[a] += face_normal
        normals[b] += face_normal
        normals[c] += face_normal

    # normalize
    lens = torch.linalg.norm(normals, dim=1, keepdim=True)
    lens[lens == 0] = 1

    normals = normals / lens

    return normals
