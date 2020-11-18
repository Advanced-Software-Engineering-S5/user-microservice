import unittest, requests, time, pytest, sys
from multiprocessing import Process
from user_microservice.app import create_app
from user_microservice.database import db, User
from user_microservice.filter_sanitizer import sanitize_filter
from datetime import datetime


class TestEndpoints(unittest.TestCase):
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

        self.app = create_app(':memory:')

        with self.app.app_context():
            for user in self.user_list:
                db.session.add(User(**user))

            db.session.commit()

    def test_all(self):
        with self.app.test_client() as client:
            response = client.get('/users')
            self.assertEqual(len(response.get_json()), len(self.user_list))

    def test_create_user(self):
        with self.app.test_client() as client:
            client.post("/user",
                        json=dict(email='user5@test.com',
                                  firstname='user5',
                                  lastname='user5',
                                  password='user5',
                                  fiscal_code='Fake',
                                  dateofbirth=datetime(year=1996, month=1, day=5)))
            self.assertEqual(client.get("/user?email=user5@test.com").get_json()['email'], 'user5@test.com')

            self.assertEqual(client.get("/user?email=user6@test.com").status_code, 404)

            self.assertEqual(
                client.post("/user",
                            json=dict(email='user5@test.com',
                                      firstname='user5',
                                      lastname='user5',
                                      password='user5',
                                      fiscal_code='Fake',
                                      dateofbirth=datetime(year=1996, month=1, day=5))).status_code, 500)
            #No email
            self.assertEqual(
                client.post("/user",
                            json=dict(firstname='user5',
                                      lastname='user5',
                                      password='user5',
                                      fiscal_code='Fake',
                                      dateofbirth=datetime(year=1996, month=1, day=5))).status_code, 500)

    def test_filter(self):
        with self.app.test_client() as client:
            #Same tests from test_user
            user_list = client.put("/users/filter", json="and_(User.id > 2, User.id < 5)").get_json()
            self.assertEqual(len(user_list), 2)

            for user in user_list:
                self.assertEqual(type(datetime.fromisoformat(user['dateofbirth'])), datetime)

            user_birthday = client.put("/users/filter",
                                       json="User.dateofbirth == '{}'".format(
                                           self.user_list[0]['dateofbirth'].isoformat())).get_json()
            self.assertEqual(user_birthday[0]['email'], self.user_list[0]['email'])

            user_list = client.put("/users/filter",
                                   json="and_(User.dateofbirth > '{date1}', User.dateofbirth < '{date2}')".format(
                                       date1=self.user_list[0]['dateofbirth'].isoformat(),
                                       date2=self.user_list[3]['dateofbirth'].isoformat())).get_json()
            self.assertEqual(len(user_list), 2)

            #Check to fail if sending bad filter expr
            self.assertEqual(client.put("/users/filter", json="print('hello')").status_code, 500)

    def test_get(self):
        with self.app.test_client() as client:
            user = client.get("/user?id=1").get_json()
            self.assertEqual(user['id'], 1)
            self.assertEqual(user['dateofbirth'], datetime(year=1996, month=1, day=2).isoformat())

            #Must fail
            self.assertEqual(client.get("/user?blubba=3").status_code, 500)
            self.assertEqual(client.get("/user").status_code, 404)

    def test_update_field(self):
        with self.app.test_client() as client:
            self.assertEqual(client.post("/user/1/firstname", json="mario").status_code, 200)
            self.assertEqual(client.post("/user/1/stuff", json="mario").status_code, 500)

    def test_get_field(self):
        with self.app.test_client() as client:
            self.assertEqual(client.get("/user/1/firstname").get_json(), "user1")
            self.assertEqual(client.get("/user/1/stuff").status_code, 500)

            #datetime test
            self.assertEqual(datetime.fromisoformat(client.get("/user/1/dateofbirth").get_json()),
                             self.user_list[0]['dateofbirth'])

    def test_auth(self):
        with self.app.test_client() as client:
            self.assertEqual(
                client.post("/user/auth",
                            json=dict(email=self.user_list[0]['email'],
                                      password=self.user_list[0]['password'])).status_code, 200)
            self.assertEqual(
                client.post("/user/auth", json=dict(email=self.user_list[0]['email'], password="password")).status_code,
                401)

    def test_sanitizer(self):
        self.assertTrue(sanitize_filter("User.id == 3"))
        self.assertTrue(sanitize_filter("User.firstname == 'mario'"))
        self.assertFalse(sanitize_filter("User.firstname == "))