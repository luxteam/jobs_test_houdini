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
    BASELINE_PATH = None
    PACKAGE = None
    COMMON_REPORT_PATH = None

    # case - render scenario; output_dir - output directory for report and images
    def __init__(self, case, output_dir, update_refs, res_x, res_y):
        self.case = case
        self.output = output_dir
        self.update_refs = update_refs
        self.scene_path = os.path.join(Renderer.ASSETS_PATH, Renderer.PACKAGE, case['case'], case['scene'])
        self.case_report_path = os.path.join(self.output, case['case'] + core_config.CASE_REPORT_SUFFIX)
        if not os.path.exists(os.path.join(output_dir, 'Color')):
            os.makedirs(os.path.join(output_dir, 'Color'))
        Renderer.COMMON_REPORT_PATH = os.path.join(output_dir, 'renderTool.log')
        self.width = res_x
        self.height = res_y
        if Renderer.TOOL is None or Renderer.ASSETS_PATH is None:
            raise Exception("Path to tool executable didn't set")
        else:
            self.__prepare_report()

    # Copy baselines images to work dirs
    def __copy_baseline(self):
        # Get original baseline json report from assets folder
        orig_baselines_dir = os.path.join(Renderer.BASELINE_PATH, self.PACKAGE)
        orig_baseline_path = os.path.join(orig_baselines_dir, self.case['case'] + core_config.CASE_REPORT_SUFFIX)
        # Create dir for baselines json for current case group in Work/Baseline/group_name
        copied_baselines_dir = os.path.join(self.output, os.pardir, os.pardir, os.pardir, 'Baseline', self.PACKAGE)
        if not os.path.exists(copied_baselines_dir):
            os.makedirs(copied_baselines_dir)
            # Create dir for baselines images for current case group in Work/Baseline/group_name/Color
            os.makedirs(os.path.join(copied_baselines_dir, 'Color'))
        copied_baseline_path = os.path.join(copied_baselines_dir, self.case['case'] + core_config.CASE_REPORT_SUFFIX)
        try:
            copyfile(orig_baseline_path, copied_baseline_path)
            with open(os.path.join(copied_baseline_path)) as f:
                baseline_json = json.load(f)
            for thumb in [''] + core_config.THUMBNAIL_PREFIXES:
                orig_thumbnail = os.path.join(orig_baselines_dir, baseline_json[thumb + 'render_color_path'])
                copied_thumbnail = os.path.join(copied_baselines_dir, baseline_json[thumb + 'render_color_path'])
                if thumb + 'render_color_path' and os.path.exists(orig_thumbnail):
                    copyfile(orig_thumbnail, copied_thumbnail)
        except Exception as e:
            LOG.error('Failed to copy baseline ' + repr(e) + ' from: ' + orig_baseline_path + ' to: ' + copied_baseline_path)

    # Creates stub image which will be replaced on success render
    def __copy_stub_image(self, status):
        try:
            root_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
            orig_stub_path = os.path.join(root_dir_path, 'jobs_launcher', 'common', 'img', status + '.png')
            copied_stub_path = os.path.join(self.output, 'Color', self.case['case'] + '.png')
            copyfile(orig_stub_path, copied_stub_path)
        except OSError or FileNotFoundError as e:
            LOG.error("Can't create img stub: " + str(e))

    def __is_case_skipped(self):
        skip_pass = sum(set(Renderer.PLATFORM.values()) &
                        set(skip_config) == set(skip_config) for skip_config in self.case.get('skip_on', ''))
        return True if (skip_pass or self.case['status'] == core_config.TEST_IGNORE_STATUS) else False

    def __prepare_report(self):
        skipped = core_config.TEST_IGNORE_STATUS
        if self.__is_case_skipped():
            self.case['status'] = skipped
        if 'frame' not in self.case:
            self.case['frame'] = 1
        report = core_config.RENDER_REPORT_BASE.copy()
        report.update({
            'test_case': self.case['case'],
            'test_group': Renderer.PACKAGE,
            'render_device': Renderer.PLATFORM.get('GPU', 'Unknown'),
            'scene_name': self.case['scene'],
            'width': self.width,
            'height': self.height,
            'tool': str(Renderer.TOOL).split("\\")[-3],
            'date_time': datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
            'file_name': self.case['case'] + self.case.get('extension', '.png'),
            'render_color_path': os.path.join('Color', self.case['case'] + self.case.get('extension', '.png')),
            'render_version': '0',  # TODO
            'plugin_version': '0',  # TODO
            'core_version': '0',
            'frame': self.case['frame']  # TODO
        })
        if self.case['status'] == skipped:
            report['test_status'] = skipped
            report['group_timeout_exceeded'] = False
            self.__copy_stub_image(skipped)
        else:
            report['test_status'] = core_config.TEST_CRASH_STATUS
            self.__copy_stub_image('error')
        with open(self.case_report_path, 'w') as f:
            json.dump([report], f, indent=4)
        if 'Update' not in self.update_refs:
            self.__copy_baseline()

    def __complete_report(self):
        case_log_path = self.case['case'] + '_renderTool.log'
        with open(Renderer.COMMON_REPORT_PATH, "a") as common_log:
            with open(case_log_path, 'r') as case_log:
                common_log.write(case_log.read())
        with open(self.case_report_path, 'r') as f:
            report = json.load(f)[0]
        if self.case['status'] == 'done' and os.path.isfile(report['render_color_path']):
            self.case['status'] = core_config.TEST_SUCCESS_STATUS
            with open(case_log_path, 'r') as f:
                tool_log = [line.strip() for line in f]
            for line in tool_log:
                if "100% Lap=" in line:
                    time = datetime.strptime(line.split()[2].replace('Lap=', ''), '%H:%M:%S.%f')
                    total_seconds = float(time.second + time.minute * 60 + time.hour * 3600) + (time.microsecond / 100000)
                    report['render_time'] = total_seconds
                if 'Peak Memory Usage' in line: report["gpu_memory_max"] = ' '.join(line.split()[-2:])
                if 'Current Memory Usage' in line: report["gpu_memory_usage"] = ' '.join(line.split()[-2:])
        report['render_log'] = case_log_path
        report['test_status'] = self.case['status']
        report['group_timeout_exceeded'] = self.case['group_timeout_exceeded']
        report['render_mode'] = 'GPU'
        with open(self.case_report_path, 'w') as f:
            json.dump([report], f, indent=4)

    def render(self):
        if self.case['status'] != core_config.TEST_IGNORE_STATUS:
            self.case['status'] = 'inprogress'
            cmd_template = '"{tool}" ' \
                           '"{scene}" ' \
                           '-R RPR -V 9 ' \
                           '-o "{file}" ' \
                           '--res {width} {height} ' \
                           '--append-stderr "{log_file}" --append-stdout "{log_file}" ' \
                           '--frame {frame_number}'
            shell_command = cmd_template.format(tool=Renderer.TOOL,
                                                scene=self.scene_path,
                                                file=(os.path.join('Color', self.case['case'] + '.png')),
                                                width=self.width,
                                                height=self.height,
                                                log_file=self.case['case'] + '_renderTool.log',
                                                frame_number = self.case['frame'])
            # saving render command to script for debugging purpose
            shell_script_path = os.path.join(self.output, (self.case['case'] + '_render') + '.bat' if Renderer.is_windows() else '.sh')
            with open(shell_script_path, 'w') as f:
                f.write(shell_command)
            if not Renderer.is_windows():
                try:
                    os.system('chmod +x ' + shell_script_path)
                except OSError as e:
                    LOG.error('Error while setting right for script execution ' + str(e))
            os.chdir(self.output)
            p = subprocess.Popen(shell_script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                p.communicate()
            except psutil.TimeoutExpired as e:
                LOG.error('Render has been aborted by timeout ', str(e))
            finally:
                operation_code = p.returncode
                LOG.info('Return code {}'.format(str(operation_code)))
                self.case['status'] = core_config.TEST_CRASH_STATUS if operation_code != 0 else 'done'
                self.case['group_timeout_exceeded'] = False
                test_cases_path = os.path.join(self.output, 'test_cases.json')
                with open(test_cases_path, 'r') as f:
                    test_cases = json.load(f)
                for case in test_cases:
                    if case['case'] == self.case['case']:
                        case['status'] = self.case['status']
                with open(test_cases_path, 'w') as f:
                    json.dump(test_cases, f, indent=4)
                self.__complete_report()

    @staticmethod
    def is_windows():
        return platform.system() == "Windows"


# Sets up the script parser
def create_parser():
    args = argparse.ArgumentParser()
    args.add_argument('--resolution_x', required=True)
    args.add_argument('--resolution_y', required=True)
    args.add_argument('--update_refs', required=True)
    args.add_argument('--tool', required=True, metavar='<path>')
    args.add_argument('--res_path', required=True)
    args.add_argument('--output', required=True, metavar='<path>')
    args.add_argument('--test_cases', required=True)
    args.add_argument('--package_name', required=True)
    return args


# Configure output_dir
def configure_output_dir(output, tests):
    try:
        os.makedirs(output)
        test_cases_path = os.path.realpath(os.path.join(os.path.abspath(output), 'test_cases.json'))
        copyfile(tests, test_cases_path)
        with open(test_cases_path, 'r') as f:
            test_cases = json.load(f)
            for case in test_cases:
                if 'status' not in case:
                    case['status'] = 'active'
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
        test_cases = configure_output_dir(args.output, args.test_cases)
    except Exception:
        exit(-1)
    # Defines the characteristics of machines which used to execute this script
    try:
        gpu = system_info.get_gpu()
    except:
        LOG.error("Can't get gpu name")
        gpu = 'Unknown'
    Renderer.PLATFORM = {
        'GPU': gpu,
        'OS': platform.system(),
    }
    Renderer.TOOL = args.tool
    Renderer.LOG = LOG
    Renderer.ASSETS_PATH = args.res_path
    Renderer.BASELINE_PATH = os.path.join(args.res_path, "..", "rpr_houdini_autotests_baselines")
    Renderer.PACKAGE = args.package_name
    [case.render() for case in
     [Renderer(case, args.output, args.update_refs, args.resolution_x, args.resolution_y) for case in test_cases]]


if __name__ == '__main__':
    exit(main())
