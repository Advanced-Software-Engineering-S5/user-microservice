import unittest, requests, time
import user_microservice.database 
from user_microservice.user import User, try_fromisoformat
from user_microservice.app import create_app
from datetime import datetime
from requests.exceptions import ConnectionError
from flask_testing import LiveServerTestCase

User.BASE_URL = "http://0.0.0.0:4200"
db = user_microservice.database.db

class TestUserMicroservice(LiveServerTestCase):
    # @classmethod
    # def setUpClass(cls):
    #     cls.app = create_app(":memory:")
    #     cls.p = Process(target=cls.app.run, kwargs={'host': "0.0.0.0", 'port': "5000"}, daemon=True)
    #     cls.p.start()
    #     time.sleep(4)

    # @classmethod
    # def tearDownClass(cls):
    #     cls.p.terminate()
    def create_app(self):
        self.app = create_app(":memory:")
        self.app.config['TESTING'] = True
        # Default port is 5000
        self.app.config['LIVESERVER_IP'] = "0.0.0.0"
        self.app.config['LIVESERVER_PORT'] = 4200
        # Default timeout is 5 seconds
        self.app.config['LIVESERVER_TIMEOUT'] = 10
        return self.app

    def setUp(self):
        self.user_list = [{
            'email': "user1@test.com",
            'firstname': "user1",
            'lastname': "user1",
            'fiscal_code': "Fake1",
            'password': "user1",
            'dateofbirth': datetime(year=1996, month=1, day=2)
        }, {
            'email': "user2@test.com",
            'firstname': "user2",
            'lastname': "user2",
            'fiscal_code': "Fake2",
            'password': "user12",
            'dateofbirth': datetime(year=1996, month=1, day=3)
        }, {
            'email': "user3@test.com",
            'firstname': "user3",
            'lastname': "user3",
            'fiscal_code': "Fake3",
            'password': "user3",
            'dateofbirth': datetime(year=1996, month=1, day=4)
        }, {
            'email': "user4@test.com",
            'firstname': "user4",
            'lastname': "user4",
            'fiscal_code': "Fake4",
            'password': "user4",
            'dateofbirth': datetime(year=1996, month=1, day=5)
        }]

        for user_dict in self.user_list:
            User.create(**user_dict)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_create_user(self):
        user_id = User.create(email='user5@test.com',
                              firstname='user5',
                              lastname='user5',
                              password='user5',
                              fiscal_code='Fake',
                              dateofbirth=datetime(year=1996, month=1, day=5))
        self.assertEqual(user_id, 5)
        #This should fail because of unique constraints
        user_id = User.create(email='user5@test.com',
                              firstname='user5',
                              lastname='user5',
                              password='user5',
                              fiscal_code='Fake',
                              dateofbirth=datetime(year=1996, month=1, day=5))
        self.assertIsNone(user_id)

    def test_all(self):
        user_list = User.all()
        self.assertEqual(len(user_list), len(self.user_list))

        for user in user_list:
            self.assertEqual(type(user.dateofbirth), datetime)

    def test_filter(self):
        user_list = User.filter("and_(User.id > 2, User.id < 5)")
        self.assertEqual(len(user_list), 2)

        for user in user_list:
            self.assertEqual(type(user.dateofbirth), datetime)

        user_birthday = User.filter("User.dateofbirth == '{}'".format(self.user_list[0]['dateofbirth'].isoformat()))
        self.assertEqual(user_birthday[0].email, self.user_list[0]['email'])

        user_list = User.filter("and_(User.dateofbirth > '{date1}', User.dateofbirth < '{date2}')".format(
            date1=self.user_list[0]['dateofbirth'].isoformat(), date2=self.user_list[3]['dateofbirth'].isoformat()))
        self.assertEqual(len(user_list), 2)

        user_list = User.filter("bubba")
        self.assertIsNone(user_list)

    def test_get(self):
        user = User.get(id=1)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.dateofbirth, datetime(year=1996, month=1, day=2))

        user = User.get(id=1337)
        self.assertIsNone(user)

    def test_submit(self):
        now = datetime.now()

        user = User.get(id=1)
        user.firstname = "mario"
        user.is_admin = True
        user.is_positive = True
        user.confirmed_positive_date = now
        user.reported_positive_date = now
        user.dateofbirth = datetime(year=1997, month=4, day=3)
        user.submit()

        self.assertEqual(User.get(id=1).firstname, "mario")
        self.assertEqual(User.get(id=1).dateofbirth, datetime(year=1997, month=4, day=3))
        self.assertEqual(User.get(id=1).is_admin, True)
        self.assertEqual(User.get(id=1).is_positive, True)
        self.assertEqual(User.get(id=1).confirmed_positive_date, now)
        self.assertEqual(User.get(id=1).reported_positive_date, now)
    
    def test_datetime_conversion(self):
        self.assertIsNotNone(try_fromisoformat(datetime.now().isoformat()))
        self.assertIsNone(try_fromisoformat("blergh"))