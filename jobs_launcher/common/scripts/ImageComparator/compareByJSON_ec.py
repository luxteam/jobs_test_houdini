import os
import json
from CompareMetrics_ec import CompareMetrics
import sys
from shutil import copyfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
import core.config


def get_diff(current, base):
    if current == base:
        return 0.0
    try:
        return (current - base) / base * 100.0
    except ZeroDivisionError:
        return 0


def check_pixel_difference(work_dir, base_dir, img, baseline_item, tolerance, pix_diff_max):

    for key in core.config.POSSIBLE_JSON_IMG_RENDERED_KEYS:
        if key in img.keys():

            baseline_img_path = os.path.join(base_dir, baseline_item.get('render_color_path', 'not.exist'))

            if img['testcase_timeout_exceeded']:
                img['message'].append('Testcase timeout exceeded')
            elif img['group_timeout_exceeded']:
                img['message'].append('Test group timeout exceeded')
            
            # if baseline image not found - return
            if not os.path.exists(baseline_img_path):
                core.config.main_logger.warning("Baseline image not found by path: {}".format(baseline_img_path))
                img.update({'baseline_color_path': os.path.relpath(os.path.join(base_dir, 'baseline.png'), work_dir)})
                img['message'].append('Baseline not found')
                if img['test_status'] != core.config.TEST_CRASH_STATUS:
                    img.update({'test_status': core.config.TEST_DIFF_STATUS})
                return img

            # else add baseline images paths to json
            img.update({'baseline_color_path': os.path.relpath(os.path.join(base_dir, baseline_item['render_color_path']), work_dir)})
            for thumb in core.config.THUMBNAIL_PREFIXES:
                if thumb + img['file_name'] in baseline_item.keys() and os.path.exists(os.path.join(base_dir, baseline_item[thumb + img['file_name']])):
                    img.update({thumb + 'baseline_color_path': os.path.relpath(os.path.join(base_dir, baseline_item[thumb + img['file_name']]), work_dir)})

            # for crushed and non-executed cases only set baseline img src
            if img['test_status'] != core.config.TEST_SUCCESS_STATUS:
                return img

            render_img_path = os.path.join(work_dir, img[key])
            if not os.path.exists(render_img_path):
                core.config.main_logger.error("Rendered image not found by path: {}".format(render_img_path))
                for possible_extension in core.config.POSSIBLE_BASELINE_EXTENSIONS:
                    if os.path.exists(os.path.join(work_dir, "Color", core.config.TEST_CRASH_STATUS + "." + possible_extension)):
                        img['render_color_path'] = os.path.join("Color", core.config.TEST_CRASH_STATUS + "." + possible_extension)
                        break
                img['message'].append('Rendered image not found')
                img['test_status'] = core.config.TEST_CRASH_STATUS
                return img

            metrics = None
            try:
                metrics = CompareMetrics(render_img_path, baseline_img_path)
            except (FileNotFoundError, OSError) as err:
                core.config.main_logger.error("Error file open: ".format(str(err)))
                return img
            # BUG: loop for all possible keys, but only one compare result
            pix_difference = metrics.getDiffPixeles(tolerance=tolerance)
            img.update({'difference_color': pix_difference})
            if type(pix_difference) is str or pix_difference > pix_diff_max:
                img['message'].append('Unacceptable pixel difference')
                img['test_status'] = core.config.TEST_DIFF_STATUS
            

    return img


# RFE: unite check_rendertime_difference() & check_vram_difference()
def check_rendertime_difference(img, baseline_item, time_diff_max):
    try:
        img.update({'baseline_render_time': baseline_item['render_time']})
    except KeyError:
        core.config.main_logger.error("Baseline render time not defined")
    else:
        img.update({'difference_time': get_diff(img['render_time'], baseline_item['render_time'])})
        # TODO: compare diff with time_diff_max
    return img


def check_vram_difference(img, baseline_item, vram_diff_max):

    try:
        img.update({'baseline_gpu_memory_usage': baseline_item['gpu_memory_usage']})
    except KeyError:
        core.config.main_logger.error()
    else:
        img.update({'difference_vram': get_diff(img['gpu_memory_usage'], baseline_item['gpu_memory_usage'])})
        # TODO: compare diff with vram_diff_max
    return img


def check_ram_difference(img, baseline_item, ram_diff_max):

    try:
        img.update({'baseline_system_memory_usage': baseline_item['system_memory_usage']})
    except KeyError:
        core.config.main_logger.error()
    else:
        img.update({'difference_ram': get_diff(img['system_memory_usage'], baseline_item['system_memory_usage'])})
        # TODO: compare diff with ram_diff_max
    return img


def main(args):
    render_json_path = os.path.join(args.work_dir, core.config.TEST_REPORT_NAME)
    baseline_json_path = os.path.join(args.base_dir, core.config.BASELINE_REPORT_NAME)

    if not os.path.exists(render_json_path):
        core.config.main_logger.error("Render report doesn't exists")
        return 1

    if not os.path.exists(args.base_dir):
        core.config.main_logger.error("Baseline folder doesn't exist. It will be created with baseline stub img.")
        os.makedirs(args.base_dir)

    try:
        if not os.path.exists(os.path.join(args.base_dir, 'baseline.png')):
            copyfile(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, 'img', 'baseline.png'),
                     os.path.join(args.base_dir, 'baseline.png'))
    except (OSError, FileNotFoundError) as err:
        core.config.main_logger.error("Couldn't copy baseline stub: {}".format(str(err)))

    if not os.path.exists(baseline_json_path):
        core.config.main_logger.warning("Baseline or manifest not found by path: {}".format(args.base_dir))
        copyfile(render_json_path, os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED))

    baseline_json = {}
    try:
        with open(render_json_path, 'r') as file:
            render_json = json.loads(file.read())
        with open(baseline_json_path, 'r') as file:
            baseline_json = json.loads(file.read())
    except (FileNotFoundError, OSError, json.JSONDecodeError) as err:
        core.config.main_logger.error("Can't get input data: {}".format(str(err)))

    for img in render_json:
        baseline_item = [x for x in baseline_json if x['test_case'] == img['test_case']]
        if len(baseline_item) == 1:
            check_pixel_difference(args.work_dir, args.base_dir, img, baseline_item[0], args.pix_diff_tolerance, args.pix_diff_max)
            check_rendertime_difference(img, baseline_item[0], args.time_diff_max)
            check_vram_difference(img, baseline_item[0], args.vram_diff_max)
            check_ram_difference(img, baseline_item[0], args.vram_diff_max)
            try:
                img.update({"baseline_render_device": baseline_item[0]['render_device']})
            except KeyError:
                core.config.main_logger.error("Can't get baseline render device")
        else:
            core.config.main_logger.error("Found invalid count of test_cases in baseline json")
            img.update({'baseline_color_path': os.path.relpath(os.path.join(args.base_dir, 'baseline.png'), args.work_dir)})
            img['message'].append('Found invalid count of test_cases in baseline json')
            if img['test_status'] != core.config.TEST_CRASH_STATUS:
                img.update({'test_status': core.config.TEST_DIFF_STATUS})
            continue

    with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
        json.dump(render_json, file, indent=4)

    return 0
