# Autotests for Radeon ProRender Houdini plugin

## Install
 1. Clone this repo
 2. Get `jobs_launcher` as git submodule, using next commands

    ```
    git submodule init
    git submodule update
    ```

 3. Put folders with scenes in `C:/TestResources/HoudiniAssets` and baselines in `C:/TestResources/HoudiniReferences`.
 
    ***You should use the specific scenes which defined in `test_cases.json` files in `jobs/Tests/` folders.***

 4. Run `run.bat` on Windows or `run.sh` on Unix-based only from `scripts` folder with customised arguments with space separator:

    | NUMBER | NAME         | DEFINES                                                                              | DEFAULT                                                                |
    |--------|--------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------|
    | 1      | FILE_FILTER  | Path to json-file with groups of test to execute                                     | "Full.json"                                                            |
    | 2      | TESTS_FILTER | Paths to certain tests from `..\Tests`. If `FILE_FILTER` is set, you can write `""`. | ""                                                                     |
    | 3      | RX           | Width of outputted images.                                                           | 0                                                                      |
    | 4      | RY           | Height of outputted images.                                                          | 0                                                                      |
    | 5      | PASS_LIMIT   | Extra iterations of repeats tests execution.                                         | 0 (that means, each test will be executed once)                         |
    | 6      | UPDATE_REFS  | Should script update references images on each iteration.                            | "No"                                                                   |
    | 7      | TOOL         | Path to executable file of render utility.                                           | "C:\Program Files\Side Effects Software\Houdini 18.5.351\bin\husk.exe" |
    | 8      | ASSETS       | Path to houdini scenes.                                                              | "C:\TestResources\HoudiniAssets"                                       |
    | 9      | RETRIES      | The number of attempts to launch the case.                                           | 2                                                                      |

    Example:
    > run.bat Full.json

    ***ATTENTION!***

    **The order of the arguments is important. You cannot skip arguments.**

    **On Windows better to run via `CMD`. If you run through `PS`, empty arguments (like this "") may be ignored.**