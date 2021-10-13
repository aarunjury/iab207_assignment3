from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login.utils import login_required
from .models import Event, Comment, EventCity, EventGenre, EventStatus, Booking
from .forms import EditEventForm, EventForm, CommentForm, BookingForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import current_user

eventbp = Blueprint('events', __name__, url_prefix='/events')


def is_current_user():
    if current_user.name == 'Guest':
        name = 'Guest'
    else:
        name = current_user.name
    return name

@eventbp.route('/<id>')
def show(id):
    event = Event.query.filter_by(id=id).first()
    # create the comment form
    comments_form = CommentForm()
    form = BookingForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    name = is_current_user()
    events = Event.query.all()
    artist_events = Event.query.filter_by(headliner=event.headliner).all()  
    genres = EventGenre
    cities = EventCity
    return render_template('events/event_details.html', event=event, form=comments_form, booking_form=form, username=name, events_list=events, artist_events=artist_events, genres=genres, cities=cities)


@eventbp.route('/view_all')
def view_all_events():
    name = is_current_user()
    events_list_all = Event.query.all()
    genres = EventGenre
    cities = EventCity
    return render_template('events/view_events.html', cities=cities, username=name, heading='All Events', events=events_list_all, genres=genres, events_list=events_list_all)


@eventbp.route('/view_all/<genre>')
def view_events(genre):
    genre = genre.upper()
    genre_events_list = Event.query.filter_by(event_genre=genre).all()
    name = is_current_user()
    events_list_all = Event.query.all()
    genres = EventGenre
    cities = EventCity
    return render_template('events/view_events.html', cities=cities, username=name, heading=genre, events=genre_events_list, genres=genres, events_list=events_list_all)


@eventbp.route('/view_all/city/<city_name>')
def view_events_city(city_name):
    city_name = city_name.upper()
    city_events = Event.query.filter_by(event_city=city_name).all()
    name = is_current_user()
    events_list_all = Event.query.all()
    genres = EventGenre
    cities = EventCity
    return render_template('events/view_events.html', cities=cities, username=name, heading=city_name, events=city_events, genres=genres, events_list=events_list_all)


@eventbp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    print('Method type: ', request.method)
    form = EventForm()
    if form.validate_on_submit():
        # call the function that checks and returns image
        db_file_path = check_upload_file(form)
        event = Event(title=form.title.data, date=form.date.data, headliner=form.headliner.data, venue=form.venue.data, description=form.desc.data,
                      image=db_file_path, total_tickets=form.total_tickets.data, tickets_remaining=form.total_tickets.data, price=form.price.data, event_status=EventStatus(
                          1).name,
                      event_genre=form.event_genre.data.upper(), event_city=form.event_city.data.upper(), created_on=datetime.now(), user_id=current_user.id)
        # add the object to the db session
        db.session.add(event)
        # commit to the database
        db.session.commit()
        flash('Successfully created new event')
        print('Successfully created new event')
        # Always end with redirect when form is valid
        return redirect(url_for('main.my_events'))
    else:
        print('something wrong')
    events_list = Event.query.all()
    genres = EventGenre
    cities = EventCity
    return render_template('events/create_event.html', cities=cities, event_form=form, username=current_user.name, events_list=events_list, genres=genres)


@eventbp.route('/<id>/update', methods=['GET', 'POST'])
@login_required
# Should first pull a list of the logged in user's events and check that they
# created the event before letting them edit it (due to url-jacking).
def update_event(id):
    form = EditEventForm()
    event_old = Event.query.get(id)
    event = Event.query.get(id)
    form.title.description = event_old.title
    form.date.description = event_old.date.strftime('%d/%m/%Y %H:%M')
    form.headliner.description = event_old.headliner
    form.venue.description = event_old.venue
    form.desc.description = event_old.description
    form.total_tickets.description = event_old.total_tickets
    form.price.description = event_old.price
    if form.validate_on_submit():
        tickets_booked = 0
        # call the function that checks and returns image
        db_file_path = check_upload_file(form)
        # Event.query.filter_by(id=id).update(
        #         {'tickets_remaining': event.tickets_remaining-form.tickets_required.data, 'tickets_booked': event.tickets_booked+form.tickets_required.data}, synchronize_session='evaluate')
        event.title = form.title.data
        event.date = form.date.data
        event.headliner = form.headliner.data
        event.venue = form.venue.data
        event.description = form.desc.data
        event.image = db_file_path
        event.total_tickets = int(form.total_tickets.data)
        # minus sum of tickets_booked where event_id in bookings=event.id
        for booking in Booking.query.filter_by(event_id=id):
            tickets_booked += booking.tickets_booked
        # This next line does not prevent negative remaining tickets
        event.tickets_remaining = event.total_tickets - tickets_booked
        event.price = form.price.data
        event.event_status = form.event_status.data.upper()
        event.event_genre = form.event_genre.data.upper()
        event.event_city = form.event_city.data.upper()
        # # commit to the database
        db.session.commit()
        flash('Successfully updated event!')
        # Always end with redirect when form is valid
        return redirect(url_for('main.my_events'))
    else:
        print('something wrong')
        #flash('Something went wrong')
    events_list = Event.query.all()
    genres = EventGenre
    cities = EventCity
    return render_template('events/edit_event.html', cities=cities, event_form=form, event=event, username=current_user.name, events_list=events_list, genres=genres)


