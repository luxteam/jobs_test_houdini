def getLightWithType(light_type):
    light_data = bpy.data.lights['Point']
    set_value(light_data, 'type', light_type)
    return bpy.data.lights['Point']
