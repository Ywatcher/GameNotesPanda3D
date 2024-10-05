from vispy.scene import TurntableCamera
class UnboundedTurnableCam(TurntableCamera):
    @property
    def elevation(self):
        """Get the camera elevation angle in degrees.
        
        The camera points along the x-y plane when the angle is 0.
        """
        return self._elevation
    
    @elevation.setter
    def elevation(self, elev):
        elev = float(elev)
        # FIXME: use elev % 360 instead of this
        while elev < -180:
            elev += 360
        while elev > 180:
            elev -= 360
        self._elevation = elev
        self.view_changed()