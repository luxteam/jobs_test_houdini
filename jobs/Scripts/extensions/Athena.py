import platform
import getpass

if (platform.system() == 'Windows'):
    CONFIG_PATH = os.path.expandvars(
        '%appdata%/Blender Foundation/Blender/2.83/scripts/addons/rprblender/config.py')
    ATHENA_DIR = os.path.expandvars('%appdata%/../Local/Temp/rprblender/')
elif (platform.system() == 'Darwin'):
    CONFIG_PATH = os.path.expandvars(
        '~/Library/Application Support/Blender/2.83/scripts/addons/rprblender/config.py')
    ATHENA_DIR = os.environ['TMPDIR'] + 'rprblender/'
# TODO implement Ubuntu


def validate_athena(case):
    athena_files = os.listdir(ATHENA_DIR)
    if(not athena_files or len(athena_files) > 1):
        logging('Athena files weren\'t found') if not athena_files else logging(
            'More than one file found')
        copyfile(path.join(WORK_DIR, '..', '..', '..', '..', 'jobs_launcher', 'common',
                           'img', 'error.jpg'), path.join(WORK_DIR, 'Color', case['case'] + '.jpg'))
    json_file = athena_files[0]
    try:
        with open(path.join(ATHENA_DIR, json_file), 'r') as athena_file:
            logging('Athena file content:\n' + athena_file.read())
            athena_file.seek(0)
            data = json.load(athena_file)
            copyfile(path.join(WORK_DIR, '..', '..', '..', '..', 'jobs_launcher', 'common',
                               'img', 'passed.jpg'), path.join(WORK_DIR, 'Color', case['case'] + '.jpg'))
    except Exception as e:
        logging(e)
        copyfile(path.join(WORK_DIR, '..', '..', '..', '..', 'jobs_launcher', 'common',
                           'img', 'error.jpg'), path.join(WORK_DIR, 'Color', case['case'] + '.jpg'))
