import numpy as np
from vispy import app, scene, visuals
from vispyutil.canvas import SynchronizedCanvas

# starfield generators


# background
class StarCanvas(SynchronizedCanvas):
    def __init__(self, n_stars, rho=10):
        SynchronizedCanvas.__init__(self)
        self.n_stars = n_stars
        # randomly pick stars
        np.random.seed(0)  # todo: use torch random state
        cos_pos_theta = np.random.uniform(-1,1, n_stars)
        pos_theta = np.arccos(cos_pos_theta)
        pos_phi = np.random.uniform(0,2*np.pi, n_stars)
        sizes = np.random.uniform(0, 5, n_stars)
        r = rho * np.sin(pos_theta)
        x = r * np.cos(pos_phi)
        y = r * np.sin(pos_phi)
        z = rho * np.cos(pos_theta)
        positions = np.vstack([x,y,z]).T
        scatter = scene.visuals.Markers()
        scatter.set_data(positions, edge_color=None, face_color='white', size=sizes, symbol='o')
        # Add scatter plot to the view
        self.view.add(scatter)
# stars
