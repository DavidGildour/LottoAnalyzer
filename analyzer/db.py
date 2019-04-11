import sqlite3
import click

from scrapy.crawler import CrawlerProcess
from lotto_scraping.lotto_scraping.spiders.lotto_spider import LottoSpider
from json import load

from flask import g, current_app
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(LottoSpider)
    process.start()

    with open('wyniki.json', 'r') as f:
        c = db.cursor()
        for record in load(f):
            c.execute("""INSERT INTO lotto (id, date, lotto, plus) VALUES (?, ?, ?, ?);""",
                      (record["draw_id"],
                       record["date"],
                       " ".join(record["lotto"]),
                       " ".join(record["plus"])))

    db.commit()
    db.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
