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
    PACKAGE = None

    # case - render scenario; output_dir - output directory for report and images
    def __init__(self, case, output_dir, update_refs):
        self.case = case
        self.output = output_dir
        self.update_refs = update_refs
        self.scene_path = os.path.join(Renderer.ASSETS_PATH, Renderer.PACKAGE, case['scene'])
        self.case_report_path = os.path.join(self.output, case['scene'] + core_config.CASE_REPORT_SUFFIX)
        os.makedirs(os.path.join(output_dir, 'Color'))

    # Copy baselines images to work dirs
    def __copy_baseline(self):
        # Get original baseline json report from assets folder
        orig_baselines_dir = os.path.join(Renderer.ASSETS_PATH, 'rpr_houdini_autotests_baselines', self.PACKAGE)
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
        except:
            LOG.error('Failed to copy baseline ' + orig_baseline_path)

    # Creates stub image which will be replaced on success render
    def __copy_stub_image(self, status):
        try:
            root_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
            orig_stub_path = os.path.join(root_dir_path, 'jobs_launcher', 'common', 'img', status + '.png')
            copied_stub_path = os.path.join(self.output, 'Color', self.case['scene'] + '.png')
            copyfile(orig_stub_path, copied_stub_path)
        except OSError or FileNotFoundError as e:
            LOG.error("Can't create img stub: " + str(e))

    def __is_case_skipped(self):
        hp = set(Renderer.PLATFORM.values())
        skip_pass = sum(hp &
                        set(skip_config) == set(skip_config) for skip_config in self.case.get('skip_on', ''))
        return True if (skip_pass or self.case['status'] == core_config.TEST_IGNORE_STATUS) else False

    def __prepare_report(self, width, height, iterations):
        skipped = core_config.TEST_IGNORE_STATUS
        c = self.case
        if self.__is_case_skipped():
            c['status'] = skipped
        if c['status'] != 'done':
            if c['status'] == 'inprogress':
                c['status'] = 'active'
        report = core_config.RENDER_REPORT_BASE.copy()
        report.update({
            'test_case': c['case'],
            'test_group': Renderer.PACKAGE if Renderer.PACKAGE is not None else "",
            'render_device': Renderer.PLATFORM.get('GPU', 'Unknown'),
            'scene_name': c['scene'],
            'width': width,
            'height': height,
            'iterations': iterations,
            'tool': Renderer.TOOL,
            'date_time': datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
            'file_name': c['scene'] + c.get('extension', '.png'),
            'render_color_path': os.path.join('Color', c['scene'] + c.get('extension', '.png'))
        })
        if c['status'] == skipped:
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
        with open(self.case_report_path, 'r') as f:
            # json.dump() always saves the data in structure json array, but when we work with one case, like now, we
            # 100% knew that there is only one element
            report = json.load(f)[0]
        # TODO: add extra fields to report
        #report["gpu_memory_total"] = testJson["gpumem.total.mb"]
        #report["gpu_memory_max"] = testJson["gpumem.max.alloc.mb"]
        #report["gpu_memory_usage"] = testJson["gpumem.usage.mb"]
        #report["system_memory_usage"] = testJson["sysmem.usage.mb"]
        report['test_status'] = self.case['status']
        with open(self.case_report_path, 'w') as f:
            json.dump([report], f, indent=4)

    def render(self, rx, ry, pass_limit):
        if Renderer.TOOL is None or Renderer.ASSETS_PATH is None:
            raise Exception("Path to husk executable didn't set")
        self.__prepare_report(rx, ry, pass_limit)
        c = self.case
        if c['status'] != core_config.TEST_IGNORE_STATUS:
            cmd_template = '"{tool}" "{scene}" -R RPR -V 9 -o "{file}" --res {width} {height} --append-stderr "{log_file}" --append-stdout "{log_file}"'
            shell_command = cmd_template.format(tool=Renderer.TOOL,
                                                scene=self.scene_path,
                                                file=(os.path.join('Color', c['scene'] + '.png')),
                                                width=rx,
                                                height=ry,
                                                log_file=os.path.join(self.output, 'render.log'))
            # saving render command to script for debugging purpose
            shell_script_path = os.path.join(self.output, 'render' + '.bat' if Renderer.PLATFORM['OS'] else '.sh')
            with open(shell_script_path, 'w') as f:
                f.write(shell_command)
            if Renderer.PLATFORM['OS'] != 'Windows':
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
                self.case['status'] = core_config.TEST_CRASH_STATUS if operation_code != 0 else 'done'
                test_cases_path = os.path.join(self.output, 'test_cases.json')
                with open(test_cases_path, 'r') as f:
                    test_cases = json.load(f)
                for case in test_cases:
                    if case['case'] == self.case['case']:
                        case['status'] = self.case['status']
                with open(test_cases_path, 'w') as f:
                    json.dump(test_cases, f, indent=4)
                self.__complete_report()

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
    p.add_argument('--package_name', required=True)
    return p


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
    Renderer.PLATFORM = {
        'GPU': system_info.get_gpu(),
        'OS': platform.system(),
    }
    Renderer.TOOL = args.tool
    Renderer.LOG = LOG
    Renderer.ASSETS_PATH = args.res_path
    Renderer.PACKAGE = args.package_name
    for case in test_cases:
        Renderer(case, args.output, args.update_refs).render(args.resolution_x, args.resolution_y, args.pass_limit)


if __name__ == '__main__':
    exit(main())
