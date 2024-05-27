import asyncio
import logging
import sys
import requests
import locale

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold
from aiogram import F
import Buttons as bt
import Text as txt
from Sql_DB_bot import ParsingWB_DB2

TOKEN = 'Вставить токен'

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
db = ParsingWB_DB2()

stop_parsing = False


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    global stop_parsing
    stop_parsing = False
    await message.reply(f'Добро пожаловать, {hbold(message.from_user.full_name)} !\n'
                        f'\n'
                        f'{txt.greeting_message}', reply_markup=bt.keyboard)


@dp.message(F.text.lower() == '📄 описание')
async def description(message: types.Message):
    await message.answer(f'{txt.description}')


@dp.message(F.text.lower() == '❌ стоп')
async def description(message: types.Message):
    global stop_parsing
    stop_parsing = True
    await message.answer('Если что-то нужно вы знаете где меня найти!')


@dp.message(F.text.lower() == '▶️ старт')
async def description(message: types.Message):
    global stop_parsing
    stop_parsing = False
    await message.answer('Давайте начнем парсить, введите категорию')


@dp.message()
async def search_wildberries(message: types.Message) -> None:
    search = message.text

    url = f'https://search.wb.ru/exactmatch/ru/common/v4/search?TestGroup=pk2_alpha05&TestID=351&appType=1&curr=rub' \
          f'&dest=-1257786&query={search}&resultset=catalog&sort=popular&spp=26&suppressSpellcheck=false'

    resp = requests.get(url)
    resp.encoding = 'utf-8'
    locale.setlocale(locale.LC_ALL, '')
    Id_product = [i['id'] for i in resp.json()['data']['products']]
    Name = [n['name'] for n in resp.json()['data']['products']]
    Raiting = [r['reviewRating'] for r in resp.json()['data']['products']]
    Feedback = [f['feedbacks'] for f in resp.json()['data']['products']]
    Cost = [locale.format_string('%d', c['salePriceU'] // 100, grouping=True) for c in resp.json()['data']['products']]
    Url_product = [f'https://www.wildberries.ru/catalog/{u}/detail.aspx?targetUrl=XS' for u in Id_product]

    data_to_insert = []
    for i, n, r, f, c, u in zip(Id_product, Name, Raiting, Feedback, Cost, Url_product):
        if stop_parsing:
            break

        message_text = f"Категория: {search}\nАртикул: {i}\nНазвание: {n}\n" \
                       f"Рейтинг: {r}\nОтзывы: {f}\nЦена: {c} руб.\nСсылка: {u}\n\n"
        await message.answer(message_text)

        category = search
        article = i
        name = n
        rating = r
        reviews = f
        price = c
        link = u

        data_to_insert.append((category, article, name, rating, reviews, price, link))

    await db.insert_data(data_to_insert)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    db.close_connection()
