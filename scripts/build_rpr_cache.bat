set TOOL=%1
if not defined TOOL set TOOL="C:\Program Files\Side Effects Software\Houdini 18.5.351\bin\husk.exe"

%TOOL% "C:\TestResources\HoudiniAssets\Basic\basic_1\basic_1.usda" -R RPR -V 9 -o "..\Work\Results\Houdini\cache_building.jpg" --res 720 480