# login required decorator
import functools
# flask dependant
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
# password hashing
from werkzeug.security import check_password_hash, generate_password_hash
# app models
from ..models import db, User, Post

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """ Validates and creates user."""
    if request.method == 'POST':
        u = User(
            username=request.form['username'],
            password=generate_password_hash(request.form['password']),
            email=request.form['email']
        )
        error = None

        if not u.username:
            error = 'Username is required.'
        elif not u.password:
            error = 'Password is required.'

        if not u.email:
            u.email = None

        if error is None:
            try:
                db.session.add(u)
                db.session.commit()
            except:
                error = f"User {u.username} is already registered"
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """ Takes user input. Creates user session."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = User.query.filter(User.username == username).first()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """ Load existing user data before each request."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter(User.id == user_id).first()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    """ Checks for user session. None returns login view"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
