def firstBSDF():
    return bpy.data.materials["HairBSDF"].node_tree.nodes['Hair BSDF']


def secondBSDF():
    return bpy.data.materials["HairBSDF"].node_tree.nodes['Hair BSDF.001']


def first_ramp():
    return bpy.data.materials["HairBSDF"].node_tree.nodes['ColorRamp']


def second_ramp():
    return bpy.data.materials["HairBSDF"].node_tree.nodes['ColorRamp.001']


def add_shader():
    return bpy.data.materials["HairBSDF"].node_tree.nodes['Add Shader']


def material_output():
    return bpy.data.materials["HairBSDF"].node_tree.nodes['Material Output']


def remove_links():
    for i in bpy.data.materials["HairBSDF"].node_tree.links:
        if (firstBSDF() == i.from_node or secondBSDF() == i.from_node or first_ramp() == i.from_node or second_ramp() == i.from_node):
            bpy.data.materials["HairBSDF"].node_tree.links.remove(i)
