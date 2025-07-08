# Introduction

The `deploy.py` script is used to publish Jupyter notebooks into the "Custom Reports"
panel on the "Custom Queries" page. It works by processing one or more Jupyter
notebooks into an HTML document, a thumbnail image and report information that 
is used to populate the version, title and summary information in the Custom Reports
interface.

# Software Dependencies

The conversion tool needs the various Jupyter notebook libraries. Easiest way 
to get these is to install anaconda python. 

Also need to add playwright and pillow for the thumbnail image generation.

```
conda install conda-forge::playwright
conda install conda-forge::pillow
```

# Usage

First create an output directory (e.g. export) then run the deploy
script specifying the output directory and the notebooks to process. Only
notebooks that contain the special "METADATA" code cell will be
processed. See the "Notebook setup" section below of details of the report
setup.

```
python3 deploy.py -o /path/to/export /path/to/notebooks/*.ipynb
```

The contents of the export directory will then contain a json file
with teh report metadata for all processed reports, and then an html file
and png file for each report. These files should be copied to the directory
that is configured on the XDMoD webserver for reading the custom reports
i.e. the `base_path` config setting in the `custom_reports` section
of `portal_settings.d/xsede.ini`

```ini
[custom_reports]
base_path = '/scratch/xdmod/custom_daf_reports'
```

# Notebook setup

The python notebooks for report generation must have a code cell that contains
report metadata in the following form:

```python
METADATA = {
    'title': 'Report Title goes here',
    'version': 9,
    'description': 'One or two sentence summary of report goes here.',
    'history': [
        [ '1', '2024-09-18', 'Initial Version.'],
        [ '2', '2024-10-18', 'Added teleportation capability.'],
        ...
        [ '9', '2024-10-18', 'Decombobulated the cromptifier']
    ]
}
```

You can also optionally add an html anchor for the location of the page that
should be used to generate the report thumbnail. (Typically chart images look
better than text walls in the thumbnails). If no anchor is added then the top
of the report will be used.

```python
# add anchor so the thumbnail generator goes here
display(HTML('<a name="thumbnail"></a>'))
```
