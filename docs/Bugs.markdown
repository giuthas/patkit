# Bugs

## Running PATKIT
- Errors like these can show up at startup, but can be safely ignored:
```shell
/home/jpalo/.local/share/uv/tools/patkit/lib/python3.13/site-packages/patkit/annotations/peaks.py:293: SyntaxWarning: invalid escape sequence '\i'
  categories = ["l$\infty$" if metric ==
/home/jpalo/.local/share/uv/tools/patkit/lib/python3.13/site-packages/patkit/plot_and_publish/publish.py:188: SyntaxWarning: invalid escape sequence '\i'
  plot_categories = ["l$\infty$" if metric ==
```
  They are related to labelling curves with maths symbols rendered with LaTeX.
- Exclusion lists are disabled until reimplementation in 0.24.

## Configuration
- Undefined fields in config files should have a clearer error message. And so
  should errors in config files in general.
- Displaying exclusion is not quite working with the new feature of exclusion
  working both globally and per metric. This leads to some warnings when trying to
  plot modalities that didn't get calculated. Will be fixed in the future as the
  configuration system gets a makeover.
- When data run config and exclusion are at odds (especially sort) there should
  be an informative message to the user. This too will get better when the
  configuration system gets a makeover.

## GUI Graphs
- When PATKIT first starts up, to start zooming you need to click on the main
  figure - also outside the graph areas will do. This is due to focus being in
  the 'Go to recording' field. This might or might not be changed in the future.
- Zooming very far in makes the plotting behave strangely.
- Switching the operating system between dark/light mode while the annotator is
  running may or may not update the plots, and may even break them. However,
  restarting the annotator will update the plots.
- Synchronising spline metrics and splines with ultrasound is currently
  unreliable. This is because the timestamps in spline files have proven to
  have either drift or just inaccuracies and testing why this is so is a job
  for the future. This may eventually be solved just by matching splines with
  ultrasound frames and reporting when that becomes too unreliable.

## GUI commands
- Saving TextGrids will overwrite the example answers to an exercise.
- Ctrl+O does not update the GUI setup correctly because it does not read or
  apply the config correctly.
- ctrl+'i' and ctrl+'a' zoom but ctrl+'o' is bound to opening a recording
  session. The fix will be removing the first two bindings which are
  unintentional.

## Cursors
- After playing a recording the plot cursors may take some time to function
  properly again.

## Misc
- Some perturbation related plotting functions have hard-coded subplot
  divisions because Comparison is not yet sortable.
