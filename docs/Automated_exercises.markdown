# Automated exercises

## Alignment exercises

TODO: description of how to create exercises, share them, and answer them. 

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
└── exercise/            <-- Exercise data
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

Currently, a Patkit Scenario will support only one Exercise, but each Exercise
may have multiple answers each consisting of multiple TextGrids. If you want to
create different Exercises based on the same data, then you should copy the
Session directory in its entirety, delete the possibly existing exercise
directory from it, and after opening the session in Patkit, run New Exercise.