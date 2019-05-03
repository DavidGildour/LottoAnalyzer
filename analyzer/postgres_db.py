import psycopg2
import click

from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from lotto_scraping.lotto_scraping.spiders import lotto_spider, multi_spider
from json import load

from flask import g, current_app, flash
from flask.cli import with_appcontext


SPIDERS = {
    'lotto': lotto_spider,
    'multi': multi_spider,
}


def insert_from_json(cur, table: str, json: str):
    with open(json, 'r') as f:
        count = 0
        if table == "lotto":
            for record in load(f):
                count += 1
                cur.execute("INSERT INTO lotto VALUES (" + ("%s," * 13) + "%s);",
                            (record["draw_id"],
                             record["date"],
                             *record["lotto"],
                             *record["plus"]))
        elif table == "multi":
            for record in load(f):
                count += 1
                cur.execute("INSERT INTO multi VALUES (" + ("%s," * 22) + "%s);",
                            (record["draw_id"],
                             record["date"],
                             *record["multi"],
                             record["plus"]))
        flash(f"Successfully added {count} record" + ("s." if count != 1 else "."))


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

    for spider in SPIDERS.values():
        process.crawl(spider.get_spider())

    process.start()

    insert_from_json(c, 'lotto', 'wyniki_lotto.json')
    insert_from_json(c, 'multi', 'wyniki_multi.json')

    c.close()
    db.close()


def update_db(lottery: str):
    db = get_db()
    c = db.cursor()

    c.execute('SELECT id FROM ' + lottery + ' ORDER BY id DESC LIMIT 1')
    latest = c.fetchone()["id"]

    spider = SPIDERS[lottery]
    spider.Control.set_latest(int(latest))

    runner = CrawlerRunner()
    runner.crawl(spider.get_spider()).addBoth(lambda _: reactor.stop())
    reactor.run(0)

    json = 'wyniki_' + lottery + '.json'

    insert_from_json(c, lottery, json)

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
