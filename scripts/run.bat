set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set FILE_FILTER=%1
set TESTS_FILTER="%2"
set RX=%3
set RY=%4
set UPDATE_REFS=%5
set TOOL=%6
set RETRIES=%7
set ASSETS=%8

if not defined FILE_FILTER set FILE_FILTER="Smoke.json"
if not defined RX set RX=0
if not defined RY set RY=0
if not defined UPDATE_REFS set UPDATE_REFS="No"
if not defined TOOL set TOOL="M:\RenderTools\Houdini 18.5.408\bin\husk.exe"
if not defined RETRIES set RETRIES=2
if not defined ASSETS set ASSETS="C:\TestResources\HoudiniAssets"

python -m pip install --user -r ../jobs_launcher/install/requirements.txt

python ..\jobs_launcher\executeTests.py --file_filter %FILE_FILTER% --test_filter %TESTS_FILTER% --tests_root ..\jobs ^
--work_root ..\Work\Results --work_dir Houdini --cmd_variables Tool %TOOL% rx %RX% ry %RY% ^
UpdateRefs %UPDATE_REFS% Retries %RETRIES% ResPath %ASSETS%