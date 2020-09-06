from flask.cli import AppGroup
from jobs.save_gsc import save_gsc
from jobs.load_gbq import load_gbq
from jobs.compress_gcs_data import compress_gcs_data

job = AppGroup('job')
job.add_command(save_gsc)
job.add_command(load_gbq)
job.add_command(compress_gcs_data)
