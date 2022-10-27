"""Takes JSON files from all the sensors and also shows it on the website"""

# pylint: disable=invalid-name
# pylint: disable=superfluous-parens
# pylint: disable=no-member
import json
import sqlalchemy
from sqlalchemy import desc
from flask import request, render_template, current_app
from flask_login import login_required
from redis import RedisError
from .forms import JSONForm, SearchEnableForm
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
def show_Accountants_data():
    """
    Outputs all Accountants post table data to an HTML table

    Returns:
        render_template, which allows a user to view all the data on
        the website via viewdata.html.
    """
    accountants_columns = Accountants.__table__.columns.keys()  # Grabs column headers
    page = request.args.get('page', 1, type=int)
    pagination = db.session.query(Accountants).order_by(desc(Accountants.name)).paginate(  # paginates response
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    page_items = pagination.items
    # need to convert the sql query to something iterable in the table
    # no coverage here but is tested via same function in api_0_1.Accountants_post
    dict_list = []
    for item in page_items:
        d = {}
        for column in item.__table__.columns:
            d[column.name] = str(getattr(item, column.name))
        dict_list.append(d)
    data = []
    for item in dict_list:
        data.append(list((item).values()))
    accountants = Accountants.query
    return render_template('viewdata.html', accountants=accountants)


@main.route("/manualjsonpostdata", methods=['GET', 'POST'])
@login_required
def manual_json_post():
    """
    Put data in database via JSON

    Returns:
        render_template which puts all the data in the website
        database via json_pot.html.
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
