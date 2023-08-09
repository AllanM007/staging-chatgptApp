import app
from celery import Celery
from celery.schedules import crontab

app = Celery()


@app.task
def run_archiver():
    from app import archiver

    archiver.run()
