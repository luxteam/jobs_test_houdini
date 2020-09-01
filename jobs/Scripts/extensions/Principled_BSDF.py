def get_material_and_node():
    prbsdf_material = [
        e for e in bpy.data.materials if e.name == 'Principled BSDF'][0]
    prbsdf_node = [
        n for n in prbsdf_material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0]
    return prbsdf_material, prbsdf_node


def create_normal_map(attr, image_name):
    prbsdf_material, prbsdf_node = get_material_and_node()
    tree = prbsdf_material.node_tree

    # create image map
    imagemap_node = tree.nodes.new(type='ShaderNodeTexImage')
    image = bpy.data.images.load(os.path.join(RES_PATH, 'Maps', image_name))
    imagemap_node.image = image

    # crete normal map
    normalmap_node = tree.nodes.new(type='ShaderNodeNormalMap')
    tree.links.new(
        imagemap_node.outputs['Color'], normalmap_node.inputs['Color'])

    # connect normal with material
    tree.links.new(normalmap_node.outputs['Normal'], prbsdf_node.inputs[attr])


def create_imagemap(attr, image_name):
    prbsdf_material, prbsdf_node = get_material_and_node()
    tree = prbsdf_material.node_tree

    imagemap_node = tree.nodes.new(type='ShaderNodeTexImage')
    image = bpy.data.images.load(os.path.join(RES_PATH, 'Maps', image_name))
    imagemap_node.image = image

    if type(prbsdf_node.inputs[attr].default_value) == float:
        tree.links.new(
            imagemap_node.outputs['Alpha'], prbsdf_node.inputs[attr])
    else:
        tree.links.new(
            imagemap_node.outputs['Color'], prbsdf_node.inputs[attr])


def delete_imagemaps():
    prbsdf_material = [
        e for e in bpy.data.materials if e.name == "Principled BSDF"][0]
    normal_nodes = [
        n for n in prbsdf_material.node_tree.nodes if n.type == 'NORMAL']
    for normal_node in normal_nodes:
        prbsdf_material.node_tree.nodes.remove(normal_node)

    imagemap_nodes = [
        n for n in prbsdf_material.node_tree.nodes if n.type == 'TEX_IMAGE']
    for imagemap_node in imagemap_nodes:
        prbsdf_material.node_tree.nodes.remove(imagemap_node)
