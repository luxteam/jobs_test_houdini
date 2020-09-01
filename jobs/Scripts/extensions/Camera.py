def resetSceneAttributes():
    set_value(bpy.context.object.data, 'type', 'PERSP')
    set_value(bpy.context.object.data, 'lens', 53.93)
    set_value(bpy.context.object.data, 'lens_unit', 'MILLIMETERS')

    set_value(bpy.context.object.data, 'shift_x', 0)
    set_value(bpy.context.object.data, 'shift_y', 0)
    set_value(bpy.context.object.data, 'clip_start', 0.1)
    set_value(bpy.context.object.data, 'clip_end', 100)

    set_value(bpy.context.object.data, 'sensor_fit', 'AUTO')
    set_value(bpy.context.object.data, 'sensor_width', 32)

    set_value(bpy.context.object.data.dof, 'use_dof', False)
    set_value(bpy.context.object.data.dof, 'focus_distance', 0)
    set_value(bpy.context.object.data.dof, 'aperture_fstop', 128)
    set_value(bpy.context.object.data.dof, 'aperture_blades', 0)
