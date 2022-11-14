"""
Template for the database. After a change, a database upgrade must be done
"""

# pylint: disable=invalid-name
import collections
import strict_rfc3339
import jwt
from datetime import datetime, timedelta
from time import time
import secrets
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from hashlib import md5
from . import db, login_manager


class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(64), nullable=False, index=True)
    access_expiration = db.Column(db.DateTime, nullable=False)
    refresh_token = db.Column(db.String(64), nullable=False, index=True)
    refresh_expiration = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                          index=True)

    user = db.relationship('User', back_populates='tokens')

    def generate(self):
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = datetime.utcnow() + \
            timedelta(minutes=current_app.config['ACCESS_TOKEN_MINUTES'])
        self.refresh_token = secrets.token_urlsafe()
        self.refresh_expiration = datetime.utcnow() + \
            timedelta(days=current_app.config['REFRESH_TOKEN_DAYS'])

    def expire(self, delay=None):
        if delay is None:  # pragma: no branch
            # 5 second delay to allow simultaneous requests
            delay = 5 if not current_app.testing else 0
        self.access_expiration = datetime.utcnow() + timedelta(seconds=delay)
        self.refresh_expiration = datetime.utcnow() + timedelta(seconds=delay)

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        db.session.execute(Token.delete().where(
            Token.refresh_expiration < yesterday))

