rom vispy.gloo import *
# https://vispy.org/gallery/gloo/hello_fbo.html

class ContextCanvas(FakeCanvas):
    def __init__(self, size, px_scale=1):
        # Create texture to render to
        FakeCanvas.__init__(self)  # create context
        self._px_scale = int(px_scale)
        self.size = size
        self._size = tuple(int(s) * px_scale for s in size)

        shape = self.physical_size[1], self.physical_size[0]
        self._rendertex = gloo.Texture2D((shape + (3,))) # FIXME: rgba,4
        # Create FBO, attach the color buffer and depth buffer
        self._fbo = gloo.FrameBuffer(self._rendertex, gloo.RenderBuffer(shape))


    @property
    def physical_size(self):
        pass # TODO

    @property
    def pixel_scale(self):
        """The ratio between the number of logical pixels, or 'points', and
        the physical pixels on the device. In most cases this will be 1.0,
        but on certain backends this will be greater than 1. This should be
        used as a scaling factor when writing your own visualisations
        with gloo (make a copy and multiply all your logical pixel values
        by it). When writing Visuals or SceneGraph visualisations, this value
        is exposed as `TransformSystem.px_scale`.
        """
        return self.physical_size[0] / self.size[0]
