from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import threading # Импорт модуля для многопоточности
import requests
import locale

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db' # Настройка пути к базе данных SQLite
db = SQLAlchemy(app) # Инициализация SQLAlchemy для работы с базой данных


class Product(db.Model): # Создание модели данных для товаров
    # Определение полей таблицы БД
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    article = db.Column(db.String(100))
    name = db.Column(db.String(200))
    rating = db.Column(db.Float)
    feedback_count = db.Column(db.Integer)
    price = db.Column(db.String(20))
    url = db.Column(db.String(500))

# Определение маршрутов приложения Flask
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contacts/')
def contacts():
    return render_template('contacts.html')


@app.route('/form/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        category = request.form['category']
        if category:
            return redirect(url_for('results', category=category))
    return render_template('form.html')


@app.route('/results/<category>', methods=['GET'])
def results(category, save_to_database=None):
    parsed_data = {} # Инициализация переменной для хранения спарсенных данных

    if category == 'default': # Обработка запроса для категории
        return render_template('results.html', category=category, results=None) # Отображение страницы результатов с информацией о пустой категории

    if category in parsed_data:
        results = parsed_data[category]
        return render_template('results.html', category=category, results=results)

    # Получение данных с внешнего источника
    url = f'https://search.wb.ru/exactmatch/ru/common/v4/search?TestGroup=pk2_alpha05&TestID=351&appType=1&curr=rub&dest=-1257786&' \
          f'query={category}&resultset=catalog&sort=popular&spp=26&suppressSpellcheck=false'

    resp = requests.get(url)
    resp.encoding = 'utf-8'
    locale.setlocale(locale.LC_ALL, '')

    # Парсинг данных и сохранение в базу данных
    if resp.status_code == 200:
        data_to_save = []
        try:
            Id_product = [i['id'] for i in resp.json()['data']['products']]
            Name = [n['name'] for n in resp.json()['data']['products']]
            Raiting = [r['reviewRating'] for r in resp.json()['data']['products']]
            Feedback = [f['feedbacks'] for f in resp.json()['data']['products']]
            Cost = [locale.format_string('%d', c['salePriceU'] // 100, grouping=True) for c in
                    resp.json()['data']['products']]
            Url_product = [f'https://www.wildberries.ru/catalog/{u}/detail.aspx?targetUrl=XS' for u in Id_product]

            for i, n, r, f, c, u in list(zip(Id_product, Name, Raiting, Feedback, Cost, Url_product)):
                existing_product = Product.query.filter_by(article=i).first()
                if not existing_product:
                    # Если товара с таким уникальным идентификатором нет, добавляем его в базу
                    product = Product(
                        category=category,
                        article=i,
                        name=n,
                        rating=r,
                        feedback_count=f,
                        price=f'{c} руб.',
                        url=u
                    )
                    db.session.add(product)

                    result = {
                        'Категория': category,
                        'Результаты': {
                            'Артикул': i,
                            'Наименование': n,
                            'Рейтинг': r,
                            'Количество отзывов': f,
                            'Цена': f'{c} руб.',
                            'Ссылка': u
                        }
                    }
                    data_to_save.append(result)
                else:
                    # Если товар уже существует, добавляем его в data_to_save без добавления в базу данных
                    result = {
                        'Категория': category,
                        'Результаты': {
                            'Артикул': existing_product.article,
                            'Наименование': existing_product.name,
                            'Рейтинг': existing_product.rating,
                            'Количество отзывов': existing_product.feedback_count,
                            'Цена': existing_product.price,
                            'Ссылка': existing_product.url
                        }
                    }
                    data_to_save.append(result)

                db.session.commit()

            threading.Thread(target=save_to_database, args=(category, data_to_save)).start()

            parsed_data[category] = data_to_save
            return render_template('results.html', category=category, results=data_to_save)
        except KeyError:
            message = "Спарсенных данных нет, вернитесь на главную страницу и введите категорию"
            return render_template('results.html', category=category, message=message)
    else:
        return "Ошибка при запросе данных"


@app.route('/saved_results', methods=['GET'])
def saved_results():
    parsed_data = {} # Инициализация переменной для хранения данных из базы данных
    with app.app_context():
        products = Product.query.all() # Получение всех товаров из базы данных

        # Обход всех товаров и формирование структуры данных
        for product in products:
            category = product.category
            if category not in parsed_data:
                parsed_data[category] = []

            result = {
                'Категория': category,
                'Результаты': {
                    'Артикул': product.article,
                    'Наименование': product.name,
                    'Рейтинг': product.rating,
                    'Количество отзывов': product.feedback_count,
                    'Цена': product.price,
                    'Ссылка': product.url
                }
            }
            parsed_data[category].append(result)

    return render_template('saved_results.html', parsed_data=parsed_data,
                           success_message='Данные успешно записаны в базу данных')


if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Создание таблиц в базе данных

    app.run(debug=True) # Запуск приложения Flask в режиме отладки
