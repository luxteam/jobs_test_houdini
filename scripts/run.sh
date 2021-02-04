#!/bin/bash
FILE_FILTER=${1:-"Full.json"}
TESTS_FILTER="$2"
RX=${3:-0}
RY=${4:-0}
UPDATE_REFS=${5:-"No"}
TOOL=$6
RETRIES=${7:-2}
ASSETS=${8:-"$CIS_TOOLS/../TestResources/rpr_usdplugin_autotests"}

python3 -m pip install --user -r ../jobs_launcher/install/requirements.txt

python3 ../jobs_launcher/executeTests.py --file_filter $FILE_FILTER --test_filter $TESTS_FILTER --tests_root \
../jobs --work_root ../Work/Results --work_dir Houdini --cmd_variables Tool $TOOL  \
rx $RX ry $RY UpdateRefs $UPDATE_REFS Retries $RETRIES ResPath $ASSETS