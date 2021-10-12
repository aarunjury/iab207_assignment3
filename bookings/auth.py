from flask import Blueprint, render_template, request, redirect, url_for, flash
from .forms import LoginForm, RegisterForm
from .models import Event, EventCity, EventGenre, User
from . import db
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# create a blueprint
authbp = Blueprint('auth', __name__)


@authbp.route('/login', methods=['GET', 'POST'])
def login():
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        user_name = loginForm.user_name.data
        password = loginForm.password.data
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(name=user_name).first()
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password_hash, password):
            flash('Please check your login details and try again.')
            # if the user doesn't exist or password is wrong, reload the page
            return redirect(url_for('auth.login'))
        else:
            login_user(user, remember=remember)
            print('Successfully logged in')
            flash('You logged in successfully')
            return redirect(url_for('main.index'))
    if current_user.name == 'Guest':
        name = 'Guest'
    else:
        name = current_user.name
    all_events = Event.query.all()
    genres = EventGenre
    cities = EventCity
    return render_template('user.html', form=loginForm,  heading='Login', username=name, genres=genres, cities=cities, events_list=all_events)


@authbp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    address = []
    if form.validate_on_submit():
        # if this returns a user, then the email already exists in database
        user = User.query.filter_by(emailid=form.email_id.data).first()
        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            flash(
                'Email address already exists. Login using that email or try using a different email.')
            return redirect(url_for('auth.register'))
        address.append(str(form.street_no.data))
        address.append(form.street_name.data)
        address.append(form.state.data)
        address.append(str(form.postcode.data))
        address_string = ' '.join(str(item) for item in address)
        user = User(name=form.user_name.data, emailid=form.email_id.data, password_hash=generate_password_hash(
            form.password.data, method='sha256'), phone=form.phone.data, address=address_string)
        db.session.add(user)
        db.session.commit()
        flash('Successfully created new user! Please login to continue.')
        return redirect(url_for('auth.login'))
    if current_user.name == 'Guest':
        name = 'Guest'
    else:
        name = current_user.name
    all_events = Event.query.all()
    genres = EventGenre
    cities = EventCity
    return render_template('user.html', form=form, heading='Register', username=name, genres=genres, cities=cities, events_list=all_events)


@authbp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