@eventbp.route('/<id>/delete', methods=['GET', 'POST'])
@login_required
def delete_event(id):
    # Delete the event from the database
    Event.query.filter_by(id=id).delete()
    # Delete any associated bookings
    # (should also delete the comments to save disk space)
    Booking.query.filter_by(event_id=id).delete()
    db.session.commit()
    return redirect(url_for('main.my_events'))


@eventbp.route('/<id>/comment', methods=['GET', 'POST'])
@login_required
def comment(id):
    form = CommentForm()
    # get the Event object associated to the page and the comment
    event = Event.query.filter_by(id=id).first()
    if form.validate_on_submit():
        # Create the Comment object using the form data
        comment = Comment(text=form.text.data,
                          event=event, created_at=datetime.now(), user_id=current_user.id)
        # here the back-referencing works - comment.destination is set
        # and the link is created
        db.session.add(comment)
        db.session.commit()
        # flashing a message which needs to be handled by the html
        flash('Your comment has been added')
        print('Your comment has been added')
    # using redirect sends a GET request to destination.show
    return redirect(url_for('events.show', id=id))

def check_tickets(form, event):
    if form.tickets_required.data == 0:
        flash("You must book at least one ticket!")
    else:
        if event.tickets_remaining - form.tickets_required.data < 0:
            flash("Your order cannot be placed at it exceeds the number of tickets remaining. Reduce the quantity and try again.")
    return True

@eventbp.route('/<id>/book', methods=['GET', 'POST'])
@login_required
def book_event(id):
    form = BookingForm()
    event = Event.query.filter_by(id=id).first()
    if check_tickets(form, event, id) == True:
        if form.validate_on_submit():
            if event.tickets_remaining - form.tickets_required.data == 0:
                event.event_status = EventStatus.BOOKED
            new_booking = Booking(
                tickets_booked=form.tickets_required.data, booked_on=datetime.now(), user_id=current_user.id, event_id=id)
            Event.query.filter_by(id=id).update(
                {'tickets_remaining': event.tickets_remaining-form.tickets_required.data, 'tickets_booked': event.tickets_booked+form.tickets_required.data}, synchronize_session='evaluate')
            db.session.add(new_booking)
            db.session.commit()
            flash_string = "Your booking was successfully created! You've been charged ${:,.2f}. Your booking reference is: {}".format(
                (event.price)*(new_booking.tickets_booked), new_booking.id)
            flash(flash_string)
            print('Your booking was successfully created!')
            return redirect(url_for('events.show', id=id))
    return redirect(url_for('events.show', id=id))


def check_upload_file(form):
    # get file data from form
    fp = form.image.data
    filename = fp.filename
    # get the current path of the module file… store image file relative to this path
    BASE_PATH = os.path.dirname(__file__)
    # upload file location – directory of this file/static/image
    # upload_path=os.path.join(BASE_PATH,current_app.config['UPLOAD_FOLDER'],secure_filename(filename))
    upload_path = os.path.join(
        BASE_PATH, 'static/images', secure_filename(filename))
    # store relative path in DB as image location in HTML is relative
    # db_upload_path=current_app.config['UPLOAD_FOLDER'] + secure_filename(filename)
    db_upload_path = '/static/images/' + secure_filename(filename)
    # save the file and return the db upload path
    fp.save(upload_path)
    return db_upload_path
