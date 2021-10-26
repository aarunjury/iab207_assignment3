import re
from flask import flash
from bookings.models import EventGenre, EventCity, EventStatus
from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, BooleanField, DecimalField, SelectField, IntegerField, DateTimeField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import InputRequired, Length, Email, EqualTo, NumberRange, Regexp, ValidationError
from wtforms_validators import Alpha
from flask_wtf.file import FileRequired, FileField, FileAllowed

ALLOWED_FILE = {'PNG', 'JPG', 'JPEG', 'jpeg', 'png', 'jpg'}

# Unlike the built-in Length validator, this will remove whitespace when counting length
# to prevent users from creating Events with properties that are all or mostly whitespace
def check_field_length(form, field):
    field = field.data.strip()
    if len(field) < 5:
        #flash("Your entry was too short! Must be 5 or more characters (not including spaces)", 'warning')
        raise ValidationError('Your entry was too short! Must be 5 or more characters (not including spaces)')


class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[
                        InputRequired(message='Your event must have a title'), Length(min=3, max=50, message='Title must be between 4 and 50 characters'), check_field_length])
    date = DateTimeLocalField('Date and Time', format='%Y-%m-%dT%H:%M', validators=[
        InputRequired(message='Must be in the format: dd/mm/yyyy HH:MM')])
    headliner = StringField('Headlining Artist', validators=[
        InputRequired(message='Your event must have a headlining artist'), Length(min=1, max=40, message='Headliner cannot be more than 40 characters'), check_field_length])
    venue = StringField('Venue', validators=[
                        InputRequired(message='Your event must have a venue'), Length(min=1, max=40, message='Venue Name cannot be more than 40 characters'), check_field_length])
    desc = TextAreaField('Event Description', validators=[
                         InputRequired(message='Your event must have a description'), Length(max=700, message='Event Description cannot be more than 700 characters.'), check_field_length])
    image = FileField('Event Image', validators=[
        FileRequired(message='Image cannot be empty'),
        FileAllowed(ALLOWED_FILE, message='Only supports png,jpg,JPG,PNG')])
    total_tickets = IntegerField(
        'Total Number of Tickets', validators=[InputRequired(message='You must select how many tickets are available for purchase.'), NumberRange(min=1, max=99999, message='Tickets must be between 1 and 99999')])
    price = DecimalField('Cost per ticket: $', validators=[InputRequired(message='You must choose a price per ticket.'), NumberRange(
        min=0.01, max=999.99, message='Price must be between $1.00 and $999.99')])
    event_genre = SelectField('Choose a genre:', choices=[
                              e.name.title() for e in EventGenre], validators=[InputRequired(message='Your event must have a genre')])
    event_city = SelectField('Choose a city:', choices=[
                             e.name.title() for e in EventCity], validators=[InputRequired(message='Your event must have a city it is located in')])
    submit = SubmitField('Create Event')


class EditEventForm(FlaskForm):
    title = StringField('Event Title', validators=[
                        Length(min=3, max=50, message='Title cannot be more than 40 characters')])
    date = DateTimeLocalField('Date and Time', format='%Y-%m-%dT%H:%M')
    headliner = StringField('Headlining Artist', validators=[Length(
        min=1, max=40, message='Headliner cannot be more than 40 characters')])
    venue = StringField('Venue')
    desc = TextAreaField('Event Description', validators=[
                         Length(max=700, message='Event Description cannot be more than 700 characters.')])
    image = FileField('Event Image', validators=[FileAllowed(
        ALLOWED_FILE, message='Only supports png,jpg,JPG,PNG')])
    total_tickets = IntegerField(
        'Total Number of Tickets', validators=[NumberRange(min=1, max=99999, message='Tickets must be between 1 and 99999')])
    price = DecimalField('Cost per ticket: $', validators=[NumberRange(
        min=0.01, max=999.99, message='Price must be between $0.01 and $999.99')])
    event_status = SelectField('Choose a status:', choices=[
                               e.name.title() for e in EventStatus])
    event_genre = SelectField('Choose a genre:', choices=[
                              e.name.title() for e in EventGenre])
    event_city = SelectField('Choose a city:', choices=[
                             e.name.title() for e in EventCity])
    submit = SubmitField('Update Event')


class CommentForm(FlaskForm):
    text = TextAreaField('Leave a Comment:', validators=[
                         InputRequired(message="Your comment can't be blank"), check_field_length])
    submit = SubmitField('Submit')


class BookingForm(FlaskForm):
    tickets_required = IntegerField(
        'How many tickets would you like to book?', default='1', validators=[InputRequired()])

    # def validate_tickets_required(form, field):
    #     if not re.match('^[0-9]+$', str(field.data)):
    #         raise ValidationError('Only whole numbers allowed')
    submit = SubmitField('Confirm Booking')


class LoginForm(FlaskForm):
    user_name = StringField("User Name", validators=[
        InputRequired('Enter user name')])
    password = PasswordField("Password", validators=[
        InputRequired('Enter user password')])
    remember = BooleanField("Remember me?",
                            default=True)
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    user_name = StringField("User Name", validators=[InputRequired(), Alpha(message='Can only contain alphabetical characters'), Length(
        min=4, max=25, message='Username must be between 4 and 25 characters')])
    email_id = StringField("Email Address", validators=[
        Email("Please enter a valid email")])
    # linking two fields - password should be equal to data entered in confirm
    password = PasswordField("Password", validators=[InputRequired(),
                                                     EqualTo('confirm', message="Passwords don't match!")])
    confirm = PasswordField("Confirm Your Password")
    phone = StringField('Mobile Number', validators=[InputRequired(), Regexp(
        '^04[0-9]{8}$', message='Must be a 10 digit number starting with 04')])
    street_no = StringField('Street No.', validators=[InputRequired(), Regexp(
        '^[0-9/]{1,9}$', message="Up to 8 numbers and a '/' allowed only")])
    street_name = StringField('Street Name', validators=[InputRequired()])
    state = SelectField('State', choices=[('QLD'), ('NSW'), ('VIC'), (
        'ACT'), ('NT'), ('TAS'), ('SA'), ('WA')], validators=[InputRequired()])
    # chosen str instead of int here to use the length validator
    postcode = StringField('Postcode', validators=[
                           InputRequired(), Regexp('^[0-9]{4}$', message='Must be a 4 digit number')])
    # submit button
    submit = SubmitField("Register")
