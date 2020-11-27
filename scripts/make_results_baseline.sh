#!/bin/bash
DELETE_BASELINES=${1:False}

python ../jobs_launcher/common/scripts/generate_baselines.py --results_root ../Work/Results/Houdini --baseline_root ../Work/GeneratedBaselines --remove_old $DELETE_BASELINES
