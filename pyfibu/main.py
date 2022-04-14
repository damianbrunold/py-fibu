from importlib.metadata import version
from sqlalchemy.exc import IntegrityError
from flask_babel import gettext

from flask import (
    Blueprint, flash, g, redirect, render_template, render_template_string, request, url_for
)

bp = Blueprint('main', __name__)

from pyfibu.auth import login_required


@bp.route('/')
@login_required
def index():
    return render_template('main/index.html')


@bp.route('/status')
def status():
    try:
        v = version('pyfibu')
    except Exception:
        v = "-"
    return render_template('main/status.html', v = v)
