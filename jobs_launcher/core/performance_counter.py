import glob
import os
import json
from datetime import datetime


def event_record(dir, event, start, case=''):
    dir = os.path.join(dir, 'events')
    if not os.path.exists(dir):
        os.makedirs(dir)
    event_file_name = str(glob.glob(os.path.join(dir, '*.json')).__len__() + 1) + '.json'
    with open(os.path.join(dir, event_file_name), 'w') as f:
        f.write(json.dumps({'name': event, 'time': datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S.%f'), 'start': start, 'case': case}, indent=4))