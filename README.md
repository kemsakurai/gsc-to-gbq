# gsc-to-gbq
Google Search Console Data to Google Big Query

--------------
## Usage   

* git clone     
```console
git clone https://github.com/kemsakurai/gsc-to-gbq.git    
```

* pip install    
```console
pip install -r requirements.txt    
```

* job list   
```console
export FLASK_APP=cli
flask job 
```

```console
Usage: flask job [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  load_gbq  Load Google Big Query from Google Cloud Storage
  save_gsc  Save Google Search Console data in the database

```

* save_gsc    
```console
export FLASK_APP=cli
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
flask job save_gsc {GSC_PROPERTY_NAME} \
{GSC_CREDENTIALS_PATH} \
{DATE} {BUCKET_NAME} {FILE_DIR_NAME}
```

* load_gbq     
```console
export FLASK_APP=cli
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
flask job load_gbq {DATE} \
{DATA_SET_ID} \
{GCS_DIR}
```

