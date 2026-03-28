from panda3d.core import (
        TransformState, Mat4,
        NodePath
        )
from panda3d.bullet import (
        BulletHingeConstraint,
        BulletGenericConstraint,
        )
from .matrix import *




def joint_to_bullet_constraint(joint, parent_node, child_node, debug=False):
    """
    Convert a Build123d joint into a Panda3D Bullet constraint.

    Parameters:
        joint: A Build123d joint object (RevoluteJoint or RigidJoint)
        parent_node: BulletRigidBodyNode or NodePath corresponding to the parent object of the joint
        child_node: BulletRigidBodyNode or NodePath corresponding to the child object of the joint

    Returns:
        A BulletConstraint object with its frame and limits properly configured.
    """

    # joint and joint.connected_to has same location in build123d
    # world_frame: panda3d Mat4
    world_frame = trsf_to_mat4(joint.location.wrapped.Transformation())
    world_ts = TransformState.makeMat(world_frame)
    parent_transform = parent_node.getTransform()
    child_transform = child_node.getTransform()
    # # parent_frame = world_frame * parent_transform.inverse()
    # parent_frame = world_ts.compose(parent_transform.getInverse())
    parent_frame = (parent_transform.getInverse()).compose(world_ts)
    # # child_frame = world_frame * child_transform.inverse()
    # child_frame = world_ts.compose(child_transform.getInverse())
    child_frame = (child_transform.getInverse()).compose(world_ts)
    # parent_mat = parent_node.getMat()
    # child_mat  = child_node.getMat()

    # parent_mat_inv = Mat4(parent_mat)
    # child_mat_inv = Mat4(child_mat)
    # parent_mat_inv.invertInPlace()
    # child_mat_inv.invertInPlace()
    # parent_frame = parent_mat_inv * world_frame
    # child_frame  = child_mat_inv * world_frame
    if debug:
        print("create hinge for:",parent_node,child_node)
        print("frame a; frame b; frm build123d")
        print(parent_frame.getMat())
        print(child_frame.getMat())
        print("")

    if isinstance(parent_node,NodePath):
        parent_node = parent_node.node()
    if isinstance(child_node, NodePath):
        child_node = child_node.node()

    if joint.__class__.__name__ == "RevoluteJoint":

        c = BulletHingeConstraint(
            parent_node, child_node, 
            # parent_transform, child_transform,
            # pivot_a, pivot_b,
            # axis_a, axis_b
            parent_frame, child_frame,
            use_frame_a=True
        )
        
        # set angular limit  
        min_angle, max_angle = getattr(joint, "angular_range", (0, 360))
        # FIXME
        if max_angle - min_angle < 360:
            print("maxmin",max_angle,min_angle)
        #     c.set_limit(min_angle, max_angle)
    # RigidJoint -> BulletGenericConstraint fixed 
    elif joint.__class__.__name__ == "RigidJoint":
        c = BulletGenericConstraint(parent_node, child_node, parent_frame, child_frame, use_frame_a=True)
        # fix position and rotation
        c.set_linear_limit((0,0,0), (0,0,0))
        c.set_angular_limit((0,0,0), (0,0,0))
    else:
        # GenericConstraint by default, not fixed
        c = BulletGenericConstraint(parent_node, child_node, parent_frame,child_frame, use_frame_a=True)

    return c



