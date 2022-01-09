#!/usr/bin/python3.8
sites = {
    'site.ru': 'https://site.ru/sitemap.xml/',
    'site2.ru': 'https://site2.ru/sitemap.xml/'
}
headers = {
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
host = "localhost"  # IP адрес базы данных
user = "user05"  # Логин
password = "tpegksteTGq21"  # Пароль
database_home = 'sitemaps'  # Название базы данных
attempt = 100
