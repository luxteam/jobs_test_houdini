import ast
import os
import json
from core.config import *
import sys
import argparse
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
try:
    from local_config import *
except ImportError:
    main_logger.critical("local config file not found. Default values will be used.")
    main_logger.critical("Correct report building isn't guaranteed")
    from core.defaults_local_config import *


# match gpu and OS labels in Jenkins and platform name which session_report.json contains
PLATFORM_CONVERTATIONS = {
	"Windows": {
		"os_name": "Windows 10(64bit)",
		"cards": {
			"AMD_RXVEGA": "Radeon RX Vega",
			"AMD_RX5700XT": "AMD Radeon RX 5700 XT",
			"AMD_RadeonVII": "AMD Radeon VII",
			"NVIDIA_GF1080TI": "GeForce GTX 1080 Ti",
			"AMD_WX7100": "AMD Radeon (TM) Pro WX 7100 Graphics",
			"AMD_WX9100": "Radeon (TM) Pro WX 9100",
			"NVIDIA_RTX2080TI": "GeForce RTX 2080 Ti",
			"NVIDIA_RTX2080": "NVIDIA GeForce RTX 2080"
		}
	},
	"Ubuntu18": {
		"os_name": "Ubuntu 18.04(64bit)",
		"cards": {
			"AMD_RadeonVII": "AMD Radeon VII",
			"NVIDIA_GTX980": "GeForce GTX 980"
		}
	},
	"OSX": {
		"os_name": "Darwin 10.14.6(64bit)",
		"cards": {
			"AMD_RXVEGA": "AMD Radeon RX Vega 56 (Metal)"
		}
	}
}

def get_lost_tests_count(data, tool_name, test_package_name):
	# number of lost tests = number of tests in test package
	if tool_name == 'blender' or tool_name == 'maya' or tool_name == 'rprviewer':
		lost_tests_count = len(data)
	elif tool_name == 'max':
		lost_tests_count = len(data['cases'])
	elif tool_name == 'core':
		lost_tests_count = len(data)
		for scene in data:
			json_name = scene['scene'].replace('rpr', 'json')
			with open(os.path.join("..", "core_tests_configuration", test_package_name, json_name), "r") as file:
				configuration_data = json.load(file)
			if 'aovs' in configuration_data:
				lost_tests_count += len(configuration_data['aovs'])
	else:
		raise Exception('Unexpected tool name: ' + tool_name)
	return lost_tests_count


def main(lost_tests_results, tests_dir, output_dir, execution_type, tests_list):
	lost_tests_data = {}
	lost_tests_results = ast.literal_eval(lost_tests_results)

	tests_list = tests_list.split(' ')

	# check that session_reports is in each results directory
	try:
		results_directories = next(os.walk(os.path.abspath(output_dir)))[1]
		for results_directory in results_directories:
			session_report_exist = False
			for path, dirs, files in os.walk(os.path.abspath(os.path.join(output_dir, results_directory))):
				for file in files:
					if file.endswith(SESSION_REPORT):
						session_report_exist = True
						if execution_type == 'default':
							with open(os.path.join(path, file), "r") as report:
								session_report = json.load(report)
							for test_package_name in session_report['results']:
								case_results = session_report["results"][test_package_name][""]
								if case_results["total"] == 0:
									with open(os.path.join(tests_dir, "jobs", "Tests", test_package_name, TEST_CASES_JSON_NAME[tool_name]), "r") as tests_conf:
										data = json.load(tests_conf)
									number_of_cases = get_lost_tests_count(data, tool_name, test_package_name)
									case_results["error"] = number_of_cases
									case_results["total"] = number_of_cases
									session_report["summary"]["error"] += number_of_cases
									session_report["summary"]["total"] += number_of_cases
							with open(os.path.join(path, file), "w") as report:
								json.dump(session_report, report, indent=4, sort_keys=True)
						else:
							with open(os.path.join(path, file), "r") as report:
								session_report = json.load(report)
							if 'summary' not in session_report or 'total' not in session_report['summary'] or session_report['summary']['total'] <= 0:
								lost_tests_results.append(results_directory)
						break
				if session_report_exist:
					break
			if not session_report_exist:
				lost_tests_results.append(results_directory)
	except:
		# all results were lost
		pass

	if execution_type == 'regression':
		with open(os.path.join(tests_dir, "jobs", "regression.json"), "r") as file:
			test_packages = json.load(file)
		for test_package_name in test_packages:
			try:
				lost_tests_count = len(set(test_packages[test_package_name].split(',')))
				for lost_test_result in lost_tests_results:
					gpu_name = lost_test_result.split('-')[0]
					os_name = lost_test_result.split('-')[1]
					# join converted gpu name and os name
					joined_gpu_os_names = PLATFORM_CONVERTATIONS[os_name]["cards"][gpu_name] + "-" + PLATFORM_CONVERTATIONS[os_name]["os_name"]
					if joined_gpu_os_names not in lost_tests_data:
						lost_tests_data[joined_gpu_os_names] = {}
					lost_tests_data[joined_gpu_os_names][test_package_name] = lost_tests_count
			except Exception as e:
				print("Failed to count lost tests for test group {}. Reason: {}".format(test_package_name, str(e)))
	elif execution_type == 'split_execution':
		for lost_test_result in lost_tests_results:
			try:
				gpu_name = lost_test_result.split('-')[0]
				os_name = lost_test_result.split('-')[1]
				test_package_name = lost_test_result.split('-')[2]
				with open(os.path.join(tests_dir, "jobs", "Tests", test_package_name, TEST_CASES_JSON_NAME[tool_name]), "r") as file:
					data = json.load(file)
				lost_tests_count = get_lost_tests_count(data, tool_name, test_package_name)
				# join converted gpu name and os name
				joined_gpu_os_names = PLATFORM_CONVERTATIONS[os_name]["cards"][gpu_name] + "-" + PLATFORM_CONVERTATIONS[os_name]["os_name"]
				if joined_gpu_os_names not in lost_tests_data:
					lost_tests_data[joined_gpu_os_names] = {}
				lost_tests_data[joined_gpu_os_names][test_package_name] = lost_tests_count
			except Exception as e:
				print("Failed to count lost tests for test group {}. Reason: {}".format(test_package_name, str(e)))
	else:
		for test_package_name in tests_list:
			try:
				with open(os.path.join(tests_dir, "jobs", "Tests", test_package_name, TEST_CASES_JSON_NAME[tool_name]), "r") as file:
					data = json.load(file)
				lost_tests_count = get_lost_tests_count(data, tool_name, test_package_name)
				for lost_test_result in lost_tests_results:
					gpu_name = lost_test_result.split('-')[0]
					os_name = lost_test_result.split('-')[1]
					# join converted gpu name and os name
					joined_gpu_os_names = PLATFORM_CONVERTATIONS[os_name]["cards"][gpu_name] + "-" + PLATFORM_CONVERTATIONS[os_name]["os_name"]
					if joined_gpu_os_names not in lost_tests_data:
						lost_tests_data[joined_gpu_os_names] = {}
					lost_tests_data[joined_gpu_os_names][test_package_name] = lost_tests_count
			except Exception as e:
				print("Failed to count lost tests for test group {}. Reason: {}".format(test_package_name, str(e)))

	os.makedirs(output_dir, exist_ok=True)
	with open(os.path.join(output_dir, LOST_TESTS_JSON_NAME), "w") as file:
		json.dump(lost_tests_data, file, indent=4, sort_keys=True)
