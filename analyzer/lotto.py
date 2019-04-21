# import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
# from random import randint

from analyzer.db import get_db

bp = Blueprint('lotto', __name__, url_prefix='/lotto')


@bp.route('/')
def index():
    db = get_db().cursor()

    db.execute("SELECT * FROM lotto ORDER BY id DESC LIMIT(1)")
    latest = db.fetchone()["date"]

    return render_template('lotto/search_results.html', latest=latest)


@bp.route('/date')
def date():
    db = get_db().cursor()

    day = request.args.get('day') or '%'
    month = request.args.get('month') or '%'
    year = request.args.get('year') or '%'

    searched_date = ".".join([day, month, year])

    db.execute("SELECT id, date, l1||l2||l3||l4||l5||l6 AS lotto, "
               "p1||p2||p3||p4||p5||p6 AS plus FROM lotto WHERE date LIKE ?", (searched_date,))
    results = db.fetchall()

    return render_template('lotto/search_results.html', results=results or [])


@bp.route('/numbers')
def numbers():

    return render_template('lotto/search_results.html', results=[])
