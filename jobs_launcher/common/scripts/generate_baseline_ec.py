import argparse
import shutil
import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
import core.config


def main(args):
    if os.path.exists(args.baseline_root):
        shutil.rmtree(args.baseline_root)

    # find and process report_compare.json files
    for path, dirs, files in os.walk(args.results_root):
        for file in files:
            if file == core.config.TEST_REPORT_NAME_COMPARED:
                # create destination folder in baseline location
                os.makedirs(os.path.join(args.baseline_root, os.path.relpath(path, args.results_root)))
                # copy json report with new names
                shutil.copyfile(os.path.join(path, file),
                                os.path.join(args.baseline_root, os.path.relpath(os.path.join(path, core.config.BASELINE_REPORT_NAME), args.results_root)))

                with open(os.path.join(path, file), 'r') as json_report:
                    report = json.loads(json_report.read())

                # copy files which described in json
                for test in report:
                    # copy rendered images and thumbnails
                    for img in core.config.POSSIBLE_JSON_IMG_RENDERED_KEYS_THUMBNAIL + core.config.POSSIBLE_JSON_IMG_RENDERED_KEYS:
                        if img in test.keys():
                            rendered_img_path = os.path.join(path, test[img])
                            baseline_img_path = os.path.relpath(rendered_img_path, args.results_root)

                            # create folder in first step for current folder
                            if not os.path.exists(os.path.join(args.baseline_root, os.path.split(baseline_img_path)[0])):
                                os.makedirs(os.path.join(args.baseline_root, os.path.split(baseline_img_path)[0]))

                            try:
                                shutil.copyfile(rendered_img_path,
                                                os.path.join(args.baseline_root, baseline_img_path))
                            except IOError as err:
                                core.config.main_logger.warning("Error baseline copy file: {}".format(str(err)))
