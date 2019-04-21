import psycopg2
import click

from scrapy.crawler import CrawlerProcess
from lotto_scraping.lotto_scraping.spiders.lotto_spider import LottoSpider
from json import load

from flask import g, current_app
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        try:
            g.db = psycopg2.connect(
                current_app.config['DATABASE'],
            )
            from psycopg2.extras import RealDictCursor
            g.db.cursor_factory = RealDictCursor

            g.db.autocommit = True
        except psycopg2.OperationalError:
            print("Connection failed, creating new db.")
            conn = psycopg2.connect(
                "postgres://postgres:postgres@localhost/postgres"
            )
            conn.autocommit = True
            with conn.cursor() as c:
                c.execute("CREATE DATABASE lotto_analyzer;")

            return get_db()

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db:
        db.close()


def init_db():
    db = get_db()
    c = db.cursor()

    with current_app.open_resource('schema.sql') as f:
        c.execute(f.read().decode('utf-8'))

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(LottoSpider)
    process.start()

    with open('wyniki.json', 'r') as f:
        for record in load(f):
            c.execute("""INSERT INTO lotto VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                      (record["draw_id"],
                       record["date"],
                       *record["lotto"],
                       *record["plus"]))

    c.close()
    db.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
