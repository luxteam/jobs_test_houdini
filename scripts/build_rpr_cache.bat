set TOOL=%1
if not defined TOOL set TOOL="C:\Program Files\Side Effects Software\Houdini 18.5.351\bin\husk.exe"

mkdir ..\Work\Results\Houdini

%TOOL% "C:\TestResources\rpr_usdplugin_autotests_assets\build_cache\build_cache.usda" -R RPR -V 9 -o "..\Work\Results\Houdini\cache_building.jpg" --res 720 480