def get_material_and_node():
    volume_material = [e for e in bpy.data.materials if e.name == "vdb_mat"][0]
    volume_node = [
        n for n in volume_material.node_tree.nodes if n.type == "PRINCIPLED_VOLUME"][0]
    return volume_material, volume_node


def create_checker_texture(attr):
    volume_material, volume_node = get_material_and_node()
    tree = volume_material.node_tree
    checker_texture_node = tree.nodes.new(type='ShaderNodeTexChecker')

    if type(volume_node.inputs[attr].default_value) == float:
        tree.links.new(
            checker_texture_node.outputs['Fac'], volume_node.inputs[attr])
    else:
        tree.links.new(
            checker_texture_node.outputs['Color'], volume_node.inputs[attr])


def create_imagemap(attr, image_name):
    volume_material, volume_node = get_material_and_node()
    tree = volume_material.node_tree

    imagemap_node = tree.nodes.new(type='ShaderNodeTexImage')
    image = bpy.data.images.load(os.path.join(RES_PATH, "Maps", image_name))
    imagemap_node.image = image

    if type(volume_node.inputs[attr].default_value) == float:
        tree.links.new(
            imagemap_node.outputs['Alpha'], volume_node.inputs[attr])
    else:
        tree.links.new(
            imagemap_node.outputs['Color'], volume_node.inputs[attr])


def delete_imagemap():
    uber_material, node_uber = get_material_and_node()
    node_imagemap = [
        n for n in uber_material.node_tree.nodes if n.name == "Image Texture"][0]
    uber_material.node_tree.nodes.remove(node_imagemap)


def delete_checker():
    uber_material, node_uber = get_material_and_node()
    node_imagemap = [
        n for n in uber_material.node_tree.nodes if n.name == "Checker Texture"][0]
    uber_material.node_tree.nodes.remove(node_imagemap)
