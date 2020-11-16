import argparse
import os
import json
import sys
from shutil import copyfile, SameFileError

# Configure script context and importing jobs_launcher and logger to it (DO NOT REPLACE THIS CODE)
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
    )
)
import jobs_launcher.core.config as core_config
import jobs_launcher.core.system_info as system_info

LOG = core_config.main_logger


# Makes report and execute case
class Renderer:
    HARDWARE_PLATFORM = None
    TOOL = None
    LOG = None

    # case - render scenario; output_dir - output directory for report and images
    def __init__(self, case, output_dir):
        self.case = case
        self.output = output_dir

    def __is_case_skipped(self):
        hp = Renderer.HARDWARE_PLATFORM
        skip_pass = sum(hp &
                        set(skip_config) == set(skip_config) for skip_config in self.case.get('skip_on', ''))
        return True if (skip_pass or self.case['status'] == 'skipped') else False

    def __prepare_report(self):
        c = self.case
        if self.__is_case_skipped():
            c['status'] = 'skipped'
        report = core_config.RENDER_REPORT_BASE.copy()

    def render(self, rx, ry):
        self.__prepare_report()
        # if not Renderer.TOOL: raise Exception("Path to husk executable didn't set")
        # c = self.case
        # name = c.case['case']
        # self.change_status('done')

    def _change_status(self, status):
        pass


# Sets up the script parser
def create_parser():
    p = argparse.ArgumentParser()
    p.add_argument('--resolution_x', required=True)
    p.add_argument('--resolution_y', required=True)
    p.add_argument('--pass_limit', required=True)
    p.add_argument('--update_refs', required=True)
    p.add_argument('--tool', required=True, metavar='<path>')
    p.add_argument('--res_path', required=True)
    p.add_argument('--output', required=True, metavar='<path>')
    p.add_argument('--test_cases', required=True)
    return p


# Configure output_dir
def configure_workdir(workdir, tests):
    try:
        os.makedirs(workdir)
        test_cases_path = os.path.realpath(os.path.join(os.path.abspath(workdir), 'test_cases.json'))
        copyfile(tests, test_cases_path)
        with open(test_cases_path, 'r') as orig_file:
            test_cases = json.load(orig_file)
            for case in test_cases:
                if 'status' not in case: case['status'] = 'active'
            with open(test_cases_path, 'w') as copied_file:
                json.dump(test_cases, copied_file, indent=4)
        LOG.info("Scenes to render: {}".format([name['scene'] for name in test_cases]))
        return test_cases, test_cases_path
    except OSError as e:
        LOG.error("Failed to read test_cases.json")
        raise e
    except (SameFileError, IOError) as e:
        LOG.error("Can't copy test_cases.json")
        raise e


def main():
    args = create_parser().parse_args()
    test_cases = []
    test_cases_path = None
    try:
        test_cases, test_cases_path = configure_workdir(args.output, args.test_cases)
    except Exception:
        exit(-1)
    # Define the characteristics of machines which used to execute this script
    Renderer.HARDWARE_PLATFORM = {
        system_info.get_gpu(),
        system_info.get_machine_info().get('os'),
    }
    Renderer.TOOL = args.tool
    Renderer.LOG = LOG
    for case in test_cases:
        Renderer(case, test_cases_path).render(args.resolution_x, args.resolution_y)


if __name__ == '__main__':
    exit(main())
