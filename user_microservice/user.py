import requests, json
from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Optional


def try_fromisoformat(iso):
    if type(iso) == str:
        try:
            return datetime.fromisoformat(iso)
        except ValueError:
            pass
    return None


@dataclass(eq=False, order=False)
class User:
    """
    User abstraction over REST endpoints.
    Do not return such instances and do not pass them around as function arguments. Each procedure should do its own
    User.get call.
    """

    BASE_URL = "http://0.0.0.0:5000"

    id: int
    email: str
    firstname: Optional[str]
    lastname: Optional[str]
    fiscal_code: Optional[str]
    phone: Optional[str]
    password: Optional[str]
    dateofbirth: Optional[datetime]
    is_active: Optional[bool]
    is_admin: Optional[bool]
    is_positive: Optional[bool]
    reported_positive_date: Optional[datetime]
    confirmed_positive_date: Optional[datetime]
    restaurant_id: Optional[int]

    #This always represents what's in the database (hopefully)
    invariant: dict = field(init=False, repr=False)

    @staticmethod
    def get(*, id=None, email=None, fiscal_code=None, phone=None):
        """
        Gets an User instance if it is found, otherwise returns None.
        Arguments are all keyword arguments.

        Example:
            usr = User.get(id=1)
            usr = User.get(email='op@op.com')
        """
        req = requests.get(f"{User.BASE_URL}/user",
                           params={
                               'id': id,
                               'email': email,
                               'fiscal_code': fiscal_code,
                               'phone': phone
                           })

        if req.status_code == 200:
            json_dict = req.json()

            # Turn iso format into datetime object
            json_dict['dateofbirth'] = try_fromisoformat(json_dict['dateofbirth'])
            json_dict['reported_positive_date'] = try_fromisoformat(json_dict['reported_positive_date'])
            json_dict['confirmed_positive_date'] = try_fromisoformat(json_dict['confirmed_positive_date'])
            usr = User(**json_dict)
            usr.invariant = json_dict
            return usr
        else:
            return None

    def submit(self):
        """
        Updates the user database with the modified fields.
        If the update fails the instance is reverted to a state consistent with the db (hopefully).

        Example:
            usr.firstname = "aldo"
            usr.submit()
        """
        for field in fields(self):
            attr = getattr(self, field.name)
            if field.init and attr != self.invariant[field.name]:
                req = requests.post(f"{User.BASE_URL}/user/{self.id}/{field.name}",
                                    json=attr.isoformat() if type(attr) == datetime else attr)
                if req.status_code == 200:
                    self.invariant[field.name] = attr
                else:
                    setattr(self, field.name, self.invariant[field.name])

    @staticmethod
    def create(*,
               email,
               firstname=None,
               lastname=None,
               password=None,
               fiscal_code=None,
               phone=None,
               dateofbirth=None,
               restaurant_id=None):
        """
        Creates an user.
        Remember to check the return value.
        """
        user_dict = {
            'email': email,
            'firstname': firstname,
            'lastname': lastname,
            'password': password,
            'fiscal_code': fiscal_code,
            'phone': phone,
            'dateofbirth': dateofbirth.isoformat() if type(dateofbirth) == datetime else dateofbirth,
            'restaurant_id': restaurant_id
        }

        req = requests.post(f"{User.BASE_URL}/user", json=user_dict)
        if req.status_code == 201:
            return req.json()
        else:
            return None

    @staticmethod
    def all():
        """
        Returns a list of all the users
        """
        req = requests.get(f"{User.BASE_URL}/users")
        if req.status_code == 200:
            lst = list()
            for user_json in req.json():

                # Turn iso format into datetime object
                user_json['dateofbirth'] = try_fromisoformat(user_json['dateofbirth'])
                user_json['reported_positive_date'] = try_fromisoformat(user_json['reported_positive_date'])
                user_json['confirmed_positive_date'] = try_fromisoformat(user_json['confirmed_positive_date'])

                usr = User(**user_json)
                usr.invariant = user_json
                lst.append(usr)
            return lst
        else:
            return None

    @staticmethod
    def filter(str: str):
        """
        Returns a list of filtered users, str is a Python expression containing only values and User fields.
        Timestamps have to be sent as ISO format strings (isoformat() method).

        Example:
            User.filter("and_(User.id > 3, User.id < 6)")
            User.filter("and_(User.dateofbirth > '2020-11-18T20:54:25.509863', User.dateofbirth < '2020-11-18T20:54:25.509881')")
        """
        req = requests.get(f"{User.BASE_URL}/users/filter", params=dict(filter=str))
        if req.status_code == 200:
            lst = list()
            for user_json in req.json():

                # Turn iso format into datetime object
                user_json['dateofbirth'] = try_fromisoformat(user_json['dateofbirth'])
                user_json['reported_positive_date'] = try_fromisoformat(user_json['reported_positive_date'])
                user_json['confirmed_positive_date'] = try_fromisoformat(user_json['confirmed_positive_date'])

                usr = User(**user_json)
                usr.invariant = user_json
                lst.append(usr)
            return lst
        else:
            return None
