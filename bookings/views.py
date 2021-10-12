from flask import Blueprint, render_template, request, url_for, redirect
from .models import Event, EventCity, EventGenre, Booking
from flask_login import login_required, current_user

mainbp = Blueprint('main', __name__)

@mainbp.route('/')
def index():
    if current_user.name == 'Guest':
        name = 'Guest'
    else:
        name = current_user.name
    all_events = Event.query.all()
    genres = EventGenre
    cities = EventCity
    return render_template('index.html', cities=cities, events_list = all_events, username = name, genres=genres)

@mainbp.route('/my_bookings')
@login_required
def my_bookings():
    all_events = Event.query.all()
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    booked_events = []
    for booking in bookings:
        booked_events += Event.query.filter_by(id=booking.id).all()
    genres = EventGenre
    cities = EventCity
    return render_template('events/my_events.html', heading='My Bookings', cities=cities, username = current_user.name, bookings=bookings, events=booked_events, events_list = all_events, genres=genres)

@mainbp.route('/my_events')
@login_required
def my_events():
    all_events = Event.query.all()
    genres = EventGenre
    cities = EventCity
    return render_template('events/my_events.html', heading='My Events', cities=cities, username = current_user.name, events=current_user.created_events, events_list = all_events, genres=genres)

@mainbp.route('/search')
def search():
    if request.args['search']:
        print(request.args['search'])
        event = "%" + request.args['search'] + '%'
        events = Event.query.filter(
            Event.description.like(event)).all()
        events += Event.query.filter(Event.title.like(event)).all()
        events += Event.query.filter(Event.event_city.like(event)).all()
        events += Event.query.filter(Event.event_genre.like(event)).all()
        events = list(set(events))
        all_events = Event.query.all()
        genres = EventGenre
        cities = EventCity
        return render_template('events/view_events.html', cities=cities, username=current_user.name, heading='Search Results', events=events, genres=genres, events_list=all_events)
    else:
        return redirect(url_for('main.index'))