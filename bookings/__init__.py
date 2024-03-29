from datetime import datetime
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    bootstrap = Bootstrap5(app)
    bcrypt = Bcrypt(app)
    app.secret_key = "1234567890"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticketsmarter.sqlite'
    app.config['UPLOAD_FOLDER'] = 'static/images/'
    db.init_app(app)
    login_manager = LoginManager()
    from .models import User, Anonymous
    login_manager.anonymous_user = Anonymous
    login_manager.login_message_category = "warning"
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    from . import views, events, auth
    app.register_blueprint(views.mainbp)
    app.register_blueprint(events.eventbp)
    app.register_blueprint(auth.authbp)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    
    @app.context_processor
    def get_context():
        # Checks if the current user is Anonymous or logged in
        if current_user.name == 'Guest':
            name = 'Guest'
        else:
            name = current_user.name
        from bookings.models import Event, EventCity, EventGenre, EventStatus
        all_events = Event.query.all()
        # On launch, check if there are any events that are now in the past
        # and if so, change them to Inactive
        for event in all_events:
            if event.date < datetime.now():
                event.event_status=EventStatus.INACTIVE
        current_events = Event.query.filter(Event.event_status!='INACTIVE')
        db.session.commit()
        dropdown_events = Event.query.group_by(Event.headliner).filter(
        Event.event_status != 'INACTIVE').all()
        genres = EventGenre
        cities = EventCity
        return(dict(events_list=all_events,artist_list=dropdown_events,genres=genres,cities=cities,username=name,current_events=current_events))

    @app.errorhandler(404)
    def not_found(e):  # error view function
        return render_template('fourohfour.html'), 404

    @app.errorhandler(500)
    def not_found(e):  # error view function
        return render_template('fourohfour.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
    # pass through HTTP errors
        if isinstance(e, HTTPException):
            return e
    # now you're handling non-HTTP exceptions only
        print(e)
        return render_template('fourohfour.html'), 500

    return app