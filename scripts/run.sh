#!/bin/bash
FILE_FILTER=${1:-"Full.json"}
TESTS_FILTER="$2"
RX=${3:-"0"}
RY=${4:-"0"}
PASS_LIMIT=${5:-0}
UPDATE_REFS=${6:-"No"}
TOOL=$7
ASSETS=${8:-"$CIS_TOOL/../TestResources/HoudiniAssets"}

python -m pip install --user -r ../jobs_launcher/install/requirements.txt

python ../jobs_launcher/executeTests.py --file_filter $FILE_FILTER --test_filter $TESTS_FILTER --tests_root \
../jobs --work_root ../Work/Results --work_dir Houdini --cmd_variables Tool $TOOL RenderDevice gpu ResPath $ASSETS \
PassLimit $PASS_LIMIT rx $RX ry $RY UpdateRefs $UPDATE_REFS