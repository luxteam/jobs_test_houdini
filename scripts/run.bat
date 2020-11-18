set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set FILE_FILTER=%1
set TESTS_FILTER="%2"
set RX=%3
set RY=%4
set PASS_LIMIT=%5
set UPDATE_REFS=%6
set TOOL=%7
set ASSETS=%8

if not defined FILE_FILTER set FILE_FILTER="Full.json"
if not defined RX set RX=16
if not defined RY set RY=9
if not defined PASS_LIMIT set PASS_LIMIT=0
if not defined UPDATE_REFS set UPDATE_REFS="No"
if not defined TOOL set TOOL="C:\Program Files\Side Effects Software\Houdini 18.5.351\bin\husk.exe"
if not defined ASSETS set ASSETS="C:\TestResources\HoudiniAssets"
if not defined THRESHOLD set THRESHOLD=0.05

python -m pip install --user -r ../jobs_launcher/install/requirements.txt
python -m pip install --user -r husk_requirements.txt

python ..\jobs_launcher\executeTests.py --file_filter %FILE_FILTER% --test_filter %TESTS_FILTER% --tests_root ..\jobs ^
--work_root ..\Work\Results --work_dir Houdini --cmd_variables Tool %TOOL% ResPath %ASSETS% PassLimit %PASS_LIMIT% ^
rx %RX% ry %RY% UpdateRefs %UPDATE_REFS%