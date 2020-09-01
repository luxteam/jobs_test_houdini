import os
import copy
import collections
import itertools
import re

from xml.etree import ElementTree as ET

import core.config

class ParsingError(Exception): pass


default_package_options = {'variables': {}, 'options': collections.OrderedDict()}


def parse_package_manifest(level, filename, cmd_variables, package_options=copy.deepcopy(default_package_options)):
    core.config.main_logger.info('Start processing package {}'.format(filename))

    delim = ' '*level
    file_dir = os.path.dirname(filename)
    root = None
    try:
        xml = ET.parse(filename)
        root = xml.getroot()
    except ET.ParseError as e:
        # print(delim + 'Bad xml: ' + str(e))
        core.config.main_logger.warning('Bad xml: {}'.format(str(e)))
        return

    if root.tag != 'package-manifest':
        print(delim + 'Package parse error "{}": root node "package-manifest" not found'.format(filename))
        core.config.main_logger.warning('Package parse error "{}": root node "package-manifest" not found'.format(filename))
        return

    package_name = root.attrib.get('name')
    if not package_name:
        package_name = os.path.basename(filename).split('.')[0]
        #print(delim + 'Package parse error: attribute "name" not found in package-manifest')
        #return

    print(delim + 'processing package ... "{}"'.format(package_name))

    for elem in root:

        for key, value in cmd_variables.items():
            package_options['variables'][key] = value

        package_options['variables']['CWD'] = file_dir

        if elem.tag == 'variable':
            name = elem.attrib.get('name')
            value = elem.attrib.get('value')
            value = value.format(**package_options['variables'])
            #print(name + '=' + value)
            package_options['variables'][name] = value

        if elem.tag == 'option':
            option_name = elem.attrib.get('name')
            package_options['options'][option_name] = collections.OrderedDict()

            option_type = elem.attrib.get('type')
            if option_type == 'exec':
                exec(elem.text, {"configurations":package_options['options'][option_name]})
            else:
                for configuration_elem in elem:
                    config_name = configuration_elem.attrib.get('name')
                    package_options['options'][option_name][config_name] = collections.OrderedDict()
                    for configuration_param_elem in configuration_elem:
                        configuration_param_name = configuration_param_elem.tag
                        configuration_param_value = configuration_param_elem.text
                        package_options['options'][option_name][config_name][configuration_param_name] = configuration_param_value


