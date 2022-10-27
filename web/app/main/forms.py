"""Creates HTML webforms, using WTForms"""
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, BooleanField, EmailField, TelField, StringField
from wtforms.validators import DataRequired
from ..models import Accountants


class JSONForm(FlaskForm):
    """
    JSONForm is a single box HTML Form used to send user
    messages to other parts of the app

    Attributes:
        json_message (obj): Allows user to input message into a TextAreaField.
        submit (obj): Takes the message from the TextAreaField and relays it.
    """
    json_message = TextAreaField("JSON Message", validators=[DataRequired()])
    submit = SubmitField('Submit')


class SearchEnableForm(FlaskForm):
    search_enable = BooleanField(
        "Enable search (disables table auto-update)",
        default=False)
    submit = SubmitField('Submit')


class AddAccountantForm(FlaskForm):
    """
    AddAccountantForm is a multi-box HTML Form used to
    add a new Accountant datafile to the database.

    Attribtues:

    """
    name = StringField('Full Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    phone_num = TelField('Phone Number', validators=[DataRequired()])
    company = StringField('Company', validators=[DataRequired()])
    specialty = StringField('Specialty', validators=[DataRequired()])
    about_me = StringField('About')
    submit = SubmitField('Submit')

    """
    def validate_phone_num(self, phone_num):
        accountant = Accountants.query.filter_by(phone_num=phone_num.data).first()
        if accountant is not None:
            raise ValidationError('The phone number is already in use. Please use another.')

    def validate_email(self, email):
        accountant = Accountants.query.filter_by(email=email.data).first()
        if accountant is not None:
            raise ValidationError('The email is already in use. Please use another. ')
    """