from panda3d.core import (
        TransformState, Mat4,
        NodePath
        )
from panda3d.bullet import (
        BulletHingeConstraint,
        BulletGenericConstraint,
        )
from .matrix import *


def joint_to_bullet_constraint_(joint, parent_node, child_node,debug=False):
    """
    将一个 Build123d joint 转换为 Panda3D Bullet constraint。

    Parameters:
        joint: Build123d joint 对象（RevoluteJoint 或 RigidJoint）
        parent_node: BulletRigidBodyNode 或 NodePath，对应 joint 的父物体
        child_node: BulletRigidBodyNode 或 NodePath，对应 joint 的子物体

    Returns:
        BulletConstraint 对象（已经设置好 frame 和限制）
    """
    if not joint.connected_to:
        raise ValueError("Joint is not connected to another joint!")

    # 两端 joint 的 transform（Mat4）
    frame_a = trsf_to_mat4(joint.location.wrapped.Transformation())
    # print("make frame a",frame_a)
    # ts_a = TransformState.make_mat(frame_a)
    frame_b = trsf_to_mat4(joint.connected_to.location.wrapped.Transformation())
    # print("make frame b",frame_b)
    # ts_b = TransformState.make_mat(frame_b)
    joint_world_mat = trsf_to_mat4(joint.location.wrapped.Transformation())
    joint_world_ts = TransformState.make_mat(joint_world_mat)

# 获取刚体的世界 transform
    parent_ts = parent_node.get_transform()   # 如果是 NodePath 用 getTransform(render)
    child_ts  = child_node.get_transform()



# ❗ 转换为 local frame
    ts_a = parent_ts.invertCompose(joint_world_ts)
    ts_b = child_ts.invertCompose(joint_world_ts)
    if debug:
        print("create hinge for:",parent_node,child_node)
        print("parent ts, child ts")
        print(parent_ts.getMat())
        print(child_ts.getMat())
        print("ts a; ts b")
        print(ts_a.getMat())
        print(ts_b.getMat())
        print("frame a; frame b; frm build123d")
        print(frame_a)
        print(frame_b)
        print("")
    if isinstance(parent_node,NodePath):
        parent_node = parent_node.node()
    if isinstance(child_node, NodePath):
        child_node = child_node.node()
    # RevoluteJoint -> BulletHingeConstraint
    if joint.__class__.__name__ == "RevoluteJoint":
        # print(
        # axis = Vec3(joint.angle_reference[0],
        #             joint.angle_reference[1],
        #             joint.angle_reference[2])
        # pivot 在各自刚体局部坐标
        # 这里假设 joint.relative_to(body_a) 已经给出局部位置
        # pivot_a = LPoint3f(*joint.relative_to(joint.connected_to).position)
        # pivot_b = LPoint3f(*joint.connected_to.relative_to(joint).position)
        # axis_a = axis
        # axis_b = axis
        c = BulletHingeConstraint(
            parent_node, child_node, 
            # pivot_a, pivot_b,
            # axis_a, axis_b
            ts_a,ts_b,
            use_frame_a=True
        )
        
        # 设置角度限制
        min_angle, max_angle = getattr(joint, "angular_range", (0, 360))
        # FIXME
        if max_angle - min_angle < 360:
            print("maxmin",max_angle,min_angle)
        #     c.set_limit(min_angle, max_angle)
    # RigidJoint -> BulletGenericConstraint 固定
    elif joint.__class__.__name__ == "RigidJoint":
        c = BulletGenericConstraint(parent_node, child_node, frame_a, frame_b, use_frame_a=True)
        # 固定位置和旋转
        c.set_linear_limit((0,0,0), (0,0,0))
        c.set_angular_limit((0,0,0), (0,0,0))
    else:
        # 默认 GenericConstraint
        c = BulletGenericConstraint(parent_node, child_node, frame_a, frame_b, use_frame_a=True)

    return c



def joint_to_bullet_constraint(joint, parent_node, child_node, debug=False):
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



