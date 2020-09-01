from . import engine_logger


main_logger = engine_logger.create_main_logger()

TIMEOUT = 2400

RENDER_REPORT_BASE = {
    "file_name": "",
    "date_time": "",
    "script_info": [],
    "render_color_path": "",
    "test_case": "",
    "render_version": "",
    "test_status": "undefined",
    "tool": "",
    "render_time": -0.0,
    "sync_time": -0.0,
    "baseline_render_time": -0.0,
    "render_mode": "",
    "scene_name": "",
    "test_group": "",
    "difference_color": -0.0,
    "difference_time": -0.0,
    "core_version": "",
    "render_device": "",
    "difference_color_2": -0,
    "testcase_timeout": 0,
    "message": [],
    "testcase_timeout_exceeded": False,
    "group_timeout_exceeded": True
}

RENDER_REPORT_DEFAULT_PACK = {

}

RENDER_REPORT_EC_PACK = {
    "minor_version": "",
    "iterations": -0,
    "width": -0,
    "height": -0,
    "system_memory_usage": -0.0,
    "gpu_memory_usage": -0.0,
    "gpu_memory_total": -0.0,
    "gpu_memory_max": -0.0,
    "baseline_gpu_memory_usage": -0.0,
    "baseline_system_memory_usage": -0.0,
    "difference_vram": -0.0,
    "difference_ram": -0.0,
    'tahoe_log': 'not.exist'
}

RENDER_REPORT_CT_PACK = {
    "difference_time_or": -0.0,
    "or_render_time": -0.0,
    "original_render_log": ""
}

RENDER_REPORT_BASE_USEFUL_KEYS = ['tool', 'render_version', 'test_group', 'core_version', 'render_device']

SIMPLE_RENDER_TIMEOUT = 10
TIMEOUT_PAR = 3

PIX_DIFF_MAX = 15
PIX_DIFF_MAX_EC = 0
PIX_DIFF_TOLERANCE = 9
TIME_DIFF_TOLERANCE = {'10': float('inf'), '30': float('inf'), '60': float('inf'), '120': float('inf'), 'inf': float('inf')} # due to core instability
TIME_DIFF_MAX = 5
VRAM_DIFF_MAX = 5

"""
# Possible test case statuses
  passed - status means case was executed without errors and difference with baseline is permissible.
  skipped - status means case wasn't launched by QA team decision.
  error - status means fatal error during render, terminating by timeout, or case wasn't launched at all.
  failed - status means that pixel difference with baseline image is too large.
"""
TEST_SUCCESS_STATUS = 'passed'
TEST_IGNORE_STATUS = 'skipped'
TEST_CRASH_STATUS = 'error'
TEST_DIFF_STATUS = 'failed'

CASE_REPORT_SUFFIX = '_RPR.json'
TEST_REPORT_NAME = 'report.json'
TEST_REPORT_NAME_COMPARED = 'report_compare.json'
TEST_REPORT_EXPECTED_NAME = 'expected.json'
TEST_REPORT_HTML_NAME = 'result.html'

SESSION_REPORT = 'session_report.json'
SESSION_REPORT_HTML = 'session_report.html'

NOT_RENDERED_REPORT = "not_rendered.json"

THUMBNAIL_PREFIXES = ['thumb64_', 'thumb256_']

POSSIBLE_JSON_IMG_KEYS = ['baseline_color_path', 'render_color_path', 'original_color_path']
POSSIBLE_JSON_IMG_KEYS_THUMBNAIL = ['thumb64_' + x for x in POSSIBLE_JSON_IMG_KEYS]
POSSIBLE_JSON_IMG_KEYS_THUMBNAIL = POSSIBLE_JSON_IMG_KEYS_THUMBNAIL + ['thumb256_' + x for x in POSSIBLE_JSON_IMG_KEYS]
POSSIBLE_JSON_IMG_RENDERED_KEYS = ['render_color_path', 'original_color_path']
POSSIBLE_JSON_IMG_RENDERED_KEYS_THUMBNAIL = ['thumb64_' + x for x in POSSIBLE_JSON_IMG_RENDERED_KEYS]
POSSIBLE_JSON_IMG_RENDERED_KEYS_THUMBNAIL = POSSIBLE_JSON_IMG_RENDERED_KEYS_THUMBNAIL + ['thumb256_' + x for x in POSSIBLE_JSON_IMG_RENDERED_KEYS]

POSSIBLE_JSON_LOG_KEYS = ['original_render_log', 'rpr_render_log', 'conversion_log', 'render_log']
REPORT_FILES = POSSIBLE_JSON_IMG_KEYS + POSSIBLE_JSON_IMG_KEYS_THUMBNAIL + POSSIBLE_JSON_LOG_KEYS

IMG_KEYS_FOR_COMPARE = ['render_color_path']

POSSIBLE_JSON_IMG_BASELINE_KEYS = ['render_color_path', 'render_opacity_path']
POSSIBLE_JSON_IMG_BASELINE_KEYS_THUMBNAIL = ['thumb64_' + x for x in POSSIBLE_JSON_IMG_BASELINE_KEYS]
POSSIBLE_JSON_IMG_BASELINE_KEYS_THUMBNAIL = POSSIBLE_JSON_IMG_BASELINE_KEYS_THUMBNAIL + ['thumb256_' + x for x in POSSIBLE_JSON_IMG_BASELINE_KEYS]

BASELINE_MANIFEST = 'baseline_manifest.json'
BASELINE_SESSION_REPORT = 'session_baseline_report.json'
BASELINE_REPORT_NAME = 'render_copied_report.json'

SUMMARY_REPORT = 'summary_report.json'
SUMMARY_REPORT_EMBED_IMG = 'summary_report_embed_img.json'
SUMMARY_REPORT_HTML = 'summary_report.html'
SUMMARY_REPORT_HTML_EMBED_IMG = 'summary_report_embed_img.html'

PERFORMANCE_REPORT = 'performance_report.json'
PERFORMANCE_REPORT_HTML = 'performance_report.html'

COMPARE_REPORT = 'compare_report.json'
COMPARE_REPORT_HTML = 'compare_report.html'

REPORT_RESOURCES_PATH = 'resources'
REPORT_CONVERSION_LOG = 'conversion.log'
REPORT_RPR_LOG = 'renderTool.log'


TEST_CASES_JSON_NAME = {
        'blender': 'test_cases.json',
        'maya': 'test_cases.json',
        'max': 'case_list.json',
        'core': 'SceneList.json',
        'rprviewer': 'test.cases.json'
    }
LOST_TESTS_JSON_NAME = 'lost_tests.json'
RETRY_INFO_NAME = 'retry_info.json'

DONT_COMPARE = "Do not compare"

POSSIBLE_BASELINE_EXTENSIONS = ['jpg', 'png', 'gif', 'bmp']

SETUP_STEPS_RPR_PLUGIN = ["Prepare tests", "Open tool", "Load rpr", "Open scene", "Prerender", "Postrender", "Close tool", "Make report json", "Compare"]
