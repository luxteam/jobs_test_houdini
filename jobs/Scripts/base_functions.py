import bpy
import addon_utils
import datetime
import time
import json
import re
import os.path as path
import os
import sys
import pyrpr
import glob
from shutil import copyfile
from rprblender import material_library
from rprblender.utils.user_settings import get_user_settings

WORK_DIR = r'{work_dir}'
TEST_TYPE = '{testType}'
RENDER_DEVICE = '{render_device}'
RES_PATH = r'{res_path}'
PASS_LIMIT = {pass_limit}
RESOLUTION_X = {resolution_x}
RESOLUTION_Y = {resolution_y}
SPU = {SPU}
THRESHOLD = {threshold}
ENGINE = r'{engine}'
LOGS_DIR = path.join(WORK_DIR, 'render_tool_logs')


def event(name, start, case):
    pathEvents = path.join(os.path.dirname(os.path.realpath(__file__)), 'events')
    with open(path.join(pathEvents, str(glob.glob(path.join(pathEvents, '*.json')).__len__() + 1) + '.json'), 'w') as f:
        f.write(json.dumps({{'name': name, 'time': datetime.datetime.utcnow().strftime(
            '%d/%m/%Y %H:%M:%S.%f'), 'start': start, 'case': case}}, indent=4))


def logging(message):
    print(' >>> [RPR TEST] [' +
          datetime.datetime.now().strftime('%H:%M:%S') + '] ' + message)


