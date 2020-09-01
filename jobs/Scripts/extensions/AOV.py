
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
