# CRDC Node Model Value Sets

Scripts for CRDC node model value sets harmonization

Documentation: https://docs.google.com/document/d/1Iu2HrbKykeNe3Q23NYEkHlWONEUV9GuWVNhzElf84TY


## Set up

### Google Drive API

In order to extract the data from google drive sheets, [enable the Google drive API](https://developers.google.com/drive/api/v3/enable-drive-api). 

After API is enabled, stay in the [Google API Console](https://console.developers.google.com/), [create and download the client credentials](https://www.iperiusbackup.net/en/how-to-enable-google-drive-api-and-get-client-credentials/).

Save the file as `google_api_credentials.json` in the root directory of this project. 

The first time running the scripts, you will see a browser page asking
for you to log in. Folow the instructions. The script will download a token
and store it locally. You won't need to log in in the future. 

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