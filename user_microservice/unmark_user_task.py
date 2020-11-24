from user_microservice.background import celery
import logging
from datetime import datetime, timedelta
from user_microservice.database import User, db

@celery.task
def unmark_all(range_days : int):
    """ Unmakr all the users marked more than a certain number of days ago.
    Args:
        range_days (int): Number of days positive users have to be unmarked
    Returns:
        [str]: '' in case of success, a error message string in case of failure.
    """
    logging.info("Unmarking users..")
    now = datetime.now()
    time_limit = now - timedelta(days=range_days)
    users = User.query.filter_by(is_positive=True).\
        filter(User.reported_positive_date <= time_limit).all()
    for user in users:
        if user != None and user.is_positive == True:
            user.is_positive = False
            user.reported_positive_date = None
    db.session.commit()

    return ''

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    logging.info("Configuring crono task..")
    # Register the unmark_all as crono task
    sender.add_periodic_task(60.0 * 60.0, unmark_all.s(14), name='unmark_positive')