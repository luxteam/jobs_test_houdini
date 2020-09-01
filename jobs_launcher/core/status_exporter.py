import os
import json
import argparse
from core.config import *


def main(work_dir=''):
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--work_dir')
    args = args_parser.parse_args()

    if work_dir:
        args.work_dir = work_dir

    summary_report = {}
    max_name = 12
    total = {'total': 0, 'passed': 0, 'failed': 0, 'error': 0, 'skipped': 0, 'duration': 0, 'render_duration': 0}
    status_to_export = ""

    if os.path.exists(os.path.join(args.work_dir, SUMMARY_REPORT)):
        with open(os.path.join(args.work_dir, SUMMARY_REPORT), 'r') as file:
            summary_report = json.load(file)

            if len(summary_report) == 0:
                return 0

            max_name = max([len(x) for x in summary_report.keys()])
            max_name = max(max_name, 12)

            for execution in summary_report:
                status_to_export += "_{: <{name_fill}}_ | *{}*/{}/`{}`/`{}`/{}\n".format(
                    execution,
                    summary_report[execution]['summary']['total'],
                    summary_report[execution]['summary']['passed'],
                    summary_report[execution]['summary']['failed'],
                    summary_report[execution]['summary']['error'],
                    summary_report[execution]['summary']['skipped'],
                    name_fill=max_name
                )

    status_to_export = "_{: <{name_fill}}_ | *total*/passed/`failed`/`error`/skipped\n".format("Test Machine", name_fill=max_name) + status_to_export
    # get summary results
    for execution in summary_report:
        for key in total:
            if summary_report[execution]['summary'][key]:
                total[key] += summary_report[execution]['summary'][key]

    with open(os.path.join(args.work_dir, 'summary_status.json'), 'w') as file:
        json.dump(total, file, indent=' ')

    with open(os.path.join(args.work_dir, 'slack_status.json'), 'w') as file:
        json.dump(status_to_export, file, indent=' ')


if __name__ == '__main__':
    main()
