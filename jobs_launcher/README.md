# Jobs launcher
[![Version](https://img.shields.io/github/v/tag/luxteam/jobs_launcher?label=Version&style=flat-square)](https://github.com/luxteam/jobs_launcher/releases)

## local config
Currently, switch between `master.ct` `master.ec` `master` reports has produced by `local_config.py` file in root dir.  
Required content - definition of:
* tool_name
* report_type

_Example_
```python3
tool_name = 'maya'
report_type = 'default'
```

## Third party libraries:
- [:octocat: Bootstrap](https://github.com/twbs/bootstrap)
- [:octocat: jQuery](https://github.com/jquery/jquery)
- [:octocat: Bootstrap tables](https://github.com/wenzhixin/bootstrap-table)
- [:octocat: Pixelmatch](https://github.com/mapbox/pixelmatch)


## What to test when upgrading a version

- [Blender](https://github.com/luxteam/jobs_test_blender) : Regression group and any few test groups   
- [Maya](https://github.com/luxteam/jobs_test_maya) : Regression group and any few test groups   
- [Max](https://github.com/luxteam/jobs_test_max) : Regression group and any few test groups   
- [RPRViewer](https://github.com/luxteam/jobs_test_rprviewer) : Scene_tests test group   
- [Core](https://github.com/luxteam/jobs_test_core) : Full 
- Conversion tools : Any conversion tool job with any few test groups   
- Northstar jobs : Fill in later
