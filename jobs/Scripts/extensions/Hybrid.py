def pre39():
    for area in bpy.context.workspace.screens[0].areas:
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'RENDERED'
    for area in bpy.context.workspace.screens[0].areas:
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'


def post39():
    for area in bpy.context.workspace.screens[0].areas:
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'


def deactivate_all_aovs(view_layer):
    for number in range(1, 30):
        view_layer.rpr.enable_aovs[number] = False


def deleteOldRenderLayerNodes(nodes):
    for node in nodes:
        if node.type in ("R_LAYERS", "COMPOSITE", "OUTPUT_FILE"):
            try:
                nodes.remove(node)
            except Exception as e:
                print('Error while removing node: ' + str(e))


def set_geometric_normal_aov(name):
    view_layer = bpy.context.view_layer
    deactivate_all_aovs(view_layer)
    set_value(view_layer, 'use', True)
    set_value(bpy.context.scene.render, 'use_single_layer', False)
    set_value(bpy.context.scene, 'use_nodes', True)
    nodes = bpy.data.scenes[0].node_tree.nodes
    deleteOldRenderLayerNodes(nodes)
    render_layer = nodes.new('CompositorNodeRLayers')
    composite = nodes.new('CompositorNodeComposite')
    file_output = nodes.new('CompositorNodeOutputFile')
    bpy.context.scene.node_tree.links.new(
        render_layer.outputs['Image'], composite.inputs['Image'])
    file_output.base_path = os.path.join(WORK_DIR, 'Color')
    file_output.file_slots.new(name)
    view_layer.rpr.enable_aovs[6] = True
    bpy.context.scene.node_tree.links.new(
        render_layer.outputs['Geometric Normal'], file_output.inputs[1])


def post_geometric_normal_aov(name):
    test_case_image = os.path.join(WORK_DIR, 'Color', name + '.jpg')
    aov_image = os.path.join(WORK_DIR, 'Color', name + '0040.jpg')
    if os.path.exists(test_case_image):
        os.remove(test_case_image)
    if os.path.exists(aov_image):
        os.rename(aov_image, test_case_image)


def duplicate_suzanne():
    obj1 = bpy.data.objects['Suzanne.001']
    obj2 = bpy.data.objects['Suzanne.002']
    obj3 = bpy.data.objects['Suzanne.003']
    obj4 = bpy.data.objects['Suzanne.004']
    obj5 = bpy.data.objects['Suzanne']
    obj1.select_set(state=True)
    obj2.select_set(state=True)
    obj3.select_set(state=True)
    obj4.select_set(state=True)
    obj5.select_set(state=True)
    bpy.ops.object.duplicate(linked=True)
    obj1.location.z = obj1.location.z + 1.3
    obj2.location.z = obj2.location.z + 1.3
    obj3.location.z = obj3.location.z + 1.3
    obj4.location.z = obj4.location.z + 1.3
    obj5.location.z = obj5.location.z + 1.3
