from flask import Blueprint, request, abort, current_app, url_for
from werkzeug.http import dump_cookie
from apifairy import authenticate, body, response, other_responses

from . import api_0_2
from .. import db
from .auth import basic_auth
from ..email import send_email
from ..models import User, Token
from .schemas import TokenSchema, PasswordResetRequestSchema, \
    PasswordResetSchema, EmptySchema

token_schema = TokenSchema()


def token_response(token):
    headers = {}
    if current_app.config['REFRESH_TOKEN_IN_COOKIE']:
        samesite = 'Strict'
        if current_app.config['USE_CORS']:  # pragma: no branch
            samesite = None if not current_app.debug else 'Lax'
        headers['Set-Cookie'] = dump_cookie(
            'refresh_token', token.refresh_token,
            path=url_for('api_0_2.new'), secure=not current_app.debug,
            httponly=True, samesite=samesite)
    return {
        'access_token': token.access_token,
        'refresh_token': token.refresh_token
        if current_app.config['REFRESH_TOKEN_IN_BODY'] else None,
    }, 200, headers


@api_0_2.route('/tokens', methods=['POST'])
@authenticate(basic_auth)
@response(token_schema)
@other_responses({401: 'Invalid username or password'})
def new():
    """Create new access and refresh tokens
    The refresh token is returned in the body of the request or as a hardened
    cookie, depending on configuration. A cookie should be used when the
    client is running in an insecure environment such as a web browser, and
    cannot adequately protect the refresh token against unauthorized access.
    """
    user = basic_auth.current_user()
    token = user.generate_auth_token()
    db.session.add(token)
    Token.clean()  # keep token table clean of old tokens
    db.session.commit()
    return token_response(token)


@api_0_2.route('/tokens', methods=['PUT'])
@body(token_schema)
@response(token_schema, description='Newly issued access and refresh tokens')
@other_responses({401: 'Invalid access or refresh token'})
def refresh(args):
    """Refresh an access token
    The client has the option to pass the refresh token in the body of the
    request or in a `refresh_token` cookie. The access token must be passed in
    the body of the request.
    """
    access_token = args['access_token']
    refresh_token = args.get('refresh_token', request.cookies.get(
        'refresh_token'))
    print(request.headers)
    if not access_token or not refresh_token:
        abort(401)
    token = User.verify_refresh_token(refresh_token, access_token)
    if not token:
        abort(401)
    token.expire()
    new_token = token.user.generate_auth_token()
    db.session.add_all([token, new_token])
    db.session.commit()
    return token_response(new_token)


@api_0_2.route('/tokens', methods=['DELETE'])
@response(EmptySchema, status_code=204, description='Token revoked')
@other_responses({401: 'Invalid access token'})
def revoke():
    """Revoke an access token"""
    access_token = request.headers['Authorization'].split()[1]
    token = Token.query.filter_by(access_token=access_token).first()
    if not token:  # pragma: no cover
        abort(401)
    token.expire()
    db.session.commit()
    return {}


@api_0_2.route('/tokens/reset', methods=['POST'])
@body(PasswordResetRequestSchema)
@response(EmptySchema, status_code=204,
          description='Password reset email sent')
def reset(args):
    """Request a password reset token"""
    user = User.query.filter_by(email=args['email']).first()
    if user is not None:
        reset_token = user.generate_reset_token()
        reset_url = current_app.config['PASSWORD_RESET_URL'] + \
            '?token=' + reset_token
        send_email(args['email'], 'Reset Your Password', 'auth/email/reset',
                   token=reset_token, username=user.username, url=reset_url)
    return {}


@api_0_2.route('/tokens/reset', methods=['PUT'])
@body(PasswordResetSchema)
@response(EmptySchema, status_code=204,
          description='Password reset successful')
@other_responses({400: 'Invalid reset token'})
def password_reset(args):
    """Reset a user password"""
    user = User.verify_reset_token(args['token'])
    if user is None:
        abort(400)
    user.password = args['new_password']
    db.session.commit()
    return {}