# GDC Data Dictionary in JSON

The json files are downloaded from the backend of GDC data dictionary viewer. The files
are timestamped by the date that it was downloaded. 

The URL for the file is https://api.gdc.cancer.gov/v0/submission/_dictionary/_all

The current.json file is a symlink to the most current version. 

The command to download a current version and update the symlinked current.json is:

```shell
# run it in the project root path
python -m ccdh.importers.gdc
```

