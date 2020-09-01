
def get_material_and_node():
    uber_material = [e for e in bpy.data.materials if e.name == "Uber"][0]
    node_uber = [
        n for n in uber_material.node_tree.nodes if n.name == "RPR Uber.001"][0]
    return uber_material, node_uber


def create_normal_map(attr, image_name):
    uber_material, node_uber = get_material_and_node()
    tree = uber_material.node_tree

    node_imagemap = tree.nodes.new(type='ShaderNodeTexImage')
    image = bpy.data.images.load(os.path.join(RES_PATH, "Maps", image_name))
    node_imagemap.image = image

    node_normalmap = tree.nodes.new(type='ShaderNodeNormalMap')
    tree.links.new(
        node_imagemap.outputs['Color'], node_normalmap.inputs['Color'])

    tree.links.new(node_normalmap.outputs['Normal'], node_uber.inputs[attr])


def create_imagemap(attr, image_name):
    uber_material, node_uber = get_material_and_node()
    tree = uber_material.node_tree
    node_imagemap = tree.nodes.new(type='ShaderNodeTexImage')
    image = bpy.data.images.load(os.path.join(RES_PATH, "Maps", image_name))
    node_imagemap.image = image
    tree.links.new(node_imagemap.outputs['Color'], node_uber.inputs[attr])


def create_imagemapA(attr, image_name):
    uber_material, node_uber = get_material_and_node()
    tree = uber_material.node_tree
    node_imagemap = tree.nodes.new(type='ShaderNodeTexImage')
    image = bpy.data.images.load(os.path.join(RES_PATH, "Maps", image_name))
    node_imagemap.image = image
    tree.links.new(node_imagemap.outputs['Alpha'], node_uber.inputs[attr])


def delete_normalmap():
    uber_material, node_uber = get_material_and_node()
    tree = uber_material.node_tree
    node_normalmap = [
        n for n in uber_material.node_tree.nodes if n.name == "Normal Map"][0]
    uber_material.node_tree.nodes.remove(node_normalmap)
    delete_imagemap()


def delete_imagemap():
    uber_material, node_uber = get_material_and_node()
    tree = uber_material.node_tree
    node_imagemap = [
        n for n in uber_material.node_tree.nodes if n.name == "Image Texture"][0]
    uber_material.node_tree.nodes.remove(node_imagemap)
    default_settings()


def default_settings():
    uber_material, node_uber = get_material_and_node()

    set_value(node_uber, "enable_diffuse", True)
    set_value(node_uber, "diffuse_use_shader_normal", True)
    set_value(node_uber, "separate_backscatter_color", False)
    node_uber.inputs['Diffuse Color'].default_value = (
        0.033, 0.258, 0.503, 1.0)
    node_uber.inputs['Diffuse Weight'].default_value = 1.0
    node_uber.inputs['Diffuse Roughness'].default_value = 0.5
    node_uber.inputs['Backscatter Color'].default_value = (0.5, 0.5, 0.5, 1.0)
    node_uber.inputs['Backscatter Weight'].default_value = 0

    set_value(node_uber, "enable_reflection", True)
    set_value(node_uber, "reflection_mode", 'PBR')
    set_value(node_uber, "reflection_use_shader_normal", True)
    node_uber.inputs['Reflection Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    node_uber.inputs['Reflection IOR'].default_value = 1.5
    node_uber.inputs['Reflection Anisotropy'].default_value = 0.0
    node_uber.inputs['Reflection Anisotropy Rotation'].default_value = 0.0
    node_uber.inputs['Reflection Metalness'].default_value = 0.0
    node_uber.inputs['Reflection Roughness'].default_value = 0.1
    node_uber.inputs['Reflection Weight'].default_value = 1.0

    set_value(node_uber, "enable_coating", False)
    set_value(node_uber, "coating_use_shader_normal", True)
    node_uber.inputs['Coating Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    node_uber.inputs['Coating Weight'].default_value = 1.0
    node_uber.inputs['Coating IOR'].default_value = 1.5
    node_uber.inputs['Coating Roughness'].default_value = 0.01
    node_uber.inputs['Coating Thickness'].default_value = 0
    node_uber.inputs['Coating Transmission Color'].default_value = (
        1.0, 1.0, 1.0, 1.0)

    set_value(node_uber, "enable_refraction", False)
    set_value(node_uber, "refraction_caustics", False)
    set_value(node_uber, "refraction_thin_surface", False)
    set_value(node_uber, "refraction_use_shader_normal", True)
    node_uber.inputs['Refraction Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    node_uber.inputs['Refraction Weight'].default_value = 1.0
    node_uber.inputs['Refraction Roughness'].default_value = 0
    node_uber.inputs['Refraction IOR'].default_value = 1.5
    node_uber.inputs['Refraction Absorption Color'].default_value = (
        1.0, 1.0, 1.0, 1.0)
    node_uber.inputs['Refraction Absorption Distance'].default_value = 0

    set_value(node_uber, "enable_sheen", False)
    node_uber.inputs['Sheen Color'].default_value = (0.5, 0.5, 0.5, 1.0)
    node_uber.inputs['Sheen Tint'].default_value = 0.5
    node_uber.inputs['Sheen Weight'].default_value = 1.0

    set_value(node_uber, "enable_emission", False)
    set_value(node_uber, "emission_doublesided", False)
    set_value(node_uber, "emission_intensity", 1.0)
    node_uber.inputs['Emission Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    node_uber.inputs['Emission Weight'].default_value = 1.0

    set_value(node_uber, "enable_sss", False)
    set_value(node_uber, "sss_multiscatter", False)
    set_value(node_uber, "sss_use_diffuse_color", False)
    node_uber.inputs['Subsurface Color'].default_value = (
        0.436, 0.227, 0.131, 1.0)
    node_uber.inputs['Subsurface Direction'].default_value = 0
    node_uber.inputs['Subsurface Radius'].default_value = (3.67, 1.37, 0.68)
    node_uber.inputs['Subsurface Weight'].default_value = 1.0

    set_value(node_uber, "enable_normal", False)

    set_value(node_uber, "enable_transparency", False)
    node_uber.inputs['Transparency'].default_value = 0

    set_value(node_uber, "enable_displacement", False)
