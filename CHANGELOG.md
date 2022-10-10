# DIME Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/) starting with version 0.0.1a1

## [1.1.3] - 2022-10-10
### Improvements
- redefined file io constants for source code clarity

### Bugfixes
- fixed a bug that caused errors in retrieving models due to an unexpected `reverse` argument

## [1.1.2] - 2022-10-09
### Improvements
- enabled `data_source_path` argument passing in `process queue`
- explanations UI improvements

### Bugfixes
- refined constant definitions
- fixed version inconsistency in the UI by fetching the version directly from the backend configurations
- fixed frontend doc url inconsistencies by defining them in the backend
- fixed api url inconsistencies by defining them in the backend 

## [1.1.1] - 2022-09-18
### Improvements
- removed custom dir and moved dime_diet_classifier to a dir called 'dime_components' in init dir list
- improved favicon support and the manifest
- UI Improvements

### Bugfixes
- removed redundant .env file loading
- turned off version check for config file

## [1.1.0] - 2022-08-11
### Improvements
- added Sinhala-English code-switching typing support

## [1.0.1] - 2022-08-11
### Bugfixes
- fixed process queue initialization exception on linux-based devices

## [1.0.0] - 2022-07-16
### Improvements
- optimized react js codebase for `DIME Server`
- renamed `process` to `process_queue` and added support to specify a specific `data_source_path` to preserve the process queue
- moved default in memory process queue to `dime_cache`

### Bugfixes
- fixed model count error after changing the active model path in `DIME Server`

## [0.0.4a14] - 2022-07-13
### Bugfixes
- fixed `dime init` bug where `.dime_cache` was not properly copied to the project directory

## [0.0.4a13] - 2022-07-13
### Improvements
- updated package dependencies to avoid conflicts with rasa dependencies

### Bugfixes
- dependency updates for `pandas` and `numpy` to resolve conflicts on Google Co-Lab
- extended DIME support for `Python 3.7` to enable DIME on Co-Lab notebooks
- updated `dime init` dir structure to include DIME-compatible `custom DIET classifier` component
- updated init dir instructions and readmes
- added an updated initial rasa model taken from rasa init trained using custom DIET classifier
- moved `.env` files from server root to project root
- added a dummy env file to the init project root

## [0.0.4a12] - 2022-07-12 (Unreleased)
### Features
- `DIME CLI` supports `quiet` mode which suppresses all logs and only outputs stdout and stderr for final outputs for the explanation generation process
- added full React support
- added `Download-able` DIME Explanations
- added `Upload` feature to the `DIME Server` which allows to upload previously generated dDIME explanation JSON files to the server
- added `Peak` feature to the `DIME Server` which allows to quickly visualize dime explanation files without having to upload it to the server
- DIME Server allows to manage both `models` and `explanations` available on the server, locally
- added a `In-Memory Process Queue` to allow users to `Abort` explanation generation requests made from the server
- added support for `Rasa 2.8.8` models
- added the ability to load `custom rasa pipeline components` while loading a model for explanation generation. (only available on local models)
- added `--quiet` flag to `dime init` which creates a new DIME project from scratch without prompting for user inputs for project location verification

### Improvements
- CLI-related docstrings were added for clarity based on the [Google Python Styleguide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- added the ability to track explanation generation requests sent from DIME server using a unique request ID attached to the process IDs. Aborting requests was not supported in previous versions

### Deprecations and Removals
- server cache was disabled and the behavior was assigned to process queue component of the DIME server
- removed React browser router and utilized hash router instead to avoid root route conflicts and routing loops
- `softmax` function and `exp_norm_softmax` functions are deprecated and will be removed in Rasa 2.0.0 onwards. `to_probability_series` can be utilized to convert feature importance score series to a probability series
- `Accuracy` and `F1-Score` are deprecated as metrics in DIME core. `Model Confidence` should be used as the default metric for all feature importance calculations

### Bugfixes
- fixed a JSON serialization error occurred while trying to parse numpy values given by the normalization, probability series calculation and feature selection methods
- `DIME sever` is now able to serve react frontends and static files, and able to redirect to the correct hash route when non hash routes are being called
- `DIME server` is able to correctly process subprocess stdout and stderr byes and figure out DIME exceptions while generating explanations
- DIME config validations were refined due to not being able to detect empty data instances specified in the DIME configuration file
- React logs were suppressed in production environments
- server-sent configuration validations were properly implemented