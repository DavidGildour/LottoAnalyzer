# import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
# from random import randint
import analyzer.search_logic as search_logic
from analyzer.postgres_db import get_db, update_db

bp = Blueprint('multi', __name__, url_prefix='/multi')


@bp.route('/')
def index():
    db = get_db().cursor()

    db.execute("SELECT * FROM multi ORDER BY id DESC LIMIT(1)")
    latest = db.fetchone()["date"]

    return render_template('multi/search_results.html', latest=latest)


@bp.route('/update')
def update():
    update_db('multi')

    return redirect(url_for('multi.index'))


@bp.route('/date')
def date():
    db = get_db().cursor()

    day = request.args.get('day') or '%'
    month = request.args.get('month') or '%'
    year = request.args.get('year') or '%'

    searched_date = ".".join([day, month, year])

    db.execute("SELECT date, plus, CONCAT_WS(' ', m1, m2, m3, m4, m5, m7, m8, m9, m10,"
               " m11, m12, m13, m14, m15, m16, m17, m18, m19, m20) AS multi "
               "FROM multi WHERE date LIKE %s", (searched_date,))
    results = db.fetchall()

    return render_template('multi/search_results.html', results=results or [], size=len(results))


@bp.route('/numbers')
def numbers():
    searched_numbers = request.args.get('numbers')
    results = search_logic.get_results_by_numbers(searched_numbers)

    return render_template('multi/search_results.html', results=results, size=len(results))
