Публичный скрипт парсинга карты сайта для множественной выборки сайтов.
Особенность скрипта - все ссылки или карты сайта должны быть указаны исключительно в едином файле.

Для работы скрипта требуется:
1. Создать базу данных MySQL.
2. Указать в настройках подключение к базе данных.
3. Создать три таблицы в базе данных:
CREATE TABLE sitemap_count (
domain text,
id INT,
cout INT,
date DATE)

CREATE TABLE sitemap_count (
domain text,
id INT,
cout INT,
date DATE)

CREATE TABLE sitemaps_add (
id int,
url text,
date DATE
)

CREATE TABLE sitemaps_del (
id INT,
url TEXT,
date DATE
)

4. Запустить скрипт на крон.
