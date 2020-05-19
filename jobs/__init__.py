from flask.cli import AppGroup
from jobs.save_gsc import save_gsc
from jobs.load_gbq import load_gbq

job = AppGroup('job')
job.add_command(save_gsc)
job.add_command(load_gbq)

