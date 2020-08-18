# CRDC Node Model Value Sets

Scripts for CRDC node model value sets harmonization

Documentation: https://docs.google.com/document/d/1Iu2HrbKykeNe3Q23NYEkHlWONEUV9GuWVNhzElf84TY


## Set up

### Google Drive API

In order to extract the data from google drive sheets, ![enable the Google drive API](https://developers.google.com/drive/api/v3/enable-drive-api). 

After API is enabled, stay in the ![Google API Console](https://console.developers.google.com/), ![create and download the client credentials](https://www.iperiusbackup.net/en/how-to-enable-google-drive-api-and-get-client-credentials/).

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