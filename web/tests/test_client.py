"""Tests all views and functions in main"""
import re
import time
import json
import unittest
from flask import url_for, current_app
from app import create_app, db
from app.models import User


class FlaskClientTestCase(unittest.TestCase):
    """
    Test as if is using the software through the webpages. They can
    register, log in and log out, look at data, and post data.
    """

    def setUp(self):
        """Set up test environment"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        with open('./tests/example_compact.json') as json_data:
            loaded_json = json.load(json_data)
            self.EXAMPLE_COMPACT_JSON_MESSAGE = json.dumps(loaded_json)
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        """Tear down environment after test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        """So posting and getting can be tested"""

        # create account
        response = self.client.post(url_for('auth.register'), data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'username': 'Waluigi',
            'password': 'walawala',
            'password2': 'walawala',
        })

        # sign in
        response = self.client.post(url_for('auth.login'), data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala'
        }, follow_redirects=True)
        self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))

        # confirm account
        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token),
                                   follow_redirects=True)

    def logout(self):
        """Puts logout here, makes tests cleaner"""
        response = self.client.get(url_for('auth.logout'),
                                   follow_redirects=True)
        self.assertTrue(b'You have been logged out' in response.data)

    # TEST PAGES WORK

    def test_home_page(self):
        """Checks index is working"""
        response = self.client.get(url_for('main.index'))
        self.assertTrue(b'operational' in response.data)

    def test_json_post_page(self):
        """Check that the json post page is working"""
        self.login()
        response = self.client.get(url_for('main.manual_json_post'))
        self.assertTrue(b'This is the JSON POST page.' in response.data)

    # TEST ERRORS

    def test_404(self):
        """Check 404 by giving bad url"""
        response = self.client.get('/wrong/url')
        self.assertTrue(response.status_code == 404)

    def test_405(self):
        """Check 405 by posting to a get-only page"""
        response = self.client.post(url_for('main.index'))
        self.assertTrue(response.status_code == 405)

    # TEST REGISTRATION AND LOGIN

    def test_register_and_login(self):
        """Run through process for a new user"""
        # register a new account
        response = self.client.post(url_for('auth.register'), data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'username': 'Waluigi',
            'password': 'walawala',
            'password2': 'walawala',
        })
        self.assertTrue(response.status_code == 302)

        # login with the new account
        response = self.client.post(url_for('auth.login'), data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala'
        }, follow_redirects=True)
        self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))
        if self.app.config['MAIL_USERNAME'] != '':
            self.assertTrue(
                b'You have not confirmed your account yet' in response.data)
        else:
            self.assertTrue(b'confirmed automatically' in response.data)

        # confirm account
        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token),
                                   follow_redirects=True)
        if self.app.config['MAIL_USERNAME'] != '':
            self.assertTrue(
                b'You have confirmed your account' in response.data)
        else:
            self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))

    def test_wrong_email_register(self):
        """Register a non-innocorps account, should fail"""
        response = self.client.post(url_for('auth.register'), data={
            'email': 'wario@nintendo.com',
            'username': 'Wario',
            'password': 'wariotime',
            'password2': 'wariotime',
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Not an allowed email domain' in response.data)

    def test_used_account_register(self):
        """
        If a user puts in a password or username
        that is already used, it should fail
        """
        self.login()

        # try to create it again with same email and username
        response = self.client.post(url_for('auth.register'), data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'username': 'Waluigi',
            'password': 'walawala',
            'password2': 'walawala',
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Username already in use.' in response.data)

    def test_failed_login(self):
        """A user with no account cannot sign in"""
        response = self.client.post(url_for('auth.login'), data={
            'email': 'wario@'+current_app.config['MAIL_DOMAIN'],
            'password': 'waaaario'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Invalid username or password.' in response.data)

    def test_email_and_username_case_insensitivty(self):
        """Checks case-insensitive account email/username"""
        # register a new account
        response = self.client.post(url_for('auth.register'), data={
            'email': 'WaLuIgI@'+current_app.config['MAIL_DOMAIN'],
            'username': 'WaLuIgI',
            'password': 'walawala',
            'password2': 'walawala',
        })
        self.assertEqual(response.status_code, 302)

        # confirm account
        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token),
                                   follow_redirects=True)

        # login with the new account
        response = self.client.post(url_for('auth.login'), data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala'
        }, follow_redirects=True)
        self.assertTrue(re.search(b'Hello,\s+WaLuIgI.', response.data))
        if self.app.config['MAIL_USERNAME'] != '':
            self.assertTrue(
                b'You have not confirmed your account yet' in response.data)
        else:
            self.assertTrue(b'confirmed automatically' in response.data)

        self.logout()

        # register a new account w/ same email; fail
        response = self.client.post(url_for('auth.register'), data={
            'email': 'WALUIGI@'+current_app.config['MAIL_DOMAIN'],
            'username': 'WALUIGI',
            'password': 'walawala',
            'password2': 'walawala',
        })
        self.assertTrue(b'Email already in use.' in response.data)
        self.assertTrue(b'Username already in use.' in response.data)

    # TEST PASSWORD RESET

    def test_email_validation_on_password_reset(self):
        """
        Test the email validator on the reset will throw an
        error if the email cannot be found
        """
        self.login()

        self.logout()

        # user wrong email
        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        token = user.generate_reset_token()
        response = self.client.post(url_for('auth.password_reset',
                                            token=token),
                                    data={
            'email': 'wario@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        })
        self.assertTrue(b'Unknown email address.'in response.data)

        # use correct email
        token2 = user.generate_reset_token()
        response = self.client.post(url_for('auth.password_reset',
                                            token=token2),
                                    data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)
        self.assertTrue(b'Your password has been updated.' in response.data)

    def test_email_validation_on_password_reset_request(self):
        """
        Test the email validator on the reset request will throw an
        error if the email cannot be found
        """
        self.login()

        self.logout()

        # use wrong email
        response = self.client.post(url_for('auth.password_reset_request'),
                                    data={
            'email': 'wario@'+current_app.config['MAIL_DOMAIN'],
        }, follow_redirects=True)
        self.assertTrue(b'Unknown email address.' in response.data)

        # use correct email
        response = self.client.post(url_for('auth.password_reset_request'),
                                    data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)
        if self.app.config['MAIL_USERNAME'] != '':
            self.assertTrue(
                b'email with instructions to reset' in response.data)
        else:
            self.assertTrue(b'cannot reset your password' in response.data)

    def test_reset_password_form(self):
        """Checks the password reset form is working properly"""
        self.login()

        response = self.client.get(url_for('auth.logout'),
                                   follow_redirects=True)
        self.assertTrue(b'You have been logged out' in response.data)

        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        token = user.generate_reset_token()
        response = self.client.post(url_for('auth.password_reset',
                                            token=token),
                                    data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)

        self.assertTrue(b'Your password has been updated.' in response.data)

    def test_reset_password_token_expires(self):
        """Checks password reset fails when token has expired"""
        self.login()

        response = self.client.get(url_for('auth.logout'),
                                   follow_redirects=True)
        self.assertTrue(b'You have been logged out' in response.data)

        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        token = user.generate_reset_token(1)
        time.sleep(2)
        response = self.client.post(url_for('auth.password_reset',
                                            token=token),
                                    data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)

        self.assertTrue(b'The password reset link is invalid or has expired.'
                        in response.data)

    def test_bad_password_reset_token(self):
        """Checks password reset fails with bad token"""
        self.login()

        response = self.client.get(url_for('auth.logout'),
                                   follow_redirects=True)
        self.assertTrue(b'You have been logged out' in response.data)

        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        token = user.generate_reset_token()
        response = self.client.post(url_for('auth.password_reset',
                                            token='bad-token'),
                                    data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)

        self.assertTrue(b'The password reset link is invalid or has expired.'
                        in response.data)

    # TEST ACCOUNT CONFIRMATION

    def test_confirmed_redirects(self):
        """
        Test that some auth functions redirect to main page
        if already signed in
        """
        self.login()

        response = self.client.get(url_for('auth.unconfirmed'),
                                   follow_redirects=True)
        self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))

        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token),
                                   follow_redirects=True)
        self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))

        token2 = user.generate_reset_token()
        response = self.client.get(url_for('auth.password_reset',
                                           token=token2),
                                   follow_redirects=True)
        self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))

        response = self.client.get(url_for('auth.oauth_authorization',
                                           provider='google'),
                                   follow_redirects=True)
        self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))

        response = self.client.get(url_for('auth.oauth_callback',
                                           provider='google'),
                                   follow_redirects=True)
        self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))

    def test_invalid_confirmation_token(self):
        """Test invalid conf token will not work"""
        response = self.client.post(url_for('auth.register'), data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'username': 'Waluigi',
            'password': 'walawala',
            'password2': 'walawala',
        })

        response = self.client.post(url_for('auth.login'), data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala'
        }, follow_redirects=True)
        self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))

        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm',
                                           token='wrong-token'),
                                   follow_redirects=True)
        if self.app.config['MAIL_USERNAME'] != '':
            self.assertTrue(b'The confirmation link is invalid or has expired'
                            in response.data)
        else:
            self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))

    def test_resend_confirmation_token(self):
        """Checks the email can be sent again"""
        response = self.client.post(url_for('auth.register'), data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'username': 'Waluigi',
            'password': 'walawala',
            'password2': 'walawala',
        })

        response = self.client.post(url_for('auth.login'), data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala'
        }, follow_redirects=True)
        self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))

        response = self.client.get(url_for('auth.resend_confirmation'),
                                   follow_redirects=True)
        self.assertTrue(b'A new confirmation token has been sent to you'
                        in response.data)

    # TEST CHANGE PASSWORD

    def test_change_password(self):
        """Test the change password function is working properly"""
        self.login()

        response = self.client.post(url_for('auth.change_password'), data={
            'old_password': 'walawala',
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)
        self.assertTrue(b'Your password has been updated' in response.data)

    def test_change_password_wrong_password(self):
        """Test that change password fails with wrong old password"""
        self.login()

        response = self.client.post(url_for('auth.change_password'), data={
            'old_password': 'waaaaaalaaaaa',
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)
        self.assertTrue(b'Invalid password.' in response.data)

    def test_change_password_missing_password(self):
        """Test that the webpage catches if data is missing"""
        self.login()

        response = self.client.post(url_for('auth.change_password'), data={
            'old_password': 'walawala',
            'password': 'walawala2',
        }, follow_redirects=True)
        self.assertTrue(b'This field is required' in response.data)

    # TEST GOOGLE ACCOUNT

    def test_email_associated_with_google(self):
        """
        If a user signs up with google, the password field will be empty,
        so app passwords must be set.
        """
        self.login()

        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        user.password_hash = None  # Simulate password_hash missing
        db.session.add(user)
        db.session.commit()

        response = self.client.post(url_for('auth.login'), data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala'
        }, follow_redirects=True)
        self.assertTrue(b'Invalid username or password', response.data)

    def test_change_password_works_with_google_login(self):
        """The change password should still work if a google account is used"""
        self.login()

        response = self.client.post(url_for('auth.change_password'), data={
            'old_password': 'walawala',
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)
        self.assertTrue(b'Your password has been updated' in response.data)

        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        user.password_hash = None  # Simulate password_hash missing
        db.session.add(user)
        db.session.commit()

        response = self.client.post(url_for('auth.change_password'), data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN']
        }, follow_redirects=True)
        self.assertTrue(b'You have not set an app password yet!' in response.data)

    def test_email_validation_on_set_app_password(self):
        """
        Test the email validator on the set app password will throw an
        error if the email cannot be found.
        """
        self.login()

        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        user.password_hash = None  # Simulate password_hash missing
        db.session.add(user)
        db.session.commit()

        self.logout()

        # user wrong email
        token = user.generate_reset_token()
        response = self.client.post(url_for('auth.set_app_password',
                                            token=token),
                                    data={
            'email': 'wario@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        })
        self.assertTrue(b'Unknown email address.'in response.data)

        # use correct email
        token2 = user.generate_reset_token()
        response = self.client.post(url_for('auth.set_app_password',
                                            token=token2),
                                    data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)
        self.assertTrue(b'Your app password has been set.' in response.data)

    def test_email_validation_on_set_app_password_request(self):
        """
        Test the email validator on the set app password request will throw an
        error if the email cannot be found.
        """
        self.login()

        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        user.password_hash = None  # Simulate password_hash missing
        db.session.add(user)
        db.session.commit()

        # use wrong email
        response = self.client.post(url_for('auth.set_app_password_request'),
                                    data={
            'email': 'wario@'+current_app.config['MAIL_DOMAIN'],
        }, follow_redirects=True)
        self.assertTrue(b'Unknown email address.' in response.data)

        # use correct email
        response = self.client.post(url_for('auth.set_app_password_request'),
                                    data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)
        if self.app.config['MAIL_USERNAME'] != '':
            self.assertTrue(
                b'An email with instructions to set your app password' in response.data)
        else:
            self.assertTrue(b'cannot reset your password' in response.data)

    def test_set_app_password_form(self):
        """Checks the set app password form is working properly"""
        self.login()

        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        user.password_hash = None  # Simulate password_hash missing
        db.session.add(user)
        db.session.commit()

        self.logout()

        token = user.generate_reset_token()
        response = self.client.post(url_for('auth.set_app_password',
                                            token=token),
                                    data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)

        self.assertTrue(b'Your app password has been set.' in response.data)

    def test_set_app_password_token_expires(self):
        """Checks set app password fails when token has expired"""
        self.login()

        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        user.password_hash = None  # Simulate password_hash missing
        db.session.add(user)
        db.session.commit()

        self.logout()

        token = user.generate_reset_token(0.5)
        time.sleep(1)
        response = self.client.post(url_for('auth.set_app_password',
                                            token=token),
                                    data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)

        self.assertTrue(b'The set app password link is invalid or has expired.'
                        in response.data)

    def test_bad_set_app_password_token(self):
        """Checks set app password failure with bad token"""
        self.login()

        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        user.password_hash = None  # Simulate password_hash missing
        db.session.add(user)
        db.session.commit()

        self.logout()

        token = user.generate_reset_token()
        response = self.client.post(url_for('auth.set_app_password',
                                            token='bad-token'),
                                    data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)

        self.assertTrue(b'The set app password link is invalid or has expired.'
                        in response.data)

    def test_set_app_password_redirect(self):
        """Checks for redirect if user isn't logged out"""
        self.login()

        # Don't Simulate password_hash missing
        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        token = user.generate_reset_token()
        response = self.client.post(url_for('auth.set_app_password',
                                            token=token),
                                    data={
            'email': 'waluigi@'+current_app.config['MAIL_DOMAIN'],
            'password': 'walawala2',
            'password2': 'walawala2'
        }, follow_redirects=True)
        self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))

    def test_set_app_password_request_redirect(self):
        """Checks for redirect if user already has an app password"""
        self.login()

        # Don't Simulate password_hash missing
        user = User.query.filter_by(email='waluigi@'+current_app.config['MAIL_DOMAIN']).first()
        token = user.generate_reset_token()
        response = self.client.post(url_for('auth.set_app_password_request'),
                                    data={
            'email': 'wario@'+current_app.config['MAIL_DOMAIN'],
        }, follow_redirects=True)
        self.assertTrue(re.search(b'Hello,\s+Waluigi.', response.data))

    # TEST OAUTH

    def test_oauth_intialization(self):
        """Checks that the function will eventually route to google"""
        response = self.client.get(url_for('auth.oauth_authorization',
                                           provider='google'))
        self.assertTrue(b'accounts.google.com' in response.data)

    def test_oauth_missing_provider(self):
        """Checks self.providers action if it is not None"""
        response = self.client.get(url_for('auth.oauth_authorization',
                                           provider='google'))
        self.assertTrue(b'accounts.google.com' in response.data)

    def test_oauth_callback_missing_email(self):
        """Check that oauth callback fails without email"""
        response = self.client.get(url_for('auth.oauth_callback',
                                           provider='google'),
                                   follow_redirects=True)
        self.assertTrue(b'Authentication failed.' in response.data)

    # TEST JSON POST TO WEBPAGE

    def test_json_post_unique_accountant_id_error(self):
        """Check error is thrown if datetime is aready in the database"""
        self.login()
        data = {}
        data['json_message'] = self.EXAMPLE_COMPACT_JSON_MESSAGE
        response = self.client.post(
            url_for('main.manual_json_post'), data=data)
        response = self.client.post(
            url_for('main.manual_json_post'), data=data)
        self.assertTrue(
            b'There was a unique constraint error' in response.data)
