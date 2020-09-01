#!/bin/bash
RENDER_DEVICE=$1
FILE_FILTER=$2
TESTS_FILTER="$3"
RX=${4:-0}
RY=${5:-0}
SPU=${6:-25}
ITER=${7:-50}
THRESHOLD=${8:-0.05}
ENGINE=${9:-FULL}
TOOL=${10:-2.83}
python -m pip install -r ../jobs_launcher/install/requirements.txt

python ../jobs_launcher/executeTests.py --test_filter $TESTS_FILTER --file_filter $FILE_FILTER --tests_root ../jobs --work_root ../Work/Results --work_dir Blender28 --cmd_variables Tool "blender$TOOL" RenderDevice $RENDER_DEVICE ResPath "$CIS_TOOLS/../TestResources/Blender2.8Assets" PassLimit $ITER rx $RX ry $RY SPU $SPU threshold $THRESHOLD engine $ENGINE
