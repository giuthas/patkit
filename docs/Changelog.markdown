# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[//]: # (Possible headings in a release:)
[//]: # (Highlights for shiny new features.)
[//]: # (Added for new features.)
[//]: # (Changed for changes in existing functionality.)
[//]: # (Refactor when functionality does not change but moves.)
[//]: # (Documentation for updates to docs.)
[//]: # (Testing for updates to tests.)
[//]: # (Deprecated for soon-to-be removed features.)
[//]: # (Removed for now removed features.)
[//]: # (Bugs for any known issues, especially in use before 1.0.)
[//]: # (Fixed for any bug fixes.)
[//]: # (Security in case of vulnerabilities.)
[//]: # (New contributors for first contributions.)

[//]: # (And of course if a version needs to be YANKED:)
[//]: # (## [version number] [data] [YANKED])


## [Unreleased]

### Added

- 0.23.x will improve the annotation GUI by adding missing features like interval
  selection
- 0.24 will update configuration handling.
- 0.25 adds simple ways of opening different kinds of data
- After this we'll be at 1.0.0-alpha and 1.0.0-beta before release of 1.0.
  - There will be a feature freeze at this point.
  - The alpha and beta versions will be mainly quality assurance and code clean up.

## [0.22.2] - 2026-05-26

### Highlights

- Save formats for Answers.

### Added

- Save formats for Answers.

### Bugs

- [Old Bugs](Bugs.markdown).

### Fixed



## [0.22.1] - 2026-05-23

### Highlights

- Manifest files now work.
- Some corrections to documentation.
  - Links on PyPi will now hopefully work. 

### Added

- First automated unit tests and integration tests.

### Bugs

- [Old Bugs](Bugs.markdown).

### Fixed

- Manifest overwrite bug.
- Links on PyPi


## [0.22.0] - 2026-04-14

### Highlights

- New light mode colors for exercise mode.
- Bug fixes

### Bugs

- [Old Bugs](Bugs.markdown).

### Fixed

- Fixed use of a deprecated function in loading ultrasound data. 
- Light mode now works in exercise mode.
- Some corrections to documentation.
  - Links on PyPi will now hopefully work. 


## [0.21.0] - 2026-03-27

### Highlights

- PATKIT can now play the recorded sounds.

### Added

- Sound playback for 
  - whole file
  - from cursor to end
  - reset cursor to beginning with rewind button

### Bugs

- [Old Bugs](Bugs.markdown).

### Fixed

- README links and other content is now more up to date.


## [0.20.2] - 2026-03-04

### Fixed

- Symlink to current PATKIT screenshot should work again in various docs.


## [0.20.1] - 2026-03-04

### Highlights

- Clearer indicators for exercise mode vs regular edit/analysis mode.

### Added

- Status of Analysis vs Exercise mode and Answer vs Example mode is now
  displayed in the GUI as a dropdown and with colours.

### Changed

- Exercise mode is now separate from regular edit mode. 
  - Flipping between new answer being worked on and the example answer does not
    disable exercise mode.
  - Editing of example answer boudnaries in exercise mode is disabled.

### Bugs

- The mode colours (Analyse vs Exercise, Answer vs Example) only work well in
  dark mode as no light mode counterparts have been yet defined.
- [Old Bugs](Bugs.markdown).

### Fixed

- Some security issues were fixed by upgrading dependencies.


## [0.20.0] - 2026-02-24

### Highlights

- Cursor timestamp is now shown in the GUI.
- Curve values and clicked frequency in spectrogram highlighted in GUI.
- Roadmap to 1.0 has been updated above.

### Added

- Display of cursor timestamp next to the cursor.
- Brought 'previous' and 'next' buttons back.
- Meta addition: The 'Bugs' section below will now track all know bugs. This is
  subject to change if the practice proves too cumbersome.

### Bugs

Only new bugs will be listed here. Bugs found in previous versions that have
not yet been fixed are listed in [Bugs](Bugs.markdown). Fixed bugs will be
listed under Fixed as before.

### Fixed

- Moved back to `tight` layout due to issues in axes not lining up vertically
  with each other.
- Commandline history now works in the interactive interpreter mode, because
  somebody else fixed it in the libraries.


## [0.20.0-alpha.1] - 2026-02-12

### Highlights

- Fixing prerelease naming to conform with Semantic versioning.


### Fixed

- Fixing prerelease naming to conform with Semantic versioning.


## [0.19.0] - 2025-12-08

### Highlights

- New Intensity Modality for analysing image intensity.

### Added

- Basic version of Intensity Modality calculates intensity as sum of pixel
  values.

### Fixed

- Simulation had broken down with recent updates, but works again.
- Also some updates to reporting in simulation.


## [0.18.2] - 2025-08-08

### Highlights

- Documentation update for installation, running, hotkeys and such. No changes
  in code.


## [0.18.1] - 2025-08-07

### Highlights

- Switching between an exercise answer and the example answer in the GUI.

### Fixed

- When running as an exercise, after scrambling, saving the modified TextGrids
  no longer overwrites the example answer. Instead for this release saving
  TextGrids is disabled in exercise mode.


## [0.18.0] - 2025-06-19

### Highlights

- Automated segmentation exercises are now becoming part of PATKIT.
- As we are still in alpha, this is not the full final release. **Only**
  scrambling a TextGrid works at the moment.
  - There will be 0.18.x releases that add most of the rest of the
    functionality.
- Some bugs have been fixed.

### Added

- Configuration, commands, and shortcuts for treating a directory as an
  exercise.
- Audio only recordings.

### Bugs

- Saving TextGrids will overwrite the example answers to an exercise.

### Fixed 

- File -> Open... works again.
- Issue of hard coded time vector in GUI selection.
- Waveform is no longer plotted in black in dark mode.


## [0.17.1] - 2025-05-28

### Highlights

- Improved zooming and panning:
  - Panning works.
  - Zooming has better short cut conformity.
- New list view of recordings.

### Added

- Clickable list view of recordings.
- Documentation for keyboard shortcuts.
- New centering shortcut to center view at cursor.

### Changed

- Panning with keyboard shortcuts has been added.
- Zooming shortcuts work more consistently.
- Zooming centers on cursor if a cursor has been placed.

### Fixed

- Zoom commands no longer 'eat' the Ctrl+O for opening a directory. However,
  see the bug below.
- There is a minimal three recording example again.

### Bugs

- When PATKIT first starts up, to start zooming you need to click on the main
  figure - also outside the graph areas will do. This is due to focus being in
  the 'Go to recording' field. This might or might not be changed in the future.
- Zooming very far in makes the plotting behave strangely.
- Ctrl+O crashes PATKIT probably because the directory opening code pre-dates
  the new directory structure.


## [0.16.0] - 2025-05-26

### Highlights

- New configuration and data management model separates recorded and PATKIT
  data into different directories.

### Changed

- Configuration now happens with files that are always named the same. Opening
  a directory that contains the correct config files is equivalent to opening
  the files.
- Derived/saved data is stored in the same directory as the configuration files
  or in subdirectories.
- PATKIT files apart from `patkit_manifest.yaml` are no longer stored with
  recorded/external data.

### Removed

- The main config file has been removed.

### Bugs

- Exclusion lists are disabled until reimplementation in most likely version
  0.20. -- Updated: most likely in version 0.28.


## [0.15.2] - 2025-04-22

### Highlights

- Fixed changelog parsing.

### Fixed

- Only change is that changelog headers now all conform to Keep a Changelog and
  should parse correctly in automated release not generation.


## [0.15.1] - 2025-04-22

### Highlights

- A menu option for selecting if the mean image, the frame at selection cursor
  - raw or interpolated - gets displayed in the image panel.

### Added

- A menu option for selecting if the mean image, the frame at selection cursor
  - raw or interpolated - gets displayed in the image panel.

### Fixed

- Attempting to fix the GitHub automated release, which failed previously due to
  a parsing error.


## [0.15.0] 2025-04-21

### Highlights

- Re-implementation of the simulation code that was originally released for
  Ultrafest 2024.

### Added

- `patkit simulate` command for simulating different metrics on spline data. It
  uses the simulation_parameters.yaml file.

### Changed

- Release notes are going to be automatically populated from the Changelog for
  better readability.
- Planned release schedule has changed.

### Fixed

- GitHub actions should now run a bit smoother and not attempt to run in forks.
- Hopefully fixed an older error complaining that `\i` is not a valid escape
  sequence in `\infty`.


## [0.14.2] 2025-04-11

### Highlights

- PATKIT is available on pypi under the name patkit.
- Fixed the build and distribution / installation issue: PATKIT should now run
  on linux, mac, and windows.
- Alpha/beta/rc releases will be made on test-pypi for those interested in
  running bleeding edge versions.
  - Also, pre-releases now work on GitHub.

### Added

- Conditional import of readline or pyreadline3 so that the interpreter mode
  should work also on windows.

### Fixed 

- Installation problems resulting in an empty package that would not run.


## [0.14.1] 2025-02-18

### Added 

- Automated releases on testpypi, pypi and github. Testpypi will in the future
  be used for pre-releases (alpha, beta, release candidate/rc) and pypi for
  regular releases. 
- Technically the software is still in alpha status as a whole but will get
  occasional alpha/beta/rc releases of the 0.x releases.


## [0.14.0] 2025-01-31

### Highlights

- New name! This program and library are now called PATKIT for Phonetic Analysis
  ToolKIT.
- PyPi package will be available very shortly after release of 0.14.
- There's a new and shiny command line interface. With the new installation
  procedure, PATKIT can be run as any regular command line tool.
- There's a new installation procedure with uv. Fast, neat, gives us the
  previous easily.

### Added

- Dark/Light mode support. See bugs below, though.

### Changed and Refactored

- Moved the project directory to src layout. Updated pyproject.toml to reflect
  this. 
- Moved to installation with uv and updated pyproject.toml to work with
  this too. 
- Command line is now implemented with `click` rather than `argparse`.
  Neater look, easier maintenance and with the new installation also working
  command line tool with subcommands.
- PATKIT now uses PyQt6 instead of 5 for the GUI.

### Docs

- Docs are now again correctly generated.
- Some preliminary docs on configuration. Expect these to update in the next
  two-three releases.

### Deprecated

- One of the next updates - probably 0.16 - will move from centralised
  single config system to per-dataset config system.
- Another soon to happen change is the expansion of the classes derived from 
  DataAggregator. Recording will be split to Source and Trial, and DataSet added
  as a class that contains Sessions.
- There maybe references to the old name (SATKIT) in documentation and source
  code. These will be updated as they are found. Please let us know if you spot
  one.

### Bugs

- Switching the operating system between dark/light mode while the annotator is
  running may or may not update the plots, and may even break them. However,
  restarting the annotator will update the plots.
- Implementing the subcommand `patkit simulate` is still underway. Expected to
  be available in 0.15.
- Errors like these can show up at startup, but can be safely ignored:
```shell
/home/jpalo/.local/share/uv/tools/patkit/lib/python3.13/site-packages/patkit/annotations/peaks.py:293: SyntaxWarning: invalid escape sequence '\i'
  categories = ["l$\infty$" if metric ==
/home/jpalo/.local/share/uv/tools/patkit/lib/python3.13/site-packages/patkit/plot_and_publish/publish.py:188: SyntaxWarning: invalid escape sequence '\i'
  plot_categories = ["l$\infty$" if metric ==
```

## [0.13.0] 2025-01-07

### Highlights

- Production version of downsampling functionality based on paper published at
  ISSP 2024.

### Added

- Downsampling of derived modalities.
- Modality legend names and formatting from config.

### Bugs

- Docs are not necessarily fully generated due to some naming issues. This
  should be fixed in 0.14.
- SatPoint in SatGrid references the old config_dict global variable. This will
  make any calls to `SatPoint.contains` crash. This will be fixed in 0.14.
- Not specifying ylim in GUI configuration crashes. This has already been fixed
  in the branch that will become 0.14.

## [0.12.0] 2024-12-29

### Highlights

- Experimental interactive workflow. 
  - Supported by interface and data initialisation being collected into some
    simple-to-use functions.
  - Also supported by temporary script file `patkit_interactive.py`.
    - Runs like `patkit.py` but instead of starting the GUI annotator, starts an 
      interactive Python session.
- Exporting data from Modalities into DataFrames for external analysis.

### Added

- Exporting data from modalities into DataFrames for external analysis.
  - Includes an option of exporting with label info from TextGrids.
  - Experimentally enabled export of several derived modalities into the same csv
    file.
- A script to run PATKIT as an interactive interpreter. 
  - The same commands can obviously be copy-pasted into an interpreter to get some
    data loaded and processable in interactive mode.
- Some helpful progress indicators to show how the data loading is going.
- Y limits of modality axes and spectrograms can be controlled from the gui
  parameter file.

### Changed

- A lot of functionality that lived in `patkit.py` is now in regular patkit
  library functions and in the new `patkit/patkit.py` module.
- Undefined fields are no longer allowed in config files.

### Removed

- Dismantled the `scripting_interface` submodule.

### Fixed

- Saving and loading works again.

### Bugs

- Same as previous versions.
- Command history does not yet work when running PATKIT as an interactive
  interpreter with `patkit_interactive.py`.
- Undefined fields in config files should have a clearer error message. And so
  should errors in config files in general.


## [0.11.0] 2024-11-20

### Added

- Simulating ultrasound probe rotation (misalignment) by selecting different
  sub-sectors from recorded raw data.
- DistanceMatrices can now be sorted by a list of substrings into or simply by 
  prompt.
  - DistanceMatrices can also specify their own exclusion list in the config.
- Saving the selected frame with metadata so that example frames can be 
  reproduced.
- Saving AggregateImages, DistanceMatrices and the main figure (of the GUI) 
  with metadata.
- Expanded SatGrid (the editable TextGrid extension) to include Points and Point
  Tiers.
- Automatic x limits now work properly in the GUI.

### Bugs

- Displaying exclusion is not quite working with the new feature of exclusion
  working both globally and per metric. This leads to some warnings when trying to
  plot modalities that didn't get calculated. Will be fixed in the future as the
  configuration system gets a makeover.
- When data run config and exclusion are at odds (especially sort) there should
  be an informative message to the user. This too will get better when the
  configuration system gets a makeover.

## [0.10.1] 2024-10-18

### Added

- Added some docstring documentation.

### Fixed

- Removed some tracing that was left from debugging.

## [0.10.0] 2024-10-18

### Highlights

- Diagnosing ultrasound probe alignment is now possible by generating a
  DistanceMatrix of a Session with the metric `mean_squared_error`.

### Added

- Statistic is a new kind of derived data class. It is meant as the base class
  for data that is not time-dependent.
- There are now new abstract base classes that Session, Recording, Statistic, and
  Modality derive from. These are meant for gathering common functionality of the
  four main classes together rather than direct inheritance.
- AggregateImage is a new Statistic and its current only implementation is the
  metric 'mean', which is used to calculate mean images.
- Mean Images are used as the basis of calculating another Statistic: 

### Deprecated

- patkit.py will eventually be removed when running PATKIT will be moved to
  access points. This means PATKIT -- when correctly installed -- will run with
  from the command line with: `patkit [command] [arguments]`.

### Fixed

- AAA ultrasound importer now reads dates both in `%d/%m/%Y %H:%M:%S` and
  `%Y-%m-%d %I:%M:%S %p`.
- Parsing yaml exclusion lists should now work also when some of the headings
  are empty.
- Added the seaborn package to conda environment patkit-devel to make it work
  properly.

### Known issues

- Saving and loading are currently not functional. While saving seems to work,
  since new data structures like FileInformation etc. are not saved at all, the
  saved files will be unloadable.

## [0.9.0]

- Simulated data and sensitivity analysis for metrics
  - Two contours for running sensitivity simulations for contour metrics.
  - Perturbation generation for the contours.
  - Functions for running metrics on the simulated data.
  - Lots of plotting routines to look at the results.
  
### Known issues:

- Same as in 0.8.0 plus
- Some perturbation related plotting functions have hard-coded subplot
  divisions because Comparison is not yet sortable.

## [0.8.0]

- Splines
  - Spline loading from AAA export files.
  - Several spline metrics now work and can be displayed.
  - Splines can be displayed on the ultrasound frame.
- Some updates to clean the code in general.

### Known issues:

- Same as in 0.7.0 plus
- Synchronising spline metrics and splines with ultrasound is currently
  unreliable. This is because the timestamps in spline files have proven to
  have either drift or just inaccuracies and testing why this is so is a job
  for the future. This may eventually be solved just by matching splines with
  ultrasound frames and reporting when that becomes too unreliable.

## [0.7.0]

- Saving and loading to/from native formats for derived Modalities.
  - Saved data can be loaded on startup or opened afterwards. This means
    derived Modalities don't need to be re-generated every time and switching
    between recording sessions is fast.
  - Metadata of derived Modalities is now saved in human-readable form while
    the numeric data is saved in numpy native formats.
  - Database is also saved in human-readable formats for easy checking of data
    integrity.
  - Opening (ctrl+'o') and saving (ctrl+shift+'s') work in the GUI. Overwrites
    are verified when saving, but the logic of that part may change before 1.0.
    The most obvious alternative to approving overwrites on a file-by-file
    basis alongside the 'Yes to all' option, is to only have the latter.
- Zooming in, out and to all now works with 'i', 'o' and 'a' respectively.

### Known issues:

- ctrl+'i' and ctrl+'a' zoom but ctrl+'o' is bound to opening a recording
  session. The fix will be removing the first two bindings which are
  unintentional.
