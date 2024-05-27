from aiogram import types


# Клавиатура
kb = [[types.KeyboardButton(text='📄 Описание'),
       types.KeyboardButton(text='❌ Стоп')],
      [types.KeyboardButton(text='▶️ Старт')]
      ]
keyboard = types.ReplyKeyboardMarkup(
    keyboard=kb,
    resize_keyboard=True,
    input_field_placeholder="Категория товаров WB:")