import time
import psutil
from .config import main_logger


def kill_process(process_list):
    for p in psutil.process_iter():
        try:
            p_info = p.as_dict(attrs=['pid', 'name', 'cpu_percent', 'username'])

            if p_info['name'] in process_list:
                try:
                    main_logger.info("Trying to kill process {name}".format(name=p_info['name']))

                    p.terminate()
                    time.sleep(10)

                    p.kill()
                    time.sleep(10)

                    status = p.status()
                    main_logger.error("Process {name} is alive (status: {status}".format(
                        name=p_info["name"],
                        status=status
                    ))
                except psutil.NoSuchProcess:
                    main_logger.info("ATENTION: {name} is killed.".format(
                        name=p_info['name']
                    ))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            main_logger.error("Can't killed process: {name}".format(name=p_info['name']))
