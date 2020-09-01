def get_material_and_node(material_name, node_name):
    material = [e for e in bpy.data.materials if e.name == material_name][0]
    node = [n for n in material.node_tree.nodes if n.name == node_name][0]
    return material, node

def connect_output(material_name, input_node_name, out_node_name, input_attr, out_attr):
    material, input_node = get_material_and_node(material_name, input_node_name)
    out_node = [n for n in material.node_tree.nodes if n.name == out_node_name][0]
    tree = material.node_tree
    tree.links.new(out_node.outputs[out_attr], input_node.inputs[input_attr])