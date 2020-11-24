import unittest
from user_microservice.unmark_user_task import unmark_all
from user_microservice.background import make_celery
from celery.contrib.testing.worker import start_worker
import os
from user_microservice.app import create_app
from datetime import datetime
from user_microservice.database import User, db

app = create_app(":memory:")

class UserUnmarkingTaskTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # start celery worker with test app context and in-memory context 
        celery_app = make_celery(app)
        cls.celery_worker = start_worker(celery_app, perform_ping_check=False)
        # spawn celery worker
        cls.celery_worker.__enter__()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # kill celery worker when tests are done
        cls.celery_worker.__exit__(None, None, None)

    def tearDown(self) -> None:
        db.drop_all(app=app)

    def test_user_unmarking(self):
        # mark some user
        user = {
            'email': "user1@test.com",
            'firstname': "user1",
            'lastname': "user1",
            'fiscal_code': "Fake1",
            'password': "user1",
            'is_positive': True,
            'dateofbirth': datetime(year=1996, month=1, day=2),
            'confirmed_positive_date': datetime(year=1996, month=1, day=2),
            'reported_positive_date': datetime(year=1996, month=1, day=2),
        }
        with app.app_context():
            user = User(**user)
            print('is positive', user.is_positive)
            db.session.add(user)
            db.session.commit()
            # start and await unmark all task
            unmark_all.delay(14).get()
            # check if user was unchecked successfully

            user = User.query.filter_by(email="user1@test.com").first()
            self.assertEqual(user.is_positive, False)
            self.assertIsNone(user.reported_positive_date)
        
