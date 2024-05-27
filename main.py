import requests
import locale
from sql_db import ParsingWB_DB


search = input('Введите категорию: ')

url = f'https://search.wb.ru/exactmatch/ru/common/v4/search?TestGroup=pk2_alpha05&TestID=351&appType=1&curr=rub&dest=-1257786&' \
      f'query={search}&resultset=catalog&sort=popular&spp=26&suppressSpellcheck=false'

resp = requests.get(url)

resp.encoding = 'utf-8'
locale.setlocale(locale.LC_ALL, '')
Id_product = [i['id'] for i in resp.json()['data']['products']]
Name = [n['name'] for n in resp.json()['data']['products']]
Raiting = [r['reviewRating'] for r in resp.json()['data']['products']]
Feedback = [f['feedbacks'] for f in resp.json()['data']['products']]
Cost = [locale.format_string('%d', c['salePriceU'] // 100, grouping=True) for c in resp.json()['data']['products']]
Url_product = [f'https://www.wildberries.ru/catalog/{u}/detail.aspx?targetUrl=XS' for u in Id_product]


data_to_save = []

for i, n, r, f, c, u in list(zip(Id_product, Name, Raiting, Feedback, Cost, Url_product)):
    result = {
        'Категория': search,
        'Результаты': {
            'Артикул': i,
            'Наименование': n,
            'Рейтинг': r,
            'Количетсво отзывов': f,
            'Цена': f'{c} руб.',
            'Ссылка': u
        }}
    data_to_save.append(result)

    db = ParsingWB_DB()
    db.insert_data(data_to_save)
    db.close_connection()