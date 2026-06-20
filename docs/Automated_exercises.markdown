# Automated exercises

## Alignment exercises

In version 0.18.0 there is just one working command in the Exercise menu: `Run
as exercise`. Clicking on it will 'scramble' the TextGrids in the currently open
Session. This means that the boundaries get redistributed equidistantly from
each other within the recordings. 

After that you can practice aligning the boundaries to which ever data modalities are open. 

**Please note**, that in 0.18.0, saving the TextGrids **overwrites** the originals.
This planned to be changed in 0.18.1 to protect the example answer.

There will be further commands enabled in versions 0.18.1 onwards to enable
saving and other functionality. See the
[Changelog's](Changelog.markdown#unreleased) Unreleased section for further
details.

### Directory structure

Below is a simple example of how Exercise and Answer files are saved when the
Exercise is based on a Patkit Scenario that has all its files in the same
directory. 

``` plain text
session_dir/
├── patkit_manifest.yaml
├── patkit_data.yaml
├── patkit_gui.yaml
├── trial_1.wav
├── trial_1.TextGrid          <-- Original textgrid (Editable as usual)
└── exercise_name/            <-- Exercise data
    ├── exercise_metadata.yaml  <-- Stores "scrambling method: equidistant", time created, etc.
    ├── example/                <-- The generated example/scrambled exercise
    │   └── trial_1.TextGrid    <-- Example is treated as immutable once the exercise has been created.
    └── answers/
        ├── answer_1/           <-- Matches the answer name (spaces replaced by underscores)
        │   ├── answer_metadata.yaml  <-- Stores user name, answer name, created/edited times
        │   └── trial_1.TextGrid      <-- User's current working copy/answer
        └── answer_2/
            ├── answer_metadata.yaml
            └── trial_1.TextGrid
```
