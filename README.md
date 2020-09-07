# gsc-to-gbq

Load Google Search Console data into Google Big Query.    
It is designed to run as a cronjob on a Linux server.       

-----    

## Install   

This tool works with Python3.
You can use the tool by cloning the repository and installing the library with the pip command.
When installing on a virtual environment such as venv, it is necessary to create the environment and switch to the virtual environment before executing the following command.   

### Prerequisites   

The Tool requires two service account keys. One is a Google Search Console service account and the other is a Google Cloud Storage and Big Query service account.   
You can specify different keys for each, You can also reuse a single key file, assuming you give the account permissions.   

   
### Git clone and install libraries        
     
```console
git clone https://github.com/kemsakurai/gsc-to-gbq.git    
cd gsc-to-gbq
pip install -r requirements.txt    
```

-----

## Command usage      

* **job list**  
```console
export FLASK_APP=cli
flask job 
```

```console
Usage: flask job [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  compress_gcs_data  Compress data uploaded Google Cloud Storage to gzip
  load_gbq           Load Google Big Query from Google Cloud Storage
  save_gsc           Save Google Search Console data in the database
```

Outputs a list of commands.

* **save_gsc**       
```console
export FLASK_APP=cli
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
DATE="2020-05-18"
GSC_PROPERTY_NAME="https://www.monotalk.xyz/"
GSC_CREDENTIALS_PATH="./gsc_client.json"
BUCKET_NAME="monotalk.appspot.com"
FILE_DIR_NAME="GSC Statistics/www.monotalk.xyz/"
flask job save_gsc {GSC_PROPERTY_NAME} \
{GSC_CREDENTIALS_PATH} \
{DATE} {BUCKET_NAME} {FILE_DIR_NAME}
```
Save Google Search Console data to Google Cloud Storage. The Google Search Console API can minimize data loss by retrieving data daily.
The tool retrieves data by specifying'query','date','country','device','page' as dimensions one day at a time.   


* **load_gbq**     
```console
export FLASK_APP=cli
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
DATE="2020-05-18"
DATA_SET_ID="monotalk.GA_Statistics"
GCS_DIR="gs://monotalk.appspot.com/GSC Statistics/www.monotalk.xyz/"
flask job load_gbq {DATE} \
{DATA_SET_ID} \
{GCS_DIR}
```
Load the JSON file uploaded to Google Cloud Storage into Google BigQuery.    

* **compress_gcs_data**   
```console
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
export FLASK_APP=cli
DATE="2020-05-18"
BUCKET_NAME="monotalk.appspot.com"
FILE_DIR_NAME="GSC Statistics/www.monotalk.xyz/"
flask job compress_gcs_data "$DATE" "$BUCKET_NAME" "$FILE_DIR_NAME"
```
Compress the JSON file uploaded to Google Cloud Storage into gzip. A new compressed gzip file will be uploaded and the original JSON file will be deleted.    
   
---

## Command execution order   

Execute the commands on a daily basis in the following order.
Data of Google Search Console may not be acquired if specified on the day.
We recommend that you specify a date that is at least one day in advance and execute it.

1. save_gsc  
2. load_gbq  
3. compress_gcs_data   


---   
## Job Scheduling EXAMPLES

This is an example of a script that executes a Python job and a cron job that uses that script.    

* **run_gsc_to_gbq.sh**  
```console
#!/bin/bash

shellName=$(basename $0)
homeDir=$(pwd)
toolHome="/home/jobuser/tools/gsc-to-gbq"

prepareRun() {
  cd $toolHome
  source /home/jobuser/venv/gsc_to_gbq/bin/activate
  export FLASK_APP=cli
  export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
}

getTreeDaysAgo() {
  if [ "$(uname)" == 'Darwin' ]; then
    DATE=`date -v-3d +'%Y-%m-%d'`
  elif [ "$(expr substr $(uname -s) 1 5)" == 'Linux' ]; then
    DATE=`date '+%Y-%m-%d' --date '3 days ago'`
  elif [ "$(expr substr $(uname -s) 1 10)" == 'MINGW32_NT' ]; then
    DATE=`date '+%Y-%m-%d' --date '3 days ago'`
  else
    echo "Your platform ($(uname -a)) is not supported."
    exit 1
  fi
  echo $DATE
}

sub_help(){
    echo "Usage: $shellName <subcommand> [options]\n"
    echo "Subcommands:"
    echo "    saveGsc   Save Google Search Consle data to Google Cloud Storage."
    echo "    loadGbq Load data to Google Big Query from Google Cloud Storage."
    echo "    compressGcsData Compress data uploaded Google Cloud Storage to gzip."
    echo ""
    echo "For help with each subcommand run:"
    echo "$shellName <subcommand> -h|--help"
    echo ""
}

sub_saveGsc() {
  prepareRun
  DATE=`getTreeDaysAgo`
  GSC_PROPERTY_NAME="https://www.monotalk.xyz/"
  GSC_CREDENTIALS_PATH="./gsc_client.json"
  BUCKET_NAME="monotalk.appspot.com"
  FILE_DIR_NAME="GSC Statistics/www.monotalk.xyz/"

  flask job save_gsc \
  "$GSC_PROPERTY_NAME" \
  "$GSC_CREDENTIALS_PATH" \
  "$DATE" \
  "$BUCKET_NAME" \
  "$FILE_DIR_NAME"
}

sub_loadGbq() {
  prepareRun
  DATE=`getTreeDaysAgo`
  DATA_SET_ID="monotalk.GSC_Statistics"
  GCS_DIR="gs://monotalk.appspot.com/GSC Statistics/www.monotalk.xyz/"

  flask job load_gbq \
  "$DATE" \
  "$DATA_SET_ID" \
  "$GCS_DIR"
}

sub_compressGcsData() {
  prepareRun
  DATE=`getTreeDaysAgo`
  BUCKET_NAME="monotalk.appspot.com"
  FILE_DIR_NAME="GSC Statistics/www.monotalk.xyz/"

  flask job compress_gcs_data \
  "$DATE" \
  "$BUCKET_NAME" \
  "$FILE_DIR_NAME"
}


for subcommand in "$@"; do
    case $subcommand in
        "" | "-h" | "--help")
            sub_help
            ;;
        *)
            shift
            sub_${subcommand} $@
            returnCode=$?
            if [ $returnCode = 127 ]; then
                echo "Error: '$subcommand' is not a known subcommand." >&2
                echo "       Run '$shellName --help' for a list of known subcommands." >&2
                exit 1
            elif [ $returnCode = 1 ]; then
                echo "Error: '$subcommand' is failed.." >&2
                exit 1            
            fi
            ;;
    esac
done

```

* **crontab**       
```console
# coomon settings
MAILTO="your.mail@example.com"
MAILFROM="error-notifications@example.com"
LOG_DIR="/var/log"
# ga-to-gbq
SH_GA_TO_GBQ="/home/jobuser/scripts/run_ga_to_gbq.sh"

00 01 * * * /bin/sh $SH_GSC_TO_GBQ saveGsc &>> $LOG_DIR/gsc_to_gbq_saveGsc.log && /bin/sh $SH_GSC_TO_GBQ loadGbq &>> $LOG_DIR/gsc_to_gbq_loadGbq.log && /bin/sh $SH_GSC_TO_GBQ compressGcsData &>> $LOG_DIR/gsc_to_gbq_compressGcsData.log
```


---

## LICENSE   

MIT


