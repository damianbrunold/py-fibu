import datetime
import functools

from flask_babel import gettext, get_locale, get_timezone

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash

from sqlalchemy import select

from pyfibu.db import get_db, user_table

bp = Blueprint('auth', __name__, url_prefix='/auth')


def get_user(email):
    with get_db().connect() as conn:
        return conn.execute(
                select(
                    user_table.c.email,
                    user_table.c.name,
                    user_table.c.password,
                    user_table.c.locale,
                    user_table.c.timezone
                ).
                where(user_table.c.email == email)
        ).fetchone()


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        error = None
        user = get_user(email)

        if user is None:
            error = gettext('Login data are not correct')
        elif not check_password_hash(user.password, password):
            error = gettext('Login data are not correct')

        if error is None:
            session.clear()
            session['user_email'] = user.email
            session.permanent = True
            return redirect(url_for('main.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_email = session.get('user_email')

    if user_email is None:
        g.user = None
    else:
        g.user = get_user(user_email)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
