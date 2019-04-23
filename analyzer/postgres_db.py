import psycopg2
import click

from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from lotto_scraping.lotto_scraping.spiders import lotto_spider, multi_spider
from json import load

from flask import g, current_app
from flask.cli import with_appcontext

SPIDERS = {
    'lotto': lotto_spider,
    'multi': multi_spider,
}

STATEMENT = {
    'lotto': 'SELECT id FROM lotto ORDER BY id DESC LIMIT 1',
}


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
    process.crawl(lotto_spider.LottoSpider)
    process.crawl(multi_spider.MultiSpider)
    process.start()

    with open('wyniki_lotto.json', 'r') as f:
        for record in load(f):
            c.execute("""INSERT INTO lotto VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                      (record["draw_id"],
                       record["date"],
                       *record["lotto"],
                       *record["plus"]))

    with open('wyniki_multi.json', 'r') as f:
        for record in load(f):
            c.execute("INSERT INTO multi VALUES (" + ("%s,"*22) + "%s);",
                      (record["draw_id"],
                       record["date"],
                       *record["multi"],
                       record["plus"]))

    c.close()
    db.close()


def update_db(lottery: str):
    db = get_db()
    c = db.cursor()

    c.execute(STATEMENT[lottery])
    latest = c.fetchone()["id"]

    spider = SPIDERS[lottery]
    spider.Control.set_latest(int(latest))

    runner = CrawlerRunner()
    runner.crawl(spider.LottoSpider).addBoth(lambda _: reactor.stop())
    reactor.run()

    with open('wyniki_lotto.json', 'r') as f:
        count = 0
        for record in load(f):
            count += 1
            c.execute("""INSERT INTO lotto VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                      (record["draw_id"],
                       record["date"],
                       *record["lotto"],
                       *record["plus"]))
        print(f"Added {count} records.")

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
