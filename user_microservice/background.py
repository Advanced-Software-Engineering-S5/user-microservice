from datetime import datetime, timedelta
from user_microservice.app import create_app
from celery import Celery
import os

# set this configs as env variables
BACKEND = BROKER = f"redis://{os.environ.get('GOS_REDIS')}"
def make_celery(app):
    # create celery object from single flask app configuration
    celery = Celery(__name__, backend=app.config['CELERY_RESULT_BACKEND'], 
    broker = app.config['CELERY_BROKER_URL'], 
    include = ['user_microservice.unmark_user_task']) # include list of modules to import when worker starts

    celery.conf.update(app.config)
    # subclass celery task so that each task execution is wrapped in an app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(create_app())