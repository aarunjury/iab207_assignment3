from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from sqlalchemy.sql.expression import false
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()
UPLOAD_FOLDER = '/static/images/'  # not working
SQLALCHEMY_TRACK_MODIFICATIONS = false


def create_app():
    app = Flask(__name__)
    bootstrap = Bootstrap(app)
    app.secret_key = "1234567890"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticketsmarter.sqlite'
    db.init_app(app)
    login_manager = LoginManager()
    from .models import User, Anonymous
    login_manager.anonymous_user = Anonymous
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

    @app.errorhandler(404)
    def not_found(e):  # error view function
        from .models import Event, EventGenre, EventCity
        all_events = Event.query.all()
        genres = EventGenre
        cities = EventCity
        return render_template('fourohfour.html', cities=cities, username=current_user.name, events=current_user.created_events, events_list=all_events, genres=genres), 404

    @app.errorhandler(500)
    def not_found(e):  # error view function
        from .models import Event, EventGenre, EventCity
        all_events = Event.query.all()
        genres = EventGenre
        cities = EventCity
        return render_template('fourohfour.html', cities=cities, username=current_user.name, events=current_user.created_events, events_list=all_events, genres=genres), 500

    # @app.errorhandler(Exception)
    # def handle_exception(e):
    #     from .models import Event, EventGenre, EventCity
    #     all_events = Event.query.all()
    #     genres = EventGenre
    #     cities = EventCity
    # # pass through HTTP errors
    #     if isinstance(e, HTTPException):
    #         return e
    # # now you're handling non-HTTP exceptions only
    #     print(e)
    #     return render_template('fourohfour.html', cities=cities, username=current_user.name, events=current_user.created_events, events_list=all_events, genres=genres), 500

    return app
