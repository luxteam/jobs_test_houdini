def get_material_and_node(material_name, node_name):
    material = [e for e in bpy.data.materials if e.name == material_name][0]
    node = [n for n in material.node_tree.nodes if n.name == node_name][0]
    return material, node

def connect_output(material_name, input_node_name, out_node_name, input_attr, out_attr):
    material, input_node = get_material_and_node(material_name, input_node_name)
    out_node = [n for n in material.node_tree.nodes if n.name == out_node_name][0]
    tree = material.node_tree
    tree.links.new(out_node.outputs[out_attr], input_node.inputs[input_attr])

def set_vector(material_name, node_name, vector_name, value):
    material, node = get_material_and_node(material_name, node_name)
    set_value(node.inputs[vector_name], 'default_value', value)

def set_type(material_name, node_name, type_name):
    material, node = get_material_and_node(material_name, node_name)
    set_value(node, 'vector_type', type_name)

def remove_output_links(material_name, node_name):
    material, node = get_material_and_node(material_name, node_name)
    material_links = material.node_tree.links
    for i in material_links:
        if (node == i.from_node):
            material_links.remove(i)

def set_default():
    set_vector('Material', 'Mapping', 'Location', (0, 0, 0))
    set_vector('Material', 'Mapping', 'Rotation', (0, 0, 0))
    set_vector('Material', 'Mapping', 'Scale', (1, 1, 1))
