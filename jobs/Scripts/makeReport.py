import sys
import json
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
import jobs_launcher.core.performance_counter as perf_count

def generate_common_report(workdir):
    files = os.listdir(workdir)
    reports = list(filter(lambda x: x.endswith('RPR.json'), files))
    result_json = ""
    for file in range(len(reports)):
        if len(reports) == 1:
            f = open(os.path.join(workdir, reports[file]), 'r')
            content = f.read()
            f.close()
            result_json += content
            break
        if file == 0:
            f = open(os.path.join(workdir, reports[file]), 'r')
            content = f.read()
            f.close()
            content = content[:-2]
            content = content + "," + "\r\n"
            result_json += content
        elif file == (len(reports)) - 1:
            f = open(os.path.join(workdir, reports[file]), 'r')
            content = f.read()
            f.close()
            content = content[2:]
            result_json += content
        else:
            f = open(os.path.join(workdir, reports[file]), 'r')
            content = f.read()
            f.close()
            content = content[2:]
            content = content[:-2]
            content = content + "," + "\r\n"
            result_json += content
    with open(os.path.join(workdir, "report.json"), 'w') as file:
        file.write(result_json)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work_dir', required=True)
    args = parser.parse_args()
    generate_common_report(args.work_dir)