# pylint: disable=no-member
class User(UserMixin, db.Model):

    """
    Template for the User table

    Attributes:
        __tablename__: table title
        id: User id
        username: Takes the user's username
        email: Takes the user's email
        password_hash: storing the hashed & salted password
    """

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True)
    email = db.Column(db.String(128), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    tokens = db.relationship('Token', back_populates='user',
                                   lazy='noload')

    @property
    def password(self):
        """
        Password should not be readable

        Args:
            self: is a class argument

        Raises:
            AttributeError: when the password contains an unreadable attribute
        """
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """
        Hash password so it is not stored plaintext in the db

        Args:
            self: is a class argument
            password: is the un-hashed password

        Returns:
            self.password_hash, which is now the hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Verify the hashed password is in the db

        Args:
            self: is a class argument
            password: is the un-hashed password

        Returns:
            check_password_hash which verifies that the
            hashed password is in the database
        """
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        """
        Create a confirmation token for authentication over email
        """
        encoded_token = jwt.encode(
            {
                'exp': time() + current_app.config['RESET_TOKEN_MINUTES'] * 60,
                'conf_email': self.email,
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return encoded_token

    def verify_confirmation_token(self, conf_token):
        """
        Use confirmation token and ensure that email of user matches
        confirmation token email
        """
        try:
            data = jwt.decode(conf_token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except jwt.PyJWTError:
            return False
        if self.email == data['conf_email']:
            self.confirmed = True
            db.session.add(self)
            db.session.commit()
            return True
        return False

    def generate_auth_token(self):
        token = Token(user=self)
        token.generate()
        return token

    @staticmethod
    def verify_access_token(access_token, refresh_token=None):
        token = db.session.scalar(Token.select().filter_by(
            access_token=access_token))
        if token:
            if token.access_expiration > datetime.utcnow():
                db.session.commit()
                return token.user

    @staticmethod
    def verify_refresh_token(refresh_token, access_token):
        token = db.session.scalar(Token.select().filter_by(
            refresh_token=refresh_token, access_token=access_token))
        if token:
            if token.refresh_expiration > datetime.utcnow():
                return token

            # someone tried to refresh with an expired token
            # revoke all tokens from this user as a precaution
            token.user.revoke_all()
            db.session.commit()

    def revoke_all(self):
        db.session.execute(Token.delete().where(Token.user == self))

    def generate_reset_token(self):
        """
        Create a reset token for authentication over email
        """
        encoded_token = jwt.encode(
            {
                'exp': time() + current_app.config['RESET_TOKEN_MINUTES'] * 60,
                'reset_email': self.email,
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return encoded_token

    def verify_reset_token(self, reset_token, form_data):
        """
        Use reset token and ensure that email of user matches
        reset token email. Then update the password
        """
        try:
            data = jwt.decode(reset_token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except jwt.PyJWTError:
            return False
        if self.email == data['reset_email']:
            self.password = form_data
            db.session.add(self)
            db.session.commit()
            return True
        return False

@login_manager.user_loader
def load_user(user_id):
    """
    Loads user for queries

    Args:
        user_id: user's token verified id

    Results:
        User.query.get(int(user_id)) which loads the user
    """
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    """Used as user when they are not signed in"""
    # pylint: disable=no-self-use

    def is_administrator(self):
        """
        If not signed in

        Args:
            self: is a class argument

        Returns:
            Flase which stops the user if the user is not signed in
        """
        return False  # pragma: no cover


login_manager.anonymous_user = AnonymousUser


class Accountants(db.Model):
    """Template for the Accountants Info table"""
    __tablename__ = 'accountants'
    # metadata
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(128), index=True, unique=True)
    phone_num = db.Column(db.String(64), index=True, unique=True)
    company = db.Column(db.String(128))
    specialty = db.Column(db.String(128))
    about_me = db.Column(db.String(140))

    @property
    def avatar_url(self):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon'

    @staticmethod
    def flatten(dictionary, parent_key='', sep='__'):
        """
        Flattens nested incoming JSON messages

        Args:
            dictionary: input dictionary.
            parent_key: the key for the nest
            sep: is the characters between each flattened level

        Returns:
            dict, which takes the data and formats it into a
            dictionary and indexes them by keys
        """
        items = []
        for key, value in dictionary.items():
            new_key = parent_key + sep + key if parent_key else key
            if isinstance(value, collections.MutableMapping):
                items.extend(Accountants.flatten(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
        return dict(items)

    @staticmethod
    def invalid_data(json_post, accepted_json):
        """
        Analyzes json message for any None values, returns which ones are
        missing.

        Args:
            json_post: a json message stored as a flattened python dict
            accepted_json: a json message that matches the accepted API

        Returns:
            A list of missing data or invalid sensors as a tuple of
            (missing_data, invalid_sensors)
        """
        """
        missing_data = []
        data = Accountants.from_json(json_post)
        to_json_data = data.to_json()
        for key, value in to_json_data.items():
            if value == "None":
                if not current_app.config['TESTING']:  # pragma: no cover
                    # disable print statement during testing
                    # to avoid filling console with messages
                    print('WARNING: Data missing for the following sensor:',
                          key)
                missing_data.append(key)

        invalid_sensors = []
        for key in json_post.keys():
            if key not in accepted_json:
                if not current_app.config['TESTING']:  # pragma: no cover
                    # disable print statement during testing
                    # to avoid filling console with messages
                    print('WARNING: The following sensor has been '
                          'added and is not in the database:', key)
                    print('Ensure this new sensor is added to the appropriate '
                          'backend functions.')
                invalid_sensors.append(key)
        return missing_data, invalid_sensors
        """
        pass

    def to_json(self):
        """
        Converts to JSON for API

        Args:
            self: is a class argument

        Returns:
            json_post which is the converted JSON for API
        """
        json_post = {
            # Metadata
            'name': self.name,
            'email': self.email,
            'phone_num': self.phone_num,
            'company': self.company,
            'specialty': self.specialty,
            'about_me': self.about_me,
            'avatar' : self.avatar_url
        }
        return json_post

    # pylint: disable=line-too-long
    @staticmethod
    def from_json(json_post):
        """
        Converts from JSON for API

        Args:
            json_post: the converted JSON data for the API

        Results:
            Accountants, which is the newly converted JSON data for API

        Raisess:
            ValidationError is date or time are missing
        """
        # Metadata
        id = json_post.get('id')
        name = json_post.get('name')
        email = json_post.get('email')
        phone_num = json_post.get('phone_num')
        company = json_post.get('company')
        specialty = json_post.get('specialty')
        about_me = json_post.get('about_me')

        return Accountants(id=id,
                       name=name,
                       email=email,
                       phone_num=phone_num,
                       company=company,
                       specialty=specialty,
                       about_me=about_me)
