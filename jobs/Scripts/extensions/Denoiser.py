def resetSceneAttributes():
    view_layer = bpy.context.view_layer
    set_value(view_layer.rpr.denoiser, 'enable', False)
    set_value(view_layer.rpr.denoiser, 'filter_type', 'EAW')

    set_value(view_layer.rpr.denoiser, 'color_sigma', 0.75)
    set_value(view_layer.rpr.denoiser, 'depth_sigma', 0.01)
    set_value(view_layer.rpr.denoiser, 'normal_sigma', 0.01)
    set_value(view_layer.rpr.denoiser, 'trans_sigma', 0.01)

    set_value(view_layer.rpr.denoiser, 'radius', 1)
    set_value(view_layer.rpr.denoiser, 'p_sigma', 0.1)

    set_value(view_layer.rpr.denoiser, 'samples', 4)
    set_value(view_layer.rpr.denoiser, 'half_window', 4)
    set_value(view_layer.rpr.denoiser, 'bandwidth', 0.2)

    set_value(view_layer.rpr.denoiser, 'ml_color_only', True)

    set_value(bpy.context.scene.rpr, 'use_tile_render', False)
