from flask import Flask, render_template, request, redirect, url_for
import requests
import locale

app = Flask(__name__)

# Глобальная переменная для хранения результатов
parsed_data = {}


@app.route('/')
def index():  # Главная страница
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
def results(category):
    global parsed_data

    if category == 'default':
        return render_template('results.html', category=category, results=None)

    # Если данные уже были спарсены для данной категории, используем их из хранилища
    if category in parsed_data:
        results = parsed_data[category]
        return render_template('results.html', category=category, results=results)

    url = f'https://search.wb.ru/exactmatch/ru/common/v4/search?TestGroup=pk2_alpha05&TestID=351&appType=1&curr=rub&dest=-1257786&' \
          f'query={category}&resultset=catalog&sort=popular&spp=26&suppressSpellcheck=false'

    resp = requests.get(url)
    resp.encoding = 'utf-8'
    locale.setlocale(locale.LC_ALL, '')

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

            parsed_data[category] = data_to_save  # Сохраняем данные в хранилище

            return render_template('results.html', category=category, results=data_to_save)
        except KeyError:
            message = "Спарсенных данных нет, вернитесь на главную страницу и введите категорию"
            return render_template('results.html', category=category, message=message)
    else:
        return "Ошибка при запросе данных"


@app.route('/saved_results', methods=['GET'])
def saved_results():
    global parsed_data
    return render_template('saved_results.html', parsed_data=parsed_data)


if __name__ == '__main__':
    app.run(debug=True)
