#!usr/bin/env python3
import os
import re
import platform
import subprocess
import psutil
import cpuinfo


def get_gpu():
    """Get installed GPU by system tools.

    Windows
      Use **wmci** ignore 'Microsoft Remote Adapter' in case of RDP connection.
      Remove **Nvidia** prefix from GPU name.
    Linux
      Use **clinfo**
    Darwin
      Use **system profiler** ignore integrated graphics by Intel.

    :returns: GPU name defined by system tool | False
    :rtype: str | bool

    .. todo:: Implement mGPU support
    """
    try:
        render_device = os.getenv('CIS_RENDER_DEVICE')
        if render_device:
            return render_device
        operation_sys = platform.system()
        if operation_sys == "Windows":
            s = subprocess.Popen("wmic path win32_VideoController get name", stdout=subprocess.PIPE)
            stdout = s.communicate()
            render_device = [x.replace('\r', '').strip(' ') for x in stdout[0].decode("utf-8").split('\n')[1:] if x.replace('\r', '').strip(' ') and 'Microsoft' not in x][0]
            render_device = render_device.replace('Nvidia ', '').replace('NVIDIA ', '')
        elif operation_sys == "Linux":
            cli_command = """clinfo --raw | grep CL_DEVICE_BOARD_NAME | awk '{for(i=3;i<=NF;++i) printf "%s ", $i; print ""}'"""
            s = subprocess.Popen(cli_command, stdout=subprocess.PIPE, shell=True)
            stdout = s.communicate()
            render_device = stdout[0].decode("utf-8").split('\n')[0].replace('\r', '').strip(' ')
        elif operation_sys == "Darwin":
            cli_command = """system_profiler SPDisplaysDataType | grep Chipset\ Model | awk '{for(i=3;i<=NF;++i) printf "%s ", $i; print ""}' """
            s = subprocess.Popen(cli_command, stdout=subprocess.PIPE, shell=True)
            stdout = s.communicate()
            # FIXME: hot fix for eGPU
            render_device = [x for x in stdout[0].decode("utf-8").split('\n') if "Intel" not in x and x][0].replace('\r', '').strip(' ')
    except Exception as err:
        print("ERROR during GPU detecting: {}".format(str(err)))
        return False

    return render_device


def get_machine_info():

    def get_os():
        custom_os_name = os.getenv('CIS_OS')
        if custom_os_name:
            return custom_os_name
        if platform.system() == "Windows":
            return '{} {}({})'.format(platform.system(), platform.release(), platform.architecture()[0])
        elif platform.system() == "Darwin":
            return '{} {}({})'.format(platform.system(), platform.mac_ver()[0], platform.architecture()[0])
        else:
            return '{} {}({})'.format(platform.linux_distribution()[0], platform.linux_distribution()[1], platform.architecture()[0])

    def get_driver_ver():
        if os.name == "nt":
            proc = subprocess.Popen(
                ["reg", "query",
                 r"HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}\0000",
                 "/v", "ReleaseVersion"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            stdout, stderr = proc.communicate(10)
            return re.search(r'\s(\d+\.\d+.+?)$', stdout.decode(), re.MULTILINE).group(1).strip()
        else:
            return "not_implemented_for_" + os.name

    def get_host():
        if platform.system() == "Darwin" and platform.node().endswith('.local'):
            return platform.node()[:-len('.local')]
        else:
            return platform.node()

    try:
        info = {}
        info['os'] = get_os()
        # info['driver'] = get_driver_ver()
        info['host'] = get_host()
        info['cpu_count'] = str(psutil.cpu_count())
        # info['asic'] = get_gpu_name()
        # info['asic_count'] = "{}".format(len(info['asic'].split('+')))
        info['ram'] = psutil.virtual_memory().total / 1024 ** 3
        # info['cpu'] = platform.processor()
        info['cpu'] = cpuinfo.get_cpu_info()['brand']
        return info
    except Exception as err:
        print("Exception: {0}".format(err))
        return {"host": platform.node()}


def print_machine_info():
    info = get_machine_info();
