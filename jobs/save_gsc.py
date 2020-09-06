import conf
import click
from flask.cli import with_appcontext
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import urllib.parse
import os
from google.cloud import storage
import pandas as pd


class URL(click.ParamType):
    name = "url"

    def convert(self, value, param, ctx):
        if not isinstance(value, tuple):
            parse_result = urllib.parse.urlparse(value)
            if parse_result.scheme not in ("http", "https"):
                self.fail(
                    f"invalid URL scheme ({parse_result.scheme}). Only HTTP URLs are allowed",
                    param,
                    ctx,
                )
        return {"value": value,
                "parse_result": parse_result}

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']


@click.command('save_gsc', help="Save Google Search Console data in the database")
@click.argument('gsc_property_name', type=URL())
@click.argument('gsc_credentials_path')
@click.argument('date')
@click.argument('bucket_name')
@click.argument('file_dir_name')
@with_appcontext
def save_gsc(gsc_property_name, gsc_credentials_path, date, bucket_name, file_dir_name):

    credentials = ServiceAccountCredentials.from_json_keyfile_name(gsc_credentials_path, SCOPES)
    webmasters = build('webmasters', 'v3', credentials=credentials)
    url = gsc_property_name.get('value')
    d_list = ['query', 'date', 'country', 'device', 'page']
    start_date = date
    end_date = date
    row_limit = 25000

    body = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': d_list,
        'rowLimit': row_limit
    }
    response = webmasters.searchanalytics().query(siteUrl=url, body=body).execute()
    df = pd.json_normalize(response['rows'])
    for i, d in enumerate(d_list):
        df[d] = df['keys'].apply(lambda x: x[i])
    df.drop(columns='keys', inplace=True)
    df['page'] = df['page'].apply(lambda x: urllib.parse.unquote(x))
    temp_file_name = 'temp.csv'
    df.to_csv(temp_file_name, index=False)

    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    file_name = conf.CSV_PREFIX + date.replace("-", "") + ".csv"
    blob = bucket.blob(file_dir_name + file_name)
    blob.upload_from_filename(filename=temp_file_name)

    if os.path.exists(temp_file_name): os.remove(temp_file_name)
