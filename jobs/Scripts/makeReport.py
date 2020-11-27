import sys
import json
import os
import argparse

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work_dir', required=True)
    args = parser.parse_args()
    wd = args.work_dir
    reports = [
        json.load(open(os.path.join(wd, e), 'r'))[0] for e in list(
            filter(
                lambda x: x.endswith('RPR.json'), os.listdir(wd)
            )
        )
    ]
    with open(os.path.join(wd, 'report.json'), 'w') as f: json.dump(reports, f, indent=4)
