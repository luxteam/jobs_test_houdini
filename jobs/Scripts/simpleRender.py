import argparse
import os
import json
import sys
import platform
import psutil
import subprocess
from datetime import datetime
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

    PLATFORM = None
    LOG = None
    TOOL = None
    ASSETS_PATH = None

    # case - render scenario; output_dir - output directory for report and images
    def __init__(self, case, output_dir, update_refs):
        self.case = case
        self.output = output_dir
        self.update_refs = update_refs
        self.scene_path = os.path.join(Renderer.ASSETS_PATH, case['case'], case['scene'])

    def __copy_baseline(self):
        pass

    def __is_case_skipped(self):
        hp = set(Renderer.PLATFORM.values())
        skip_pass = sum(hp &
                        set(skip_config) == set(skip_config) for skip_config in self.case.get('skip_on', ''))
        return True if (skip_pass or self.case['status'] == core_config.TEST_IGNORE_STATUS) else False

    def __copy_baselines(self, report):
        pass

    def __prepare_report(self, width, height, iterations):
        c = self.case
        if self.__is_case_skipped():
            c['status'] = core_config.TEST_IGNORE_STATUS
        report = core_config.RENDER_REPORT_BASE.copy()
        report.update({
            'test_case': c['case'],
            'render_device': Renderer.PLATFORM.get('GPU', 'Unknown'),
            'scene_name': c['scene'],
            'width': width,
            'height': height,
            'iterations': iterations,
            'tool': Renderer.TOOL,
            'date_time': datetime.now().strftime('m/%d/%Y %H:%M:%S'),
            'file_name': c['case'] + '.png'
        })
        # TODO: копировать baseline
        if c['status'] == core_config.TEST_IGNORE_STATUS:
            report['test_status'] = core_config.TEST_IGNORE_STATUS
            report['group_timeout_exceeded'] = False
        with open(os.path.join(self.output, c['scene'] + '.json'), 'w') as f:
            json.dump([report], f, indent=4)

    def render(self, rx, ry, pass_limit):
        if Renderer.TOOL is None or Renderer.ASSETS_PATH is None: raise Exception("Path to husk executable didn't set")
        self.__prepare_report(rx, ry, pass_limit)
        c = self.case
        if c['status'] != core_config.TEST_IGNORE_STATUS:
            LOG.debug('Test scene path:' + self.scene_path)
            command_template = '"{tool}" "{scene}" -R RPR -o "{file}" --res {width} {height}'
            shell_command = command_template.format(tool=Renderer.TOOL, scene=self.scene_path, file=(c['case'] + '.png'),
                                                    width=rx, height=ry)
            # saving render command to script for debugging purpose
            shell_script_path = os.path.join(self.output, 'render.bat' if Renderer.PLATFORM['OS'] == 'Windows' else 'render.sh')
            with open(shell_script_path, 'w') as f:
                f.write(shell_command)
            if Renderer.PLATFORM['OS'] != 'Windows':
                try:
                    os.system('chmod +x ' + shell_script_path)
                except OSError as e:
                    LOG.error('Error while setting right for script execution ' + str(e))
                os.chdir(self.output)  # Investigate the reason of this
                process = psutil.Popen(shell_script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # self.change_status('done')
                # TODO: смена статуса на done
                # TODO: сверка с бейзлайнами
                # TODO: общий репорт


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
        return test_cases
    except OSError as e:
        LOG.error("Failed to read test_cases.json")
        raise e
    except (SameFileError, IOError) as e:
        LOG.error("Can't copy test_cases.json")
        raise e


def main():
    args = create_parser().parse_args()
    test_cases = []
    try:
        test_cases = configure_workdir(args.output, args.test_cases)
    except Exception:
        exit(-1)
    # Define the characteristics of machines which used to execute this script
    Renderer.PLATFORM = {
        'GPU': system_info.get_gpu(),
        'OS': platform.system(),
    }
    Renderer.TOOL = args.tool
    Renderer.LOG = LOG
    Renderer.ASSETS_PATH = args.res_path
    for case in test_cases:
        Renderer(case, args.output, args.update_refs).render(args.resolution_x, args.resolution_y, args.pass_limit)


if __name__ == '__main__':
    exit(main())
