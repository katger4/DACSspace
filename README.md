# DACSspace

A simple Python script to evaluate your ArchivesSpace instance for DACS [single-level minimum](http://www2.archivists.org/standards/DACS/part_I/chapter_1) required elements, as well as required elements based on the [Orbis Cascade Alliance's EAD Best Practices](https://www.orbiscascade.org/archivesspace-usage-manual-resource-records) (Version 3.8.1). 

DACSspace utilizes the ArchivesSpace API to check resources for DACS compliance and produces a csv containing a list of evaluated resources. If a DACS field is present its content will be written to the csv, if a field is missing the csv will read "FALSE" for that item.

## Requirements

*   Python (written for and tested on 2.7).
*   ConfigParser
*   Requests module

## Installation

Download [Python](https://www.python.org/downloads/)

If you are using Windows, add Python to your [PATH variable](https://docs.python.org/2/using/windows.html)

Install requirements ([ConfigParser instructions](https://docs.python.org/2/library/configparser.html) /  [Requests instructions](http://docs.python-requests.org/en/master/user/install/))

## Setup

Run `setup.py` to create a configuration file named `local_settings.cfg` which will allow you to connect to your ArchivesSpace instance. You will need:
* BaseURL of your ArchivesSpace instance
* Repository ID for your ArchivesSpace installation
* ArchivesSpace username and password

Your configuration file will look something like this:
```
[ArchivesSpace]
baseURL: #BaseURL of your ArchivesSpace instance
repository: #Repository ID of your ArchivesSpace installation
user: #ArchivesSpace username
password: #ArchivesSpace password for the username used above

[Destinations]
directory: #Directory where you would like to save the csv file
filename: dacs_singlelevel_report.csv
```

## Usage

Using the command line navigate to the directory containing the DACSspace repository and run `single-level.py` to execute the script.

DACSspace will prompt you to answer two questions allowing you to limit which resources you'd like the script to evaluate:

```
Welcome to DACSspace!
I'll ask you a series of questions to refine how to script works.
If you want to use the default value for a question press the ENTER key.

Do you want DACSspace to include unpublished resources? y/n (default is n):
Do you want to further limit the script by a specific resource id? If so, enter a string that must be present in the resource id (enter to skip):
```

Pressing the ENTER key for both questions will use the default version of the script which will get ALL resources.

The script will create a list of evaluated resources in a csv file (default is `dacs_singlelevel_report.csv`).

A sample csv file will look like this:

| title | publish | resource | level | extent | date| language | repository | creation_date | creator | aw_subjects | abstract | bioghist | scope | restrictions | ead_id | ead_location | finding_aid_title | finding_aid_author | finding_aid_date | finding_aid_description_rules | finding_aid_filing_title | finding_aid_language
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| #resource title | TRUE | #resourceId | collection | 20.8 | creation|  eng   | #NameofRepository | 2008 | FALSE | #subjects | #abstract | #bioghistnote | #scopenote | #accessrestriction
| #resource title | TRUE | #resourceId | collection | 50.6 | FALSE   |  FALSE | #NameofRepository | 2012 | #creator | FALSE | FALSE | FALSE | FALSE | FALSE

If you are using Microsoft Excel to view the csv file, consult the following links to avoid encoding issues: [Excel 2007](https://www.itg.ias.edu/content/how-import-csv-file-uses-utf-8-character-encoding-0), [Excel 2013](https://www.itg.ias.edu/node/985).

## Authors

Hillel Arnold and Amy Berish

## License

This code is released under the MIT license. See `LICENSE` for further details.