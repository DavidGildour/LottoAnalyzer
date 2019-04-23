# import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
# from random import randint
import analyzer.search_logic as search_logic
from analyzer.postgres_db import get_db, update_db

bp = Blueprint('lotto', __name__, url_prefix='/lotto')


@bp.route('/')
def index():
    db = get_db().cursor()

    db.execute("SELECT * FROM lotto ORDER BY id DESC LIMIT(1)")
    latest = db.fetchone()["date"]

    return render_template('lotto/search_results.html', latest=latest)


@bp.route('/update')
def update():
    update_db('lotto')

    return redirect(url_for('lotto.index'))


@bp.route('/date')
def date():
    db = get_db().cursor()

    day = request.args.get('day') or '%'
    month = request.args.get('month') or '%'
    year = request.args.get('year') or '%'

    searched_date = ".".join([day, month, year])

    db.execute("SELECT id, date, CONCAT_WS(' ', l1, l2, l3, l4, l5, l6) AS lotto, "
               "CONCAT_WS(' ', p1, p2, p3, p4, p5, p6) AS plus FROM lotto WHERE date LIKE %s", (searched_date,))
    results = db.fetchall()

    return render_template('lotto/search_results.html', results=results or [], size=len(results))


@bp.route('/numbers')
def numbers():
    searched_numbers = request.args.get('numbers')
    results = search_logic.get_results_by_numbers(searched_numbers)

    return render_template('lotto/search_results.html', results=results, size=len(results))
