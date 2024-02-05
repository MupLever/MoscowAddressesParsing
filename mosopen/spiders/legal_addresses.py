import re

from typing import Iterable, Any
from scrapy import Request, Spider
from scrapy.http import Response


class LegalAddressesSpider(Spider):
    name = "legal_addresses"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Referer": "http://mosopen.ru/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    }

    def start_requests(self) -> Iterable[Request]:
        """Делает запрос на получение страницы со всеми районами Москвы"""
        yield Request(
            headers=self.headers,
            url="http://mosopen.ru/streets",
            method="GET",
            callback=self.parse_districts,
        )

    def parse_districts(self, response: Response) -> Iterable[Request]:
        """
        Делает подзапрос на каждый район для получения названий улиц
        :param response: Ответ
        :return: Запрос
        """
        districts = response.xpath("//div[@id='regions_by_letters']/table[@class='regions_list']/tr/td/p/a")
        for district in districts:
            district_name = district.xpath("./text()").get()
            district_url = district.xpath("./@href").get()

            yield Request(
                url=district_url,
                callback=self.parse_streets,
                headers=self.headers,
                method="GET",
                cb_kwargs={"district": district_name},
            )

    def parse_streets(self, response: Response, **kwargs: Any) -> Iterable[Request]:
        """
        Делает подзапросы для получения номеров домов на каждой улице
        :param response: Ответ
        :param kwargs: "district" - название района для проброса
        :return: Запрос
        """
        district = kwargs["district"]
        streets = response.xpath("//div[@class='double_block clearfix']/div/ul/li/a")

        for street in streets:
            street_name = street.xpath("./text()").get()
            street_url = street.xpath("./@href").get()

            yield Request(
                url=street_url,
                method="GET",
                headers=self.headers,
                callback=self.parse_houses,
                cb_kwargs={"district": district, "street": street_name},
            )

    @staticmethod
    def parse_houses(response: Response, **kwargs: Any) -> dict:
        """
        Отдает данные по каждой улице в своем районе
        :param response: Ответ
        :param kwargs: "district" - название района, "street" - название улицы
        :return: словарь вида: {
            "district": district,
            "street": street,
            "houses": [...]
        }
        """
        district = kwargs["district"]
        street = kwargs["street"]
        houses = response.xpath("//div[@id='content']/p[3]/a/text()").getall()
        if houses and houses[-1].startswith("показать"):
            houses.pop()
            houses.extend(response.xpath("//div[@id='content']/p[3]/span/a/text()").getall() or [])

        yield {
            "district": district,
            "street": street,
            "houses": list(map(lambda house: re.sub(r"[ |\xa0]", " ", house), houses)),
        }
