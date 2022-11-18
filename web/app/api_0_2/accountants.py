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