def parse_job_manifest(level, job_root_dir, job_rel_path, session_dir, found_jobs, package_options):
    delim = ' ' * level
    job_file_path = os.path.join(job_root_dir, job_rel_path)
    job_rel_dir = os.path.dirname(job_rel_path)

    # for remove Tests dir
    job_rel_dir = os.path.split(job_rel_dir)[1]
    #output_dir = job_rel_dir #os.path.join(session_dir, job_rel_dir)

    #print(delim + 'processing job... {} to dir {} '.format(os.path.abspath(job_file_path), output_dir))
    core.config.main_logger.info('Processing job: {}'.format(job_file_path))

    root = None
    try:
        xml = ET.parse(job_file_path)
        root = xml.getroot()
    except ET.ParseError as e:
        print(delim + 'Bad xml: ' + str(e))
        core.config.main_logger.warning('Bad xml: {}'.format(str(e)))
        return

    if root.tag != 'job-manifest':
        print(delim + 'Package parse error "{}": root node "package-manifest" not found'.format(job_file_path))
        core.config.main_logger.warning(delim + 'Package parse error "{}": root node "package-manifest" not found'.format(job_file_path))
        return

    job_name = os.path.split(os.path.dirname(job_rel_path))[1]
    # job_name = os.path.normpath(os.path.dirname(job_rel_path)).replace('\\', '_')

    print(delim + 'processing job ... "{}"'.format(job_name))

    summary_command_parts = []
    command_parts = []
    outdir = []
    stage_name = None
    stages = []
    job_timeout = []
    timeout = None

    for elem in root:
        if elem.tag == 'variable':
            name = elem.attrib.get('name')
            value = elem.attrib.get('value')
            value = value.format(**package_options['variables'])
            #print(name + '=' + value)
            package_options['variables'][name] = value

        if elem.tag == 'option':
            option_name = elem.attrib.get('name')
            package_options['options'][option_name] = collections.OrderedDict()

            for configuration_elem in elem:
                config_name = configuration_elem.attrib.get('name')
                config_condition = configuration_elem.attrib.get('condition')
                package_options['options'][option_name][config_name] = collections.OrderedDict()
                if config_condition:
                    package_options['options'][option_name][config_name]['condition'] = config_condition
                for configuration_param_elem in configuration_elem:
                    configuration_param_name = configuration_param_elem.tag
                    configuration_param_value = configuration_param_elem.text
                    package_options['options'][option_name][config_name][configuration_param_name] = configuration_param_value

        if elem.tag == 'execute':
            command_parts = [elem.attrib.get('command')]
            stage_name = elem.attrib.get('stage')
            timeout = elem.attrib.get('timeout')
            for arguments_elem in elem:
                command_parts.append(arguments_elem.text)

            if timeout:
                job_timeout.append(int(timeout))
            else:
                job_timeout.append(0)

        if not command_parts == []:
            summary_command_parts.append(command_parts)
            command_parts = []

        if stage_name:
            stages.append(stage_name)
            stage_name = None

        if elem.tag == 'outpath':
            outdir = [elem.attrib.get('value')]

    list_of_lists = []
    for option_name in package_options['options']:
        option = package_options['options'][option_name].items()
        keys = [(option_name, key, value) for (key, value) in option]
        #print(keys)
        list_of_lists.append(keys)

    options = list(itertools.product(*list_of_lists))

    for option in options:
        config_names=[]
        config_dirs=[]
        config_map={}
        ok_conditions = True
        for option_name, config_name, option_val in option:
            if 'condition' in option_val:
                config_condition = option_val['condition']
                config_condition = config_condition.format(**config_map, **package_options['variables'])
                (value, pattern) = str(config_condition).split("=")
                if not re.match(pattern, value):
                    ok_conditions = False
                    break

            config_names.append(option_name + '=' + config_name)
            config_dirs.append(config_name)
            config_map[option_name] = {}
            config_map[option_name]['Name'] = config_name
            for option_val_attr_name, option_val_attr_val in option_val.items():
                config_map[option_name][option_val_attr_name] = option_val_attr_val.format(**config_map, **package_options['variables'])
        if not ok_conditions:
            continue

        job_config_name = ' '.join(config_names)

        execute_command = []
        for command in summary_command_parts:
            execute_command.append(' '.join(command))

        if config_dirs:
            config_output_dir = os.path.join(os.path.join("{SessionDir}", job_rel_dir), os.path.sep.join(config_dirs))
        else:
            config_output_dir = os.path.join(os.path.join("{SessionDir}", job_rel_dir))

        #try:
        #    os.makedirs(config_output_dir)
        #except OSError as e:
        #    print(delim + str(e))
        #    pass

        #print('opt-'+str(option))
        #print('cnf-'+str(config_map))
        #print('cmd-'+str(execute_command))

        execute_command1 = execute_command
        execute_command = []

        try:
            for command in execute_command1:
                execute_command.append(command.format(**config_map, **package_options['variables'], OutputDir=config_output_dir))
        except KeyError as err:
            core.config.main_logger.error("XML variable error: {}".format(str(err)))
        else:
            # outdir = [outdir[0].format(**config_map, **package_options['variables'], OutputDir=config_output_dir)]
            found_jobs.append(
                (
                    job_name,
                    config_dirs,
                    config_map,
                    execute_command,
                    [outdir[0].format(**config_map, **package_options['variables'], OutputDir=config_output_dir)],
                    stages,
                    job_timeout
                )
            )
        #print(delim + execute_command)
        #execute_job(level, execute_command, report['results'][job_name][job_config_name])


def parse_folder(level, job_root_dir, job_sub_path, session_dir, found_jobs, cmd_variables,
                 package_options=copy.deepcopy(default_package_options), test_filter=None, package_filter=None):
    delim = ' '*level
    current_job_dir = os.path.join(job_root_dir, job_sub_path)
    dir_items = os.listdir(path=current_job_dir)

    for dir_item in dir_items:
        dir_item_path = os.path.join(current_job_dir, dir_item)
        if dir_item_path.endswith('.package-manifest.xml') and os.path.isfile(dir_item_path):
            if package_filter:
                if os.path.basename(os.path.dirname(dir_item_path)) in package_filter:
                    parse_package_manifest(level, dir_item_path, cmd_variables, package_options)
            else:
                parse_package_manifest(level, dir_item_path, cmd_variables, package_options)

    for dir_item in dir_items:
        dir_item_path = os.path.join(current_job_dir, dir_item)
        if dir_item_path.endswith('.job-manifest.xml') and os.path.isfile(dir_item_path):
            if test_filter:
                if os.path.basename(os.path.dirname(dir_item_path)) in test_filter:
                    parse_job_manifest(level, job_root_dir, os.path.join(job_sub_path, dir_item),
                                                    session_dir, found_jobs, package_options)
            else:
                parse_job_manifest(level, job_root_dir, os.path.join(job_sub_path, dir_item),
                                   session_dir, found_jobs, package_options)

    for dir_item in dir_items:
        dir_item_path = os.path.join(current_job_dir, dir_item)
        if os.path.isdir(dir_item_path):
            parse_folder(level + 1, job_root_dir, os.path.join(job_sub_path, dir_item), session_dir, found_jobs,
                         cmd_variables, copy.deepcopy(package_options), test_filter=test_filter, package_filter=package_filter)
