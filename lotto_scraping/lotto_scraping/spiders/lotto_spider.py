from scrapy import Spider, Request
# from datetime import date
from json import dump


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


class LottoSpider(Spider):
    name = "lotto"
    start_urls = [
        'https://www.multipasko.pl/wyniki-lotto/duzy-lotek/',
    ]

    def parse(self, response):
        results = response.css("table.wynikiLosowan tr")
        current_page = int(results.css("td.nrlos::text").get())
        for result in results:
            draw_id = int(result.css("td.nrlos::text").get())

            # current_date = date(*reversed(list(map(int, data.split('.')))))

            latest = Control.get_latest()

            if not latest or latest > draw_id:
                lotto = list(map(str.strip, result.css("td.wyn3 ul.showdl li::text").getall()))
                plus = list(map(str.strip, result.css("td.wyn3 ul.lplus.showlp li::text").getall()))

                Control.result.append({
                    "draw_id": draw_id,
                    "date": result.css("td.wyn2::text").get(),
                    "lotto": lotto,
                    "plus": plus if plus else ['', '', '', '', '', ''],
                })
            else:
                Control.stop_running()
                break

        if Control.is_running() and current_page - 25 > 0:
            next_page = response.urljoin(f'''wyniki-lotto/duzy-lotek/sortowane/{str(current_page - 25)}''')
            yield Request(next_page, callback=self.parse)
        else:
            with open('wyniki.json', 'w') as f:
                dump(Control.result, f)
