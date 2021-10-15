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
    return render_template('index.html')


@mainbp.route('/my_bookings')
@login_required
def my_bookings():
    # First get the all the current user's bookings
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    print(current_user.id)
    # Create an empty list to hold their Events pertaining to each Booking
    booked_events = []
    # Add the booked events to the list
    for booking in bookings:
        booked_events += Event.query.filter_by(id=booking.event_id).all()
    print(booked_events)
    return render_template('events/my_events.html', heading='My Bookings', bookings=bookings, events=booked_events)


@mainbp.route('/my_events')
@login_required
def my_events():
    return render_template('events/my_events.html', heading='My Events', events=current_user.created_events)


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
        # Filter out duplicates
        events = list(set(events))
        return render_template('events/view_events.html', heading='Search Results', events=events)
    else:
        return redirect(url_for('main.index'))
