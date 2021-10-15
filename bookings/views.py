from flask import Blueprint, render_template, request, url_for, redirect
from .models import Event, EventCity, EventGenre, Booking
from flask_login import login_required, current_user

mainbp = Blueprint('main', __name__)

# Checks if the current user is Anonymous or logged in
def is_current_user():
    if current_user.name == 'Guest':
        name = 'Guest'
    else:
        name = current_user.name
    return name


@mainbp.route('/')
def index():
    name = is_current_user()
    # Gets a list of Events without duplicate artists (to populate the Artist navbar dropdown)
    dropdown_events = Event.query.group_by(Event.headliner)
    all_events = Event.query.all()
    genres = EventGenre
    cities = EventCity
    return render_template('index.html', username=name, artist_list=dropdown_events, events_list=all_events,  genres=genres, cities=cities)


@mainbp.route('/my_bookings')
@login_required
def my_bookings():
    # First get the all the current user's bookings
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    # Create an empty list to hold their Events pertaining to each Booking
    booked_events = []
    # Add the booked events to the list
    for booking in bookings:
        booked_events += Event.query.filter_by(id=booking.id).all()
    # General objects reqd. for loading page
    all_events = Event.query.all()
    dropdown_events = Event.query.group_by(Event.headliner)
    genres = EventGenre
    cities = EventCity
    return render_template('events/my_events.html', heading='My Bookings', cities=cities, username=current_user.name, artist_list=dropdown_events, bookings=bookings, events=booked_events, events_list=all_events, genres=genres)


@mainbp.route('/my_events')
@login_required
def my_events():
    all_events = Event.query.all()
    # General objects reqd. for loading page
    dropdown_events = Event.query.group_by(Event.headliner)
    genres = EventGenre
    cities = EventCity
    return render_template('events/my_events.html', heading='My Events', cities=cities, username=current_user.name, artist_list=dropdown_events, events=current_user.created_events, events_list=all_events, genres=genres)


@mainbp.route('/search')
def search():
    name = is_current_user()
    if request.args['search']:
        print(request.args['search'])
        event = "%" + request.args['search'] + '%'
        events = Event.query.filter(
            Event.description.like(event)).all()
        events += Event.query.filter(Event.title.like(event)).all()
        events += Event.query.filter(Event.event_city.like(event)).all()
        events += Event.query.filter(Event.event_genre.like(event)).all()
        # Filter out duplicates
        events = list(set(events))
        # General objects reqd. for loading page
        all_events = Event.query.all()
        dropdown_events = Event.query.group_by(Event.headliner)
        genres = EventGenre
        cities = EventCity
        return render_template('events/view_events.html', cities=cities, artist_list=dropdown_events, username=name, heading='Search Results', events=events, genres=genres, events_list=all_events)
    else:
        return redirect(url_for('main.index'))
