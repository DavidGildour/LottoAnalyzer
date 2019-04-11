import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from random import randint

from analyzer.db import get_db

bp = Blueprint('lotto', __name__, url_prefix='/lotto')


@bp.route('/', methods=("GET",))
def index():
    db = get_db().cursor()

    rand = randint(1, 6241)

    db.execute("SELECT lotto, plus FROM lotto WHERE id=?;", (rand,))
    latest = db.fetchone()

    return f"Random draw results: {tuple(latest)}"
