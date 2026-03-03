# class OffScreenBufferFactory:
    # def __init__(self, pipe, graphicsEngine, clear_color=None):
        
class BufferFactory:
    def __init__(self, parent):
        """
        parent is a showbase 
        """
        self.parent = parent 

    def makeOutputBuffer(self, name, sort, props, winprops)
