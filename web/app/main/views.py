"""Takes JSON files from all the sensors and also shows it on the website"""

# pylint: disable=invalid-name
# pylint: disable=superfluous-parens
# pylint: disable=no-member
import json
import sqlalchemy
from sqlalchemy import desc
from flask import request, render_template, current_app, redirect, flash, jsonify
from flask_login import login_required
from redis import RedisError
from .forms import JSONForm, SearchEnableForm, AddAccountantForm
from . import main
from .. import db, cache, watchdog
from ..accepted_json_message import ACCEPTED_JSON
from ..models import Accountants


@main.route('/')
def index():
    """
    Sets up homepage

    Returns:
        render_template using index.html to set up the webpage
    """
    return render_template('index.html')


@main.route("/viewdata", methods=['GET', 'POST'])
@login_required
def show_Accountants():
    """
    Outputs all Accounts data to an Ajax rendered table.

    Returns:
        render_template, which allows a user to view the data
        via a javascript table.
    """
    return render_template('ajaxtable.html', title="Ajax Table")


@main.route("/api/data", methods=['GET', 'POST'])
@login_required
def accountant_data():
    data = {'data': [accountant.to_json() for accountant in Accountants.query]}
    return jsonify(data)


@main.route("/addaccountant", methods=['GET', 'POST'])
@login_required
def add_accountant_post():
    """
    Put data in database via Form

    Returns:
        render_template which puts all the data in the
        website database via accountant_form_post.html.
    """
    form = AddAccountantForm()
    if form.validate_on_submit():
        accountant = Accountants(name=form.name.data,
                                email=form.email.data,
                                phone_num=form.phone_num.data,
                                company=form.company.data,
                                specialty = form.specialty.data,
                                about_me = form.about_me.data)
        try:
            db.session.add(accountant)
            db.session.commit()
            flash("The user has been added to the database.")
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            flash("There was an error adding the user to the database - the email or phone number is already in use.")
    return render_template('accountant_form_post.html', form=form)


@main.route("/manualjsonpostdata", methods=['GET', 'POST'])
@login_required
def manual_json_post():
    """
    Put data in database via JSON

    Returns:
        render_template which puts all the data in the website
        database via json_post.html.
    """
    form = JSONForm()
    is_dict = None
    dict_error = None
    if request.method == 'POST':
        parsed_dict = json_post_to_dict(form)
        if parsed_dict is None:
            dict_error = "JSON message was improperly formatted."
            is_dict = False
            current_app.logger.warning('JSON Form Message '
                                       'Exception: %s', dict_error)
            return render_template('json_post.html',
                                   form=form,
                                   is_dict=is_dict,
                                   error=dict_error)

        json_post = Accountants.flatten(parsed_dict)
        flattened_accepted_json = Accountants.flatten(ACCEPTED_JSON)
        data = Accountants.from_json(json_post)
        to_json_data = data.to_json()

        try:
            db.session.add(data)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            is_dict = False
            dict_error = (
                "There was a unique constraint error,"
                " this id already appears in the database.")
            return render_template('json_post.html',
                                   form=form,
                                   is_dict=is_dict,
                                   error=dict_error)

        dict_error = None
        is_dict = True
        return render_template('json_post.html',
                               form=form,
                               is_dict=is_dict,
                               error=dict_error)

    return render_template('json_post.html',
                           form=form,
                           is_dict=is_dict,
                           error=dict_error)


def json_post_to_dict(form):
    """
    Takes the JSONs out of the messy HTML format and
    splits them into individual dicts.

    Args:
        form: the JSON data.

    Returns:
        parsed_dicts which further organizes and seperates the flattened JSON.
    """
    message = str(form.json_message.data)
    try:
        dict_post = json.loads(message)
    except json.decoder.JSONDecodeError as e:
        print("json_post_to_dict: json decoder failed to parse message")
        print(e)
        return None
    return dict_post
