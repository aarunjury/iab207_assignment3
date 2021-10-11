from sqlalchemy.sql.sqltypes import Float
from bookings.models import EventGenre, EventCity, EventStatus
from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, BooleanField, DateTimeField
from wtforms.fields.core import FloatField, SelectField
from wtforms.fields.html5 import TelField, IntegerField
from wtforms.validators import InputRequired, Length, Email, EqualTo, NumberRange
from flask_wtf.file import FileRequired, FileField, FileAllowed

ALLOWED_FILE = {'PNG', 'JPG', 'JPEG', 'jpeg', 'png', 'jpg'}


class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[
                        InputRequired(message='Your event must have a title'), Length(max=40)])
    date = DateTimeField('Date and Time', format='%d/%m/%Y %H:%M', validators=[
                         InputRequired(message='Must be in the format: dd/mm/yyyy HH:MM')])
    headliner = StringField('Headlining Artist', validators=[
        InputRequired(message='Your event must have a headlining artist')])
    venue = StringField('Venue', validators=[
                        InputRequired(message='Your event must have a venue')])
    desc = TextAreaField('Event Description', validators=[
                         InputRequired(message='Your event must have a description'), Length(max=700, message='Event Description cannot be more than 700 characters.')])
    image = FileField('Event Image', validators=[
        FileRequired(message='Image cannot be empty'),
        FileAllowed(ALLOWED_FILE, message='Only supports png,jpg,JPG,PNG')])
    total_tickets = StringField(
        'Total Number of Tickets', validators=[InputRequired(message='You must select how many tickets are available for purchase.')])
    price = FloatField('Cost per ticket: $', validators=[InputRequired(message='You must choose a price per ticket.'), NumberRange(
        min=0.01, max=999.99, message='Must include dollars and cents')])
    event_genre = SelectField('Choose a genre:', choices=[
                              e.name.title() for e in EventGenre], validators=[InputRequired(message='Your event must have a genre.')])
    event_city = SelectField('Choose a city:', choices=[
                             e.name.title() for e in EventCity], validators=[InputRequired(message='Your event must have a city it is located in.')])
    submit = SubmitField('Create Event')


class EditEventForm(FlaskForm):
    title = StringField('Event Title', validators=[Length(max=40)])
    date = DateTimeField('Date and Time', format='%d/%m/%Y %H:%M')
    headliner = StringField('Headlining Artist')
    venue = StringField('Venue')
    desc = TextAreaField('Event Description', validators=[Length(max=700)])
    image = FileField('Event Image', validators=[FileAllowed(
        ALLOWED_FILE, message='Only supports png,jpg,JPG,PNG')])
    total_tickets = StringField(
        'Total Number of Tickets')
    price = FloatField('Cost per ticket:', validators=[NumberRange(
        min=0.01, max=999.99, message='Must include dollars and cents')])
    event_status = SelectField('Choose a status:', choices=[
                               e.name.title() for e in EventStatus])
    event_genre = SelectField('Choose a genre:', choices=[
                              e.name.title() for e in EventGenre])
    event_city = SelectField('Choose a city:', choices=[
                             e.name.title() for e in EventCity])
    submit = SubmitField('Update Event')


class CommentForm(FlaskForm):
    text = TextAreaField('Leave a Comment:', validators=[
                         InputRequired(message="Your comment can't be blank")])
    submit = SubmitField('Submit')


class BookingForm(FlaskForm):
    tickets_required = IntegerField(
        'How many tickets would you like to book?', default='1', validators=[InputRequired()])
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
    user_name = StringField("User Name", validators=[InputRequired()])
    email_id = StringField("Email Address", validators=[
        Email("Please enter a valid email")])
    # linking two fields - password should be equal to data entered in confirm
    password = PasswordField("Password", validators=[InputRequired(),
                                                     EqualTo('confirm', message="Passwords don't match!")])
    confirm = PasswordField("Confirm Your Password")
    phone = TelField('Mobile Number', validators=[InputRequired()])
    street_no = IntegerField('Street No.', validators=[InputRequired()])
    street_name = StringField('Street Name', validators=[InputRequired()])
    state = SelectField('State', choices=[('QLD'), ('NSW'), ('VIC'), (
        'ACT'), ('NT'), ('TAS'), ('SA'), ('WA')], validators=[InputRequired()])
    # chosen str instead of int here to use the length validator
    postcode = StringField('Postcode', validators=[
                           InputRequired(), Length(min=4, max=4)])
    # submit button
    submit = SubmitField("Register")
