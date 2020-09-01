import os
import json
import argparse
import requests
from platform import system
import subprocess
from core.system_info import get_machine_info, get_gpu


gpu_map = {
	"RadeonPro560": "AMD Radeon Pro 560",
	"AMD_WX7100": "AMD Radeon Pro WX 7100",
	"AMD_WX9100": "AMD Radeon Pro WX 9100",
	"AMD_RXVEGA": "AMD Radeon RX Vega",
	"AMD_RadeonVII": "AMD Radeon VII",
	"NVIDIA_GTX980": "NVIDIA GeForce GTX 980",
	"NVIDIA_GF1080TI": "NVIDIA GeForce GTX 1080 Ti",
	"NVIDIA_RTX2080": "NVIDIA GeForce RTX 2080",
	"NVIDIA_RTX2080TI": "NVIDIA GeForce RTX 2080 Ti"
}


def get_gpu_from_label():
	try:
		node_labels = os.environ["NODE_LABELS"].split()
		for label in node_labels:
			if label.startswith("gpu"):
				GPU_TAG = label[3:]
				break
		return gpu_map.get(GPU_TAG, "undefined")
	except Exception as e:
		print(e)
		return None


def get_render_device():
	render_device = get_gpu()
	if not render_device:
		render_device = get_gpu_from_label()
		print("Will be used value from map: {}".format(render_device))

	return {"render_device": render_device}

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--tool', required=True)
	parser.add_argument('--branch',  required=True)
	parser.add_argument('--build', required=True)
	parser.add_argument('--tests', nargs='+', required=False, default=[])
	parser.add_argument('--tests_package', required=False)
	parser.add_argument('--token', required=True)
	parser.add_argument('--link', required=True)
	args = parser.parse_args()

	if args.tests:
		test_groups = args.tests
	elif args.tests_package:
		try:
			with open('../jobs/{0}'.format(args.tests_package)) as file:
				test_groups = [group.strip() for group in file.read().split('\n') if group]
		except Exception as err:
			print(err)
			return False
	else:
		return False

	data = {
		"build_name": args.build,
		"branch": args.branch,
		"tool": args.tool,
		"groups": test_groups,
		"tester_info": {**get_machine_info(), **get_render_device()}
	}

	print(data)

	requests.post(
		args.link + "/report/setTester",
		params={'data': str(json.dumps(data))},
		headers={"Authorization": "Bearer " + args.token}
	)


if __name__ == "__main__":
	main()
