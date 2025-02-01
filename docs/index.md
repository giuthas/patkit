
# PATKIT Documentation

Until the 1.0 release none of the documentation is final nor necessarily
correct.

## Installation and use

- New [instructions](Installing_and_using.markdown).
- Setting PATKIT up for analysis is currently covered by setting up for
  development:
- [Set PATKIT up for development](SetupForDevelopment.markdown)

## GUI User guide

[To be written.]

## Commandline User guide

[To be written] but already available in a rudimentary form by running
`patkit --help`

## PATKIT Runtime data structures

PATKIT's class structure aims for efficiency without sacrificing clarity.
Clarity of code brings easy maintainability and that is more important in the
long run than gains in execution speed.

- Introduction to PATKIT Data Structures
  - [Core Data Structures](CoreDataStructures.markdown)
  - [Modalities for Recorded Data](ModalitiesforRecordedData.markdown)
  - [Modalities for Derived Data](ModalitiesforDerivedData.markdown)
  - [Modalities in Practice](ModalitiesinPractice.markdown) including notes on
    specific Modalities
    - [Splines in PATKIT](Splines.markdown)
  - [Database Classes](DatabaseClasses.markdown)
- Extending PATKIT
  - Before starting, please read Coding conventions in [PATKIT development
    guide](Development_guide).
  - Implementing a New Datasource
  - [Writing a New Modality](WritingNewModality.markdown)

## PATKIT API

[API Documentation](api/index.html)

## PATKIT Files

- Data files
  - [Guidelines for Data Directory Structure](DirectoryStructure.markdown)
  - Importing and Exporting
  - [Saving and Loading](Saving_and_loading.markdown)
- [Configuration files](Configuration.markdown)
  - Command history
  - Global configuration
    - General parameters
    - GUI parameters
    - Data processing parameters
  - Local configuration
