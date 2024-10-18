from panda3d.bullet import (
       BulletGenericConstraint,
)

class FixedConstraint(BulletGenericConstraint):
    def __init__(self, *args, **kwargs):
        BulletGenericConstraint.__init__(self, *args, *kwargs)
        # Disable all linear movement along X, Y, Z axes
        linear_limit = 0,0
        self.setLinearLimit(0, *linear_limit)  # x
        self.setLinearLimit(1, *linear_limit)  # y
        self.setLinearLimit(2, *linear_limit)  # z
        # Disable all angular rotation around X, Y, Z axes
        angular_limit = 0,0
        self.setAngularLimit(0, *angular_limit)  # rotation around x
        self.setAngularLimit(1, *angular_limit)  # rotation around y
        self.setAngularLimit(2, *angular_limit) 