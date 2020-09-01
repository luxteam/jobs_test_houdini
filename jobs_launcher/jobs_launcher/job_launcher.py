import subprocess
import psutil
import time
import core.config


def launch_job(cmd_line, job_timeout=None):
    report = {'total': 0, 'passed': 0, 'failed': 0, 'error': 1, 'skipped': 0, 'duration': 0}
    core.config.main_logger.info('Started job: {}'.format(cmd_line))
    if not job_timeout:
        job_timeout = core.config.TIMEOUT
    started = time.time()

    p = psutil.Popen(cmd_line, stdout=subprocess.PIPE, shell=True)
    try:
        rc = p.wait(timeout=job_timeout)
    except (psutil.TimeoutExpired, subprocess.TimeoutExpired):
        rc = -10
        for child in reversed(p.children(recursive=True)):
            child.terminate()
        p.terminate()

    proc_time = int(time.time() - started)

    report['duration'] = proc_time

    if rc == 0:
        core.config.main_logger.info('Job was completed normal')
        report['passed'] = 1
        report['skipped'] = 0
    elif rc == -10:
        core.config.main_logger.error('Job was terminated by timeout')
    else:
        core.config.main_logger.warning('Job has returned exit code: {}'.format(rc))

    return report
