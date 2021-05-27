# CCDH Terminology Service 

The CCDH terminology service is a RESTful API that supports the validation, lookup, binding, and mapping of the concepts 
in the CCDH data harmonization process and the transformation and validation workflow.  

## Terminology Service Rest API

The rest api provide endpoints for retreiving the data dictionaries from CRDC nodes, 
and the CRDC-H model. It is based on the ISO/IEC-11179-3, matadata registry metamodel, and integrates
the TCCM (Terminology Core Common Model). 

### TCCM Model

## Data

### CRDC Nodes Data Dictionaries

The documentation of the CRDC nodes models can be found here: 

https://docs.google.com/document/d/1Iu2HrbKykeNe3Q23NYEkHlWONEUV9GuWVNhzElf84TY

### Mappings

CCDH-curated mappings

NCIT-GDC mapping

### 

### Other References

References to caDSR CDEs 

## Loaders

The loader scripts load the data models and mappings into the Neo4J graph store. 

Data dictionary loaded:

* GDC
* PDC

Mappings loaded: 

* NCIT-GDC mapping

Ontologies and Concept Systems: 

* NCIT

## Set up

### Google Drive API

In order to extract the data from google drive sheets, [enable the Google drive API](https://developers.google.com/drive/api/v3/enable-drive-api). 

After API is enabled, stay in the [Google API Console](https://console.developers.google.com/), [create and download the client credentials](https://www.iperiusbackup.net/en/how-to-enable-google-drive-api-and-get-client-credentials/).

Save the file as `google_api_credentials.json` in the root directory of this project. 

The first time running the scripts, you will see a browser page asking
for you to log in. Folow the instructions. The script will download a token
and store it locally. You won't need to log in again in the future. 

### Python packages

Use pipenv to install python packages. 

```
pipenv install
```

## Run

To run the script to populate everything, run main

```
pipenv run python -m ccdh.main
```

## Data

The node github repos are added as git submodules.

The node github repos are documented here: https://docs.google.com/document/d/1Iu2HrbKykeNe3Q23NYEkHlWONEUV9GuWVNhzElf84TY

Note that HTAN data dictionary is not in the master branch. The branch is tracked in the submodule using 
these commands: 

```
git submodule add https://github.com/ncihtan/HTAN-data-pipeline.git
git submodule set-branch --branch organized-into-packages -- HTAN-data-pipeline/
git submodule update --recursive --remote
```

PDC uses git-lfs for some bigger files. If you don't have git-lfs installed, 
install it first: 

```
brew install git-lfs
```

Use this command to pull the files

```
cd crdc-nodes/PDC-Public/documentation/prod/json
# Run the install command only once
git lfs install
git lfs pull --include './*.json'
```

# BiolinkML generator for CCDH 

Create a `.env` file in the current directory. Put the following in the file: 

```
CDM_GOOGLE_SHEET_ID=1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4
```

Then run 

```
pipenv run python -m ccdh.biolinkml.cdm_biolinkml_loader
```

or run `pipenv shell` first and then the python command.
