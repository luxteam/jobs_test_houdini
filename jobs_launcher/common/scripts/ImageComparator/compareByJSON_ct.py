import os
import json
from CompareMetrics_ct import CompareMetrics
import shutil
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
import core.config


def get_diff(current, previous):
    if current == previous:
        return 0.0
    try:
        return (current - previous) / previous * 100.0
    except ZeroDivisionError:
        return 0


def get_pixel_difference(work_dir, base_dir, img, baseline_json, tolerance, pix_diff_max):

    for key in core.config.IMG_KEYS_FOR_COMPARE:
        if key in img.keys():
            render_img_path = os.path.join(work_dir, img[key])

            try:
                baseline_img_path = os.path.join(base_dir, baseline_json[key])
            except KeyError as err:
                core.config.main_logger.error("No such file in baseline: {}".format(str(err)))
                continue

            if not os.path.exists(baseline_img_path):
                core.config.main_logger.error("BROKEN BASELINE MANIFEST")
                continue

            metrics = None
            try:
                metrics = CompareMetrics(render_img_path, baseline_img_path)
            except (FileNotFoundError, OSError) as err:
                core.config.main_logger.error(str(err))
                return img

            pix_difference = metrics.getDiffPixeles(tolerance=tolerance)
            img.update({'difference_color': pix_difference})
            if type(pix_difference) is str or pix_difference > pix_diff_max:
                img['test_status'] = core.config.TEST_DIFF_STATUS
            img.update({'baseline_color_path': os.path.relpath(
                os.path.join(base_dir, baseline_json[key]), work_dir)})
            for thumb in core.config.THUMBNAIL_PREFIXES:
                if os.path.exists(os.path.join(base_dir, thumb + baseline_json[key])):
                    img.update({thumb + 'baseline_color_path': os.path.relpath(
                        os.path.join(base_dir, thumb + baseline_json[key]), work_dir)})

    return img


def get_rendertime_difference(img, baseline_item, time_diff_max):
    if 'render_time' not in baseline_item.keys():
        render_time = img['render_time']
    else:
        render_time = img['render_time']
    baseline_time = baseline_item['render_time']

    img.update({'difference_time': get_diff(render_time, baseline_time)})
    img.update({'baseline_render_time': baseline_time})

    return img


def main(args):
    render_json_path = os.path.join(args.work_dir, core.config.TEST_REPORT_NAME)

    if not os.path.exists(render_json_path):
        core.config.main_logger.error("Render report doesn't exists")
        return 1

    if not os.path.exists(args.base_dir):
        core.config.main_logger.warning("Baseline or manifest not found by path: {}".format(args.base_dir))
        shutil.copyfile(render_json_path, os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED))
        return 1

    with open(render_json_path, 'r') as file:
        render_json = json.loads(file.read())

    for img in render_json:
        # NOTE: for conversion scripts testing only
        # add original render key
        if args.case_suffix:
            or_baseline_json_path = os.path.join(args.base_dir, img['test_case'] + args.case_suffix)
            if not os.path.exists(or_baseline_json_path):
                core.config.main_logger.error("Test case {} original render report not found".format(img['test_case']))
            else:
                with open(or_baseline_json_path, 'r') as file:
                    original_json = json.loads(file.read())
                if len(original_json) <= 0:
                    core.config.main_logger.error("{} case OR json is empty".format(img['test_case']))
                else:
                    for key in ['original_color_path', 'original_render_log']:
                        try:
                            original_path = original_json[0][key]
                            img.update({key: os.path.relpath(os.path.join(args.base_dir, original_path),
                                                             args.work_dir)})
                        except KeyError:
                            core.config.main_logger.error("{} case OR json is incomplete".format(img['test_case']))

                        try:
                            original_render_time = original_json[0]['render_time']
                            img.update({'or_render_time': original_render_time})
                            img.update({'difference_time_or': get_diff(img['render_time'], original_render_time)})
                        except KeyError:
                            core.config.main_logger.error("{} case OR json is incomplete".format(img['test_case']))

        baseline_json_path = os.path.join(args.base_dir, img['test_case'] + core.config.CASE_REPORT_SUFFIX)
        if not os.path.exists(baseline_json_path):
            core.config.main_logger.error("Test case {} report not found".format(img['test_case']))
            continue
        else:
            with open(baseline_json_path, 'r') as file:
                baseline_item = json.loads(file.read())

        get_pixel_difference(args.work_dir, args.base_dir, img, baseline_item[0], args.pix_diff_tolerance, args.pix_diff_max)
        get_rendertime_difference(img, baseline_item[0], args.time_diff_max)
        try:
            img.update({"baseline_render_device": baseline_item[0]['render_device']})
        except KeyError:
            core.config.main_logger.error("Can't get baseline render device")

    with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'w') as file:
        json.dump(render_json, file, indent=4)

    return 0
