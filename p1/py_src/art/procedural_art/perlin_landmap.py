import torch 
# From chatgpt
def fractal_perlin_1d(shape, base_res, octaves=4, persistence=0.5, lacunarity=2.0, device="cpu"):
    noise = torch.zeros(shape, device=device)
    amplitude = 1.0
    freq_x, freq_y = 1.0, 1.0

    for _ in range(octaves):
        res = (int(base_res[0] * freq_x), int(base_res[1] * freq_y))
        noise += amplitude * perlin_noise_2d(shape, res, device=device)

        amplitude *= persistence
        freq_x *= lacunarity
        freq_y *= lacunarity

    noise = (noise - noise.min()) / (noise.max() - noise.min())
    return noise
import torch

def fractal_perlin_custom_lac(shape, base_res, lacunarity_list, persistence_list=None, device="cpu"):
    if persistence_list is None:
        persistence_list = [.5 for i in lacunarity_list]
    if len(persistence_list) != len(lacunarity_list):
        raise ValueError("persistence_list must match lacunarity_list length")

    noise = torch.zeros(shape, device=device)
    amplitude = 1.0
    fx, fy = 1.0, 1.0
    total_amp = 0.0

    # for lac in lacunarity_list:
    for lac, persistence in zip(lacunarity_list, persistence_list):
        # FIXME: zip to get lac, persistence in ...
        res = (int(base_res[0]*fy), int(base_res[1]*fx))
        noise += amplitude * perlin_noise_2d(shape, res, device=device)
        total_amp += amplitude
        amplitude *= persistence
        fx *= lac
        fy *= lac
    noise = noise / total_amp
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    return noise


def perlin_noise_2d(shape, res, device="cpu"):
    """
    shape: (H, W) output size
    res: (rH, rW) number of noise periods (grid resolution)
    """
    H, W = shape
    rH, rW = res

    # Create grid coordinates (0..rH, 0..rW)
    y = torch.linspace(0, rH, H, device=device, dtype=torch.float32)
    x = torch.linspace(0, rW, W, device=device, dtype=torch.float32)
    yy, xx = torch.meshgrid(y, x, indexing="ij")

    # Integer lattice corners
    x0 = xx.floor().long()
    y0 = yy.floor().long()
    x1 = x0 + 1
    y1 = y0 + 1

    # Relative coordinates inside cell
    sx = xx - x0.float()
    sy = yy - y0.float()

    # Fade function (Perlin's smoothstep)
    def fade(t):
        return 6*t**5 - 15*t**4 + 10*t**3

    u = fade(sx)
    v = fade(sy)

    # Random gradient vectors at lattice points
    gradients = torch.randn(rH+1, rW+1, 2, device=device)
    gradients = gradients / gradients.norm(dim=-1, keepdim=True)

    def dot_grid(ix, iy, x, y):
        g = gradients[iy.clamp(0, rH), ix.clamp(0, rW)]
        dx = x - ix.float()
        dy = y - iy.float()
        return (dx * g[..., 0] + dy * g[..., 1])

    # Dot products at the 4 corners
    n00 = dot_grid(x0, y0, xx, yy)
    n10 = dot_grid(x1, y0, xx, yy)
    n01 = dot_grid(x0, y1, xx, yy)
    n11 = dot_grid(x1, y1, xx, yy)

    # Bilinear interpolation with fade curve
    nx0 = n00 * (1 - u) + n10 * u
    nx1 = n01 * (1 - u) + n11 * u
    nxy = nx0 * (1 - v) + nx1 * v

    return nxy


