from panda3d.core import LineSegs, Vec3, TransformState


from panda3d.core import TextNode

def add_label(parent, text, pos, scale=0.3, color=(1,1,1)):
    tn = TextNode('label')
    tn.setText(text)
    tn.setTextColor(*color)

    np = parent.attachNewNode(tn)
    np.setPos(pos)
    np.setScale(scale)

    # text will always face to camera 
    np.setBillboardPointEye()

    return np

def draw_frame_axes(parent, transform, scale=1.0, color_scale=(1,1,1), label=None):
    segs = LineSegs()
    r, g, b = color_scale
    
    origin = transform.getPos()
    # mat = transform.getMat3()
    mat4 = transform.getMat()
    mat = mat4.getUpper3()

    # axes direction of local frame
    x_axis = mat.getRow(0)
    y_axis = mat.getRow(1)
    z_axis = mat.getRow(2)

    # X（red）
    # segs.setColor(1, 0, 0, 1)
    segs.setColor(1*r, 0, 0, 1)
    segs.moveTo(origin)
    segs.drawTo(origin + x_axis * scale)

    # Y（green）
    # segs.setColor(0, 1, 0, 1)
    segs.setColor(0, 1*g, 0, 1)
    segs.moveTo(origin)
    segs.drawTo(origin + y_axis * scale)

    # Z（blue）
    # segs.setColor(0, 0, 1, 1)
    segs.setColor(0, 0, 1*b, 1)
    segs.moveTo(origin)
    segs.drawTo(origin + z_axis * scale)
    if label is not None:
        add_label(parent, f"{label}_x", origin + x_axis * scale, color=(1,1,1,.5))
        add_label(parent, f"{label}_y", origin + y_axis * scale, color=(1,1,1,.5))
        add_label(parent, f"{label}_z", origin + z_axis * scale, color=(1,1,1,.5))

    return parent.attachNewNode(segs.create())





def visualize_constraint(world_np, bodyA_np, bodyB_np, constraint, scale=1.0):
    frame_a = constraint.getFrameA()
    frame_b = constraint.getFrameB()

    draw_frame_axes(bodyA_np, frame_a, scale, color_scale=(1, 0.5, 0.5),label="a") # red
    draw_frame_axes(bodyB_np, frame_b, scale, color_scale=(0.5, 0.5, 1),label="b") # blue
