from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), unique=True, nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    fiscal_code = db.Column(db.Text(50), unique=True)
    phone = db.Column(db.Text(20), nullable=True, unique=True)
    password = db.Column(db.Unicode(128))
    dateofbirth = db.Column(db.DateTime)
    confirmed_positive_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_positive = db.Column(db.Boolean, default=False)
    reported_positive_date = db.Column(db.DateTime, nullable=True)
    restaurant_id = db.Column(db.Integer, nullable=True)
    is_anonymous = False

    # Now that everything is split into microservices this isn't needed anymore
    # #One to one relationship
    # restaurant = db.relationship("Restaurant", back_populates="operator", uselist=False)

    # #One to many relationship
    # reservations = db.relationship("Reservation", back_populates="user")

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    # @property
    # def is_authenticated(self):
    #     return self._authenticated

    # def authenticate(self, password):
    #     checked = check_password_hash(self.password, password)
    #     self._authenticated = checked
    #     return self._authenticated

    def get_id(self):
        return self.id

    def __str__(self) -> str:
        return f'{self.firstname} {self.lastname}--mail:{self.email}--born:{self.dateofbirth.strftime("%B %d %Y")}'

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
