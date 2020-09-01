import sys
import argparse
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
import common.scripts.generate_baseline_default as generate_baseline_default
import common.scripts.generate_baseline_ct as generate_baseline_ct
import common.scripts.generate_baseline_ec as generate_baseline_ec
import core.config
try:
    from local_config import *
except ImportError:
    core.config.main_logger.critical("local config file not found. Default values will be used.")
    core.config.main_logger.critical("Correct report building isn't guaranteed")
    from core.defaults_local_config import *



def create_args_parser():
    args = argparse.ArgumentParser()
    args.add_argument('--results_root')
    args.add_argument('--baseline_root')
    if report_type == 'ct':
        args.add_argument('--case_suffix', required=False, default=core.config.CASE_REPORT_SUFFIX)
    return args


if __name__ == '__main__':
    args = create_args_parser()
    args = args.parse_args()

    args.results_root = os.path.abspath(args.results_root)
    args.baseline_root = os.path.abspath(args.baseline_root)
    
    if report_type == 'default':
        generate_baseline_default.main(args)
    elif report_type == 'ct':
        generate_baseline_ct.main(args)
    elif report_type == 'ec':
        generate_baseline_ec.main(args)
    
