# Automated exercises

Exercises in Patkit are managed within a [Session
directory](DataManagement.markdown), which serves as the base Scenario.

## Annotator modes

The Annotator has two modes - Analyse and Exercise - and the Exercise mode is
split into tow submodes: Answer and Example.

In Exercise mode, Patkit isolates the Answer TextGrids to protect the primary
reference data. In the current implementation (v0.22.2). The Session's
TextGrids are copied into a immutable example set when an exercise is created.
The original TextGrids remain editable in Analyse mode, but editing them will
not update the example TextGrids after creating an Exercise.

## Creating Exercises

Converting a Session into an Exercise Patkit will automatically generate an
`exercise` folder containing the exercise metadata file
(`exercise_metadata.yaml`) and an `answers` folder with one new answer (see
[Directory Structure](Automated_exercises.markdown#directory-structure) below
for more detail).

1. Open your session in Patkit and in the **Exercise** menu select **New
   Exercise**.
2. A setup dialog will prompt you to select a scrambling method (at the moment
   only option is `Equidistant`) to scramble the alignment boundaries. 
3. Creating a new exercise immediately opens a dialogue window for a **"New
   Answer"**. You must provide an answer name to proceed. Cancelling
   this subsequent answer dialog aborts the exercise creation process.
4. Upon successful creation, Patkit automatically saves the exercise parameters
   to disk and shifts the main application window from **Analyse** mode into
   **Exercise** mode.

### Handling Multiple Exercises 

Patkit Scenarios/Sessions can only support a single Exercise at a time. To
create a different exercise variant using the same source data, duplicate the
entire Session directory, delete the existing `exercise/` folder within that
copy, open the cloned session in Patkit, and run the "New Exercise" process
fresh.


## Answering and Managing Exercises

**Creating a new answer:** In the **Exercise** menu select **New answer...**.
This opens a dialog prompting for a name for the answer and an optional Author
Name. On pressing 'OK' Patkit will open the new Answer in the GUI.

**Saving Progress:** Save Answer writes the current answer's TextGrids into the
`answers` directory. 

**Resuming an Assignment:** Open the Session in Patkit and in the **Exercise**
menu select **Open answer...**. This shows a dialog window with dropdown menu
to select an Answer to open.

**Reviewing Examples:** Toggle **Show example** in the **Exercise** menu or
change the exercise dropdown selector from **Answer** to **Example** - also via
the shortcut Alt+E. This swaps the display to the example answer and vice
versa.


## Sharing Exercises

Sharing exercises is currently (v0.22.2) a somewhat manual process. However,
the next release (v0.22.3) will include an automated way of bundling an
Exercise for sharing.


## Directory Structure

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


