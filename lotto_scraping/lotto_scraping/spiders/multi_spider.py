from scrapy import Spider, Request
from json import dump
from re import sub


def get_spider():
    return MultiSpider


class Control:
    __latest = None
    __running = True
    result = []

    @classmethod
    def get_latest(cls):
        return cls.__latest

    @classmethod
    def set_latest(cls, val):
        cls.__latest = val

    @classmethod
    def is_running(cls):
        return cls.__running

    @classmethod
    def stop_running(cls):
        cls.__running = False


class MultiSpider(Spider):
    name = "multi"
    start_urls = [
        'https://www.multipasko.pl/wyniki-lotto/multi-lotek/',
    ]

    def parse(self, response):
        latest = Control.get_latest()

        table = response.css("table.wynikiLosowan")

        draw_ids = table.css("td.nrlos *::text").getall()
        results = table.css("td.wyn3")

        current_page = int(draw_ids[0])
        for i in range(len(draw_ids)):
            draw_id = int(draw_ids[i])
            draw_date = "".join(results[i].css("div *::text").getall())

            if not latest or latest < draw_id:

                plain_html = results[i].get()
                numbers_start = plain_html.index("</div>") + len("</div>")
                proper_results = sub(r'<.*?>', '', plain_html[numbers_start:]).split(",")
                plus = results[i].css("span.plus::text").get()

                Control.result.append({
                    "draw_id": draw_id,
                    "date": draw_date,
                    "multi": proper_results,
                    "plus": plus,
                })
            else:
                Control.stop_running()
                break

        if Control.is_running() and current_page - 30 > 0:
            next_page = response.urljoin(f'''wyniki-lotto/multi-lotek/sortowane/{str(current_page - 30)}''')
            yield Request(next_page, callback=self.parse)
        else:
            with open('wyniki_multi.json', 'w') as f:
                dump(Control.result, f)
