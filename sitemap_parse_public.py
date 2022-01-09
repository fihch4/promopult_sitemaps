import requests
from bs4 import BeautifulSoup
from config_public import *
from datetime import datetime
import time
from script_mysql import MySQLi


class Sitemap:
    def __init__(self):
        self.urls_list = []
        self.xml_list = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/90.0.4430.212 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                      "*/*;q=0.8, "
                      "application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache"
        }

    def get_data(self, url_request):
        try:
            r = requests.get(url=url_request, headers=self.headers)
            return r
        except Exception as ex:
            print(ex)
            return "Error"

    def get_xml_and_url(self, sitemap_url):
        data_url = ""
        error_count = 0
        while data_url != 200:
            data_url = self.get_data(sitemap_url)
            if data_url.status_code == 200:
                soup = BeautifulSoup(data_url.text, "lxml")
                request_urls_result = soup.find_all("loc")
                for url in request_urls_result:
                    url = str(url).replace("<loc>", "").replace("</loc>", "")
                    if '.xml' in url:
                        if url not in self.xml_list:
                            self.xml_list.append(url)
                    else:
                        if url not in self.urls_list:
                            self.urls_list.append(url)
                for url in self.xml_list:
                    error_count = 0
                    data_url = ""
                    r = requests.get(url=url, headers=self.headers)
                    while data_url != 200:
                        if r.status_code == 200:
                            soup = BeautifulSoup(r.text, "lxml")
                            request_urls_result = soup.find_all("loc")
                            for url in request_urls_result:
                                url = str(url).replace("<loc>", "").replace("</loc>", "")
                                if '.xml' in url:
                                    if url not in self.xml_list:
                                        self.xml_list.append(url)
                                else:
                                    if url not in self.urls_list:
                                        self.urls_list.append(url)
                        else:
                            error_count += 1
                            time.sleep(5)
                            if error_count >= attempt:
                                return "Error"
                        data_url = 200
            else:
                error_count += 1
                time.sleep(5)
                if error_count >= attempt:
                    return "Error"

            d = {'xml_list': self.xml_list, 'urls_list': self.urls_list}
            return d


def list_urls_from_bd():
    db = MySQLi(host, user, password, database_home)
    all_urls_for_domain_in_db = db.fetch("SELECT url FROM sitemaps")
    urls_in_bd = []
    """Наполняем временный список ссылками из БД"""
    for list_url_bd in all_urls_for_domain_in_db['rows']:
        urls_in_bd.append(list_url_bd[0])
    return urls_in_bd


def finally_threads_sitemap(site):
    db = MySQLi(host, user, password, database_home)
    print(f"SITE: {site}")
    date_for_bd = datetime.now().date()
    """Определяем, был сегодня парсинг карт сайта или нет.
    Если переменная id_domain_from_date будет пустой, то парсинга не было.
    """
    id_domain_from_date = db.fetch("SELECT id FROM sitemap_count WHERE domain = %s AND date = %s LIMIT 1", site,
                                   date_for_bd)
    if len(id_domain_from_date['rows']) < 1:
        sitemap_url = sites[site]
        sitemap_obj = Sitemap()
        sitemaps_urls = sitemap_obj.get_xml_and_url(sitemap_url)
        count_sitemaps = len(sitemaps_urls['urls_list'])
        print(f"Закончился парсинг карты сайта для: {site}")
        """Для БД sitemap_count
        Проверяем, есть ли домен в БД. Если домена нет, берем последний id, увеличиваем на 1.
        Если домен присутствует, заносим сразу всю информацию.
        """

        id_domain = db.fetch("SELECT id FROM sitemap_count WHERE domain = %s LIMIT 1", site)
        if not id_domain['rows']:
            id_domain_desc = db.fetch("select id from sitemap_count ORDER BY id DESC LIMIT 1")
            if not id_domain_desc['rows']:
                id_domain_desc = 0
            else:
                id_domain_desc = int(id_domain_desc['rows'][0][0]) + 1

            db.commit("INSERT INTO sitemap_count (id, domain, count, date) VALUES (%s, %s, %s, %s)", id_domain_desc,
                      site,
                      count_sitemaps, date_for_bd)
            id_domain = id_domain_desc
        else:
            id_domain = id_domain['rows'][0][0]
            db.commit("INSERT INTO sitemap_count (id, domain, count, date) VALUES (%s, %s, %s, %s)", id_domain,
                      site,
                      count_sitemaps, date_for_bd)
        """Получаем список ссылок в базе данных, которые привязаны к домену."""
        urls_in_db = list_urls_from_bd()
        num_urls_in_bd_check = 0
        num_add_urls = 0
        for url in sitemaps_urls['urls_list']:
            if url in urls_in_db:
                num_urls_in_bd_check += 1
            else:
                num_add_urls += 1
                db.commit("INSERT INTO sitemaps (id, url) VALUES (%s, %s)", id_domain, url)
        """Добавление в БД sitemap_add и проверка """
        if num_add_urls >= 1 and num_add_urls != count_sitemaps:
            for url_bd in sitemaps_urls['urls_list']:
                if url_bd not in urls_in_db:
                    num_add_urls += 1
                    db.commit("INSERT INTO sitemaps_add(id, url, date) VALUES (%s, %s, %s)", id_domain, url_bd,
                              date_for_bd)
        """Проверяем, какие ссылки удалены из карты сайта. Заносим в БД и удаляем из общей"""
        for url in urls_in_db:
            if url not in sitemaps_urls['urls_list']:
                db.commit("DELETE FROM sitemaps WHERE url = %s", url)
                db.commit("INSERT INTO sitemaps_del (id, url, date) VALUES(%s, %s, %s)", id_domain, url, date_for_bd)


def main():
    for site in sites:
        finally_threads_sitemap(site)


if __name__ == "__main__":
    main()