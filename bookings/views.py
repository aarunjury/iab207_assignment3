from flask import Blueprint, render_template, request
from .models import Event
from flask_login import login_required, current_user
from . import db

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
    return render_template('events/my_events.html', heading='My Bookings', bookings=current_user.created_bookings)


@mainbp.route('/my_events')
@login_required
def my_events():
    return render_template('events/my_events.html', heading='My Events', events=current_user.created_events)

    
@mainbp.route('/search', methods=['GET', 'POST'])
def search():
    # create query object
    query = db.session.query(Event)
    # loop through arguments
    for arg in request.args:
        # check if arg exists and is not empty
        if (arg == 'genre' and request.args['genre'] != ''):
            # update your query with the arg
            query = query.filter(Event.event_genre.like(f"%{request.args['genre']}%"))

        if (arg == 'city' and request.args['city'] != ''):
            query = query.filter(Event.event_city.like(f"%{request.args['city']}%"))

        # get destinations from your query
        events = query.order_by(Event.title.asc()).all()
        if (arg == 'search' and request.args['search'] != ''):
            query = "%" + request.args['search'] + '%'
            events = Event.query.filter(
                Event.description.like(query)).all()
            events += Event.query.filter(Event.title.like(query)).all()
            events += Event.query.filter(Event.event_city.like(query)).all()
            events += Event.query.filter(Event.event_genre.like(query)).all()
            # Filter out duplicates (__eq__ has been set on the model for comparison)
            events = list(set(events))
    # return all events that meet the search criteria on a page
    return render_template('events/view_events.html', heading='Search Results', events=events)
