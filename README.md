# PATKIT - Phonetic Analysis ToolKIT 

![PATKIT GUI](docs/PATKIT_UI.png)

PATKIT provides tools for phonetic analysis of speech data. It includes a GUI
for manual assessment/analysis/annotation (see picture above), command line
tools for batch processing, and an API for programming your own tools.

While currently PATKIT's tools mainly work on tongue and larynx ultrasound as
well as audio, in the future, the toolkit will include facilities for processing
other kinds of articulatory data. The first two tools to be implemented are
Optical Flow and Pixel Difference.

Optical Flow tracks local changes in ultrasound frames and estimates
the flow field based on these.

Pixel Difference and Scanline Based Pixel Difference -- work on raw,
uninterpolated data and produce measures of change over the course of a
recording. How they work is explained in Chapter 3 of Pertti Palo's [PhD
thesis](https://eresearch.qmu.ac.uk/handle/20.500.12289/10163).

## Getting PATKIT

[Detailed instructions](docs/Installing_and_using.markdown).

### Quick start guide: 

Check that [PyPi](https://pypi.org/search/?q=patkit) finds patkit and if it
does:
- Install [uv](https://docs.astral.sh/uv/#getting-started).
- On the commandline run `uv tool install patkit`.
- Run `patkit --help` for instructions.
- If you want to run the example data, get the `recorded_data` folder from
  [github](https://github.com/giuthas/patkit).
  - Run `patkit recorded_data/minimal` in the folder where you downloaded the data
    and experiment from there.

## Current version and development plans

See [Changelog](docs/Changelog.markdown), for what's new in the current version
and what's coming up.


## What's included

TODO 0.15: give a quick description of included data and goodies here.
TODO 1.0: Move the data elsewhere to be optionally loaded.

## Contributing

Please get in touch with [Pertti](https://taurlin.org), if you would like to
contribute to the project. All help is welcome regardless of your skill level.
You can contribute by trying to use it according to instructions and reporting
back when they lead you astray, proofreading docs, commenting code, testing
PATKIT on a new platform, writing new functionality, writing tests for the code,
roasting the code, doing UI design, contributing use cases...

## Versioning

We use [SemVer](http://semver.org/) for versioning under the rules as
set out by [PEP 440](https://www.python.org/dev/peps/pep-0440/) with
the additional understanding that releases before 1.0 (i.e. current
releases at time of writing) have not been tested in any way.

For the versions available, see the [tags on this
repository](https://github.com/giuthas/patkit/tags).

## Authors

* **Pertti Palo** - *The core of PATKIT* - [giuthas](https://github.com/giuthas)
* **Scott Moisik** - *Optic flow* - [ScottMoisik](https://github.com/ScottMoisik)
* **Matthew Faytak** - *Dimensionality reduction with PCA and LDA*
  [mfaytak](https://github.com/mfaytak)
* **Motoki Saito** - *Producing interpolated ultrasound images from raw data*
  [msaito8623](https://github.com/msaito8623)

List of [contributors](https://github.com/your/project/CONTRIBUTORS.markdown)
will be updated once there are more people working on this project.

## Copyright and License

The Phonetic Analysis ToolKIT (PATKIT or patkit for short) and examples is a
tool box for analysing phonetic data.

PATKIT Copyright (C) 2019-2025 Pertti Palo, Scott Moisik, Matthew
Faytak and Motoki Saito.

Optical Flow tools Copyright (C) 2020-2025 Scott Moisik

Pixel Difference tools Copyright (C) 2019-2025 Pertti Palo

Laryngeal example data Copyright (C) 2020 Scott Moisik

Tongue and tongue spline example data Copyright (C) 2013-2020 Pertti Palo

### Program license

PATKIT is licensed under [GPL
3.0](https://github.com/giuthas/patkit/blob/master/LICENSE.markdown).

This program (see below for data) is free software: you can
redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see
<https://www.gnu.org/licenses/gpl-3.0.en.html>

### Data license

[Data
License](https://github.com/giuthas/patkit/blob/master/DATA_LICENSE_by-nc-sa.markdown)

The data in directories `larynx_data`, `tongue_data_1`,
`tongue_data_1_2`, and `tongue_data_2` are licensed under the Creative
Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC
BY-NC-SA 4.0) License. See link above or
<https://creativecommons.org/licenses/by-nc-sa/4.0/> for details.

### Citing the code

When using any part of PATKIT, please cite:

1. Palo, P., Moisik, S. R., and Faytak, M. (2023). “Analysing Speech Data with
SATKIT”. In: International Conference of Phonetic Sciences (ICPhS 2023).
Prague.
2. Faytak, M., Moisik, S. & Palo, P. (2020): The Speech Articulation Toolkit
(SATKit): Ultrasound image analysis in Python. In ISSP 2020, Online (planned as
Providence, Rhode Island)

When making use of the Optic Flow code, please cite:

1. Esling, J. H., & Moisik, S. R. (2012). Laryngeal aperture in
relation to larynx height change: An analysis using simultaneous
laryngoscopy and laryngeal ultrasound. In D. Gibbon, D. Hirst, &
N. Campbell (Eds.), Rhythm, melody and harmony in speech: Studies in
honour of Wiktor Jassem: Vol. 14/15 (pp. 117–127). Polskie Towarzystwo
Fonetyczne.
2. Moisik, S. R., Lin, H., & Esling, J. H. (2014). A study of
laryngeal gestures in Mandarin citation tones using simultaneous
laryngoscopy and laryngeal ultrasound (SLLUS). Journal of the
International Phonetic Association, 44(01),
21–58. <https://doi.org/10.1017/S0025100313000327>
3. Poh, D. P. Z., & Moisik, S. R. (2019). An acoustic and
articulatory investigation of citation tones in Singaporean Mandarin
using laryngeal ultrasound. In S. Calhoun, P. Escudero, M. Tabain, &
P. Warren (Eds.), Proceedings of the 19th International Congress of
the Phonetic Sciences.

When using the Pixel Difference (PD) code, please cite:

1. Pertti Palo (2019). Measuring Pre-Speech Articulation. PhD
thesis. Queen Margaret University, Scotland, UK. Available here [PhD
thesis](https://eresearch.qmu.ac.uk/handle/20.500.12289/10163).

## Acknowledgments

* Inspiration for PD was drawn from previous projects using Euclidean
  distance to measure change in articulatory speech data. For
  references, see Pertti Palo's [PhD
  thesis](https://eresearch.qmu.ac.uk/handle/20.500.12289/10163).

* The project uses a nifty python tool called
  [licenseheaders](https://github.com/johann-petrak/licenseheaders) by
  Johann Petrak and contributors to add and update license headers for
  python files.
