import conf
import click
from flask.cli import with_appcontext
from google.cloud import bigquery
from google.cloud.bigquery.dataset import DatasetReference


@click.command('load_gbq', help="Load Google Big Query from Google Cloud Storage")
@click.argument('date')
@click.argument('data_set_id')
@click.argument('gcs_dir')
@with_appcontext
def load_gbq(date, data_set_id, gcs_dir):
    table_name = file_name = conf.TABLE_PREFIX + date.replace("-", "")
    client = bigquery.Client()
    data_set_ref = DatasetReference.from_string(data_set_id)
    job_config = bigquery.LoadJobConfig()
    job_config.autodetect = True
    job_config.skip_leading_rows = 1

    # The source format defaults to CSV, so the line below is optional.
    job_config.source_format = bigquery.SourceFormat.CSV
    table_ref = DatasetReference.from_string(data_set_id).table(table_name)
    try:
        client.delete_table(table_ref)  # API request
    except:
        pass
    uri = gcs_dir + file_name + '.csv'
    load_job = client.load_table_from_uri(
        uri,
        data_set_ref.table(table_name),
        job_config=job_config)  # API request

    assert load_job.job_type == 'load'

    load_job.result()  # Waits for table load to complete.

    assert load_job.state == 'DONE'
