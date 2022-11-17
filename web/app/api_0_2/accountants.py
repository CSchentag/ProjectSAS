"""api endpoints"""
import cProfile
import pstats
import io
import sqlalchemy
import json
from sqlalchemy import desc
from datetime import datetime, timedelta
from flask import jsonify, request, url_for, current_app
from flask_sqlalchemy import get_debug_queries
from redis import RedisError
from .. import db, cache, watchdog, celery
from . import api_0_2
#from .errors import not_acceptable, bad_request, too_many_requests, server_error
from ..accepted_json_message import ACCEPTED_JSON
from ..models import Accountants, User

@api_0_2.after_request
def after_request(response):
    """
    Logs queries that took a long time
    https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-debugging-testing-and-profiling
    """
    for query in get_debug_queries():
        if query.duration >= current_app.config['SQLALCHEMY_DATABASE_QUERY_TIMEOUT']:
            current_app.logger.warning(
                f"SLOW SQL QUERY: {query.statement} PARAMETERS: {query.parameters} DURATION: {query.duration}s CONTEXT: {query.context}")
    return response

@api_0_2.route('/accountants/')
def get_accountants():
    """
    Get all posts in the database.

    Returns:
        jsonify

    .. :quickref: All Data; Get all data

    **Example request**:

    Shell command:

    *with email/password:*

    .. sourcecode:: shell

        curl --user <email>:<password> -X GET https://localhost/api/v0.1/posts/

    *with token:*

    .. sourcecode:: shell

        curl --user <token>: -X GET https://localhost/api/v0.1/posts/

    Command response:

    .. sourcecode:: http

        GET /api/v0.1/posts/ HTTP/1.1
        Host: localhost
        Authorization: Basic <b64 encoded email:password or token:>

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "count": 127,
            "next": "http://localhost/api/v0.1/posts/?page=2",
            "prev": null,
            "data": [
                {
                "datetime": "2017-08-17T21:27:34Z",
                "sensor_1": "10.0"
                }
                ]
            }

    *(JSON cut for length)*

   :reqheader Authorization: use cURL tag with <email>:<psswrd>, or <token>:
   :resheader Content-Type: application/json
   :statuscode 200: Successfully retrieved data
   :statuscode 401: Invalid credentials
   :statuscode 403: Not signed in

    """
    query_result_list = [accountant.to_json() for accountant in Accountants.query]
    for query_result in query_result_list:
        # this is for the sake of unique URLs in the frontend
        query_result['username'] = (query_result['email']).split('@')[0]
    data = {'data': query_result_list}
    return jsonify(data)


@api_0_2.route('/accountants/<username>', methods=['GET'])
def get_accountant_info(username):
    accountant = Accountants.query.filter(Accountants.email.contains(username)).first()
    json_data = accountant.to_json()
    json_data['username'] = (json_data['email']).split('@')[0]
    data = {'data': json_data}
    return jsonify(data)

