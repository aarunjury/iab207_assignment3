from bookings.views import my_events
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login.utils import login_required
from .models import Event, Comment, EventCity, EventGenre, EventStatus, Booking
from .forms import EditEventForm, EventForm, CommentForm, BookingForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import current_user

eventbp = Blueprint('events', __name__, url_prefix='/events')

@eventbp.route('/<id>')
def show(id):
    event = Event.query.filter_by(id=id).first()
    # create the comment form
    comments_form = CommentForm()
    form = BookingForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    if current_user.name == 'Guest':
        name = 'Guest'
    else:
        name = current_user.name
    events = Event.query.all()
    genres = EventGenre
    cities = EventCity
    return render_template('events/event_details.html', cities=cities, event=event, form=comments_form, booking_form=form, username=name, events_list=events, genres=genres)

@eventbp.route('/view_all')
def view_all_events():
    if current_user.name == 'Guest':
      name = 'Guest'
    else:
      name = current_user.name
    events_list_all = Event.query.all()
    genres=EventGenre
    cities = EventCity
    return render_template('events/view_events.html', cities=cities, username=name, heading='All Events', events=events_list_all, genres=genres, events_list=events_list_all)

@eventbp.route('/view_all/<genre>')
def view_events(genre):
    genre = genre.upper()
    genre_events_list = Event.query.filter_by(event_genre=genre).all()
    if current_user.name == 'Guest':
      name = 'Guest'
    else:
      name = current_user.name
    events_list_all = Event.query.all()
    genres=EventGenre
    cities = EventCity
    return render_template('events/view_events.html', cities=cities, username=name, heading=genre, events=genre_events_list, genres=genres, events_list=events_list_all)

@eventbp.route('/view_all/city/<city_name>')
def view_events_city(city_name):
    city_name = city_name.upper()
    city_events = Event.query.filter_by(event_city=city_name).all()
    if current_user.name == 'Guest':
      name = 'Guest'
    else:
      name = current_user.name
    events_list_all = Event.query.all()
    genres=EventGenre
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
                      image=db_file_path, total_tickets=form.total_tickets.data, tickets_remaining=form.total_tickets.data, event_status=EventStatus(
                          1).name,
                      event_genre=form.event_genre.data.upper(), event_city=form.event_city.data.upper(), user_id=current_user.id)
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
def update_event(id):
    form = EditEventForm()
    event = Event.query.get(id)
    # form.title.data=event.title
    # form.date.data=event.date
    # form.headliner.data=event.headliner
    # form.venue.data=event.venue
    # form.desc.data=event.description
    # form.total_tickets.data=event.total_tickets
    if form.validate_on_submit():
        # call the function that checks and returns image
        db_file_path = check_upload_file(form)
        event.title=form.title.data
        event.date=form.date.data
        event.headliner=form.headliner.data
        event.venue=form.venue.data
        event.description=form.desc.data
        event.image=db_file_path
        event.total_tickets=form.total_tickets.data
        event.tickets_remaining=form.total_tickets.data#minus sum of tickets_booked where event_id in bookings=event.id
        event.event_status=form.event_status.data.upper()
        event.event_genre=form.event_genre.data.upper()
        event.event_city=form.event_city.data.upper()
        # # commit to the database
        db.session.commit()
        flash('Successfully updated event!')
        # Always end with redirect when form is valid
        return redirect(url_for('main.my_events'))
    else:
        print('something wrong')
    events_list = Event.query.all()
    genres = EventGenre
    cities = EventCity
    return render_template('events/edit_event.html', cities=cities, event_form=form, event=event, username=current_user.name, events_list=events_list, genres=genres)

@eventbp.route('/<id>/delete', methods=['GET', 'POST'])
@login_required
def delete_event(id):
    Event.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('main.my_events'))

@eventbp.route('/<id>/comment', methods=['GET', 'POST'])
@login_required
def comment(id):
    form = CommentForm()
    # get the destination object associated to the page and the comment
    event_obj = Event.query.filter_by(id=id).first()
    if form.validate_on_submit():
        # read the comment from the form
        comment = Comment(text=form.text.data,
                          event=event_obj, user_id=current_user.id)
        # here the back-referencing works - comment.destination is set
        # and the link is created
        db.session.add(comment)
        db.session.commit()
        # flashing a message which needs to be handled by the html
        flash('Your comment has been added')
        print('Your comment has been added')
    # using redirect sends a GET request to destination.show
    return redirect(url_for('events.show', id=id))

@eventbp.route('/<id>/book', methods=['GET', 'POST'])
@login_required
def book_event(id):
  form = BookingForm()
  event_obj = Event.query.filter_by(id=id).first()
  if form.validate_on_submit():
    if event_obj.tickets_remaining - form.tickets_required.data < 0:
        flash("You can't book that many tickets!")
        return redirect(url_for('events.show', id=id))
    else:
        if event_obj.tickets_remaining - form.tickets_required.data == 0:
            event_obj.event_status = EventStatus.BOOKED
        new_booking = Booking(tickets_booked=form.tickets_required.data, user_id=current_user.id, event_id=id)
        Event.query.filter_by(id=id).\
            update({'tickets_remaining': event_obj.tickets_remaining-form.tickets_required.data}, synchronize_session='evaluate')
        db.session.add(new_booking)
        db.session.commit()
        flash('Your booking was successfully created!')
        print('Your booking was successfully created!')
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