def reportToJSON(case, render_time=0):
    path_to_file = path.join(WORK_DIR, case['case'] + '_RPR.json')

    with open(path_to_file, 'r') as file:
        report = json.loads(file.read())[0]

    if case['status'] == 'inprogress':
        report['test_status'] = 'passed'
    else:
        report['test_status'] = case['status']

    logging('Create report json ({{}} {{}})'.format(
            case['case'], report['test_status']))

    report['file_name'] = case['case'] + case.get('extension', '.jpg')
    # TODO: render device may be incorrect (if it changes in case)
    report['render_device'] = set_render_device(RENDER_DEVICE)
    report['tool'] = 'Blender ' + bpy.app.version_string.split(' (')[0]
    report['date_time'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    report['render_version'] = get_addon_version()
    report['core_version'] = get_core_version()
    report['render_color_path'] = path.join('Color', report['file_name'])
    report['render_time'] = render_time
    report['test_group'] = TEST_TYPE
    report['test_case'] = case['case']
    report['difference_color'] = 0
    report['script_info'] = case['script_info']
    report['render_log'] = path.join('render_tool_logs', case['case'] + '.log')
    report['scene_name'] = case.get('scene', '')
    report['group_timeout_exceeded'] = False

    with open(path_to_file, 'w') as file:
        file.write(json.dumps([report], indent=4))


def render_tool_log_path(name):
    return path.join(LOGS_DIR, name + '.log')

# TODO: remove support for deprecated core


def get_core_version():
    import pyrprwrap
    if hasattr(pyrprwrap, 'VERSION_MAJOR_MINOR_REVISION'):
        return '{{}}.{{}}.{{}}'.format(pyrprwrap.VERSION_MAJOR,
                                       pyrprwrap.VERSION_MINOR,
                                       pyrprwrap.VERSION_REVISION)


def enable_rpr(case):
    event('Load rpr', True, case)
    if not addon_utils.check('rprblender')[0]:
        addon_utils.enable('rprblender', default_set=True,
                           persistent=False, handle_error=None)
    set_value(bpy.context.scene.render, 'engine', 'RPR')
    event('Load rpr', False, case)


def get_addon_version():
    tuple_ver = sys.modules['rprblender'].bl_info['version']
    version = str(tuple_ver[0]) + '.' + \
        str(tuple_ver[1]) + '.' + str(tuple_ver[2])
    return version


def set_value(path, name, value):
    if hasattr(path, name):
        setattr(path, name, value)
    else:
        logging('No attribute found ' + name)


def set_render_device(render_mode):
    render_device_settings = get_user_settings().final_devices
    if render_mode == 'dual':
        render_device_settings.gpu_states[0] = True
        set_value(render_device_settings, 'cpu_state', True)
        device_name = pyrpr.Context.cpu_device['name'] + \
            ' & ' + pyrpr.Context.gpu_devices[0]['name']
    elif render_mode == 'cpu':
        set_value(render_device_settings, 'cpu_state', True)
        render_device_settings.gpu_states[0] = False
        device_name = pyrpr.Context.cpu_device['name']
    elif render_mode == 'gpu':
        set_value(render_device_settings, 'cpu_state', False)
        render_device_settings.gpu_states[0] = True
        device_name = pyrpr.Context.gpu_devices[0]['name']

    return device_name


def rpr_render(case):
    logging('Render image')
    event('Prerender', False, case['case'])

    event('Postrender', True, case['case'])
    start_time = datetime.datetime.now()
    bpy.ops.render.render(write_still=True)
    render_time = (datetime.datetime.now() - start_time).total_seconds()
    event('Postrender', True, case['case'])

    reportToJSON(case, render_time)


def prerender(case):
    logging('Prerender')
    scene = case.get('scene', '')
    scene_name = bpy.path.basename(bpy.context.blend_data.filepath)
    if scene_name != scene:
        try:
            event('Open scene', True, case['case'])
            bpy.ops.wm.open_mainfile(filepath=os.path.join(RES_PATH, scene))
            event('Open scene', False, case['case'])
        except:
            logging("Can't load scene. Exit Blender")
            bpy.ops.wm.quit_blender()

    enable_rpr(case['case']) # some cases open scene inside case functions

    event('Prerender', True, case['case'])

    scene = bpy.context.scene

    set_value(scene.rpr, 'render_quality', ENGINE)

    device_name = set_render_device(RENDER_DEVICE)

    if RESOLUTION_X and RESOLUTION_Y:
        set_value(scene.render, 'resolution_x', RESOLUTION_X)
        set_value(scene.render, 'resolution_y', RESOLUTION_Y)

    set_value(scene.render.image_settings, 'file_format', 'JPEG')
    set_value(scene.rpr.limits, 'noise_threshold', THRESHOLD)

    set_value(scene.rpr.limits, 'min_samples', 16)
    set_value(scene.rpr.limits, 'max_samples', PASS_LIMIT)

    set_value(scene.rpr, 'use_render_stamp', False)

    # image settings
    set_value(scene.render.image_settings, 'quality', 100)
    set_value(scene.render.image_settings, 'compression', 0)
    set_value(scene.render.image_settings, 'color_mode', 'RGB')

    # output settings
    set_value(scene.render, 'filepath', os.path.join(
        WORK_DIR, 'Color', case['case']))
    set_value(scene.render, 'use_placeholder', True)
    set_value(scene.render, 'use_file_extension', True)
    set_value(scene.render, 'use_overwrite', True)

    for function in case['functions']:
        try:
            if re.match('((^\S+|^\S+ \S+) = |^print|^if|^for|^with)', function):
                exec(function)
            else:
                eval(function)
        except Exception as e:
            logging('Error "{{}}" with string "{{}}"'.format(e, function))
    event('Postrender', False, case['case'])


def save_report(case):
    logging('Save report without rendering for ' + case['case'])

    if not os.path.exists(os.path.join(WORK_DIR, 'Color')):
        os.makedirs(os.path.join(WORK_DIR, 'Color'))

    work_dir = path.join(WORK_DIR, 'Color', case['case'] + '.jpg')
    source_dir = path.join(WORK_DIR, '..', '..', '..',
                           '..', 'jobs_launcher', 'common', 'img')

    if case['status'] == 'inprogress':
        copyfile(path.join(source_dir, 'passed.jpg'), work_dir)
    else:
        copyfile(
            path.join(source_dir, case['status'] + '.jpg'), work_dir)

    enable_rpr(case['case'])

    reportToJSON(case)


def case_function(case):
    functions = {{
        'prerender': prerender,
        'save_report': save_report
    }}

    func = 'prerender'

    if case['functions'][0] == 'check_test_cases_success_save':
        func = 'save_report'

    # 2- retries count
    if case['status'] == 'fail' or case.get('number_of_tries', 1) == 2:
        case['status'] = 'error'
        func = 'save_report'
    elif case['status'] == 'skipped':
        func = 'save_report'
    else:
        case['number_of_tries'] = case.get('number_of_tries', 0) + 1

    functions[func](case)


# place for extension functions


def main():

    if not os.path.exists(os.path.join(WORK_DIR, LOGS_DIR)):
        os.makedirs(os.path.join(WORK_DIR, LOGS_DIR))

    with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
        cases = json.load(json_file)

    event('Open tool', False, next(
        case['case'] for case in cases if case['status'] in ['active', 'fail', 'skipped']))

    total_time = 0

    for case in cases:
        if case['status'] in ['active', 'fail', 'skipped']:
            if case['status'] == 'active':
                case['status'] = 'inprogress'

            with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
                json.dump(cases, file, indent=4)

            log_path = render_tool_log_path(case['case'])
            if not path.exists(log_path):
                with open(log_path, 'w'):
                    logging('Create log file for ' + case['case'])

            logging('In progress: ' + case['case'])

            start_time = datetime.datetime.now()
            case_function(case)
            stop_time = (datetime.datetime.now() - start_time).total_seconds()
            case['time_taken'] = stop_time

            if case['status'] == 'inprogress':
                case['status'] = 'done'
                logging(case['case'] + ' done')

            with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
                json.dump(cases, file, indent=4)

    logging('Time taken: ' + str(total_time))

    event('Close tool', True, cases[-1]['case'])


main()
