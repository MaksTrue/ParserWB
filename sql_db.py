import sqlite3


class ParsingWB_DB:
    def __init__(self):
        self.db_name = sqlite3.connect('ParsingWB.db')
        self.cursor = self.db_name.cursor()
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Products (
                        Category TEXT,
                        Article TEXT PRIMARY KEY,
                        Name TEXT,
                        Rating REAL,
                        Reviews INTEGER,
                        Price TEXT,
                        Link TEXT
                    )
                ''')
        self.db_name.commit()

    def insert_data(self, data):
        data_to_save_sql = []
        for item in data:
            entry = (
                item['Категория'],
                item['Результаты']['Артикул'],
                item['Результаты']['Наименование'],
                item['Результаты']['Рейтинг'],
                item['Результаты']['Количетсво отзывов'],
                item['Результаты']['Цена'],
                item['Результаты']['Ссылка']
            )
            data_to_save_sql.append(entry)

        self.cursor.executemany('''
            INSERT OR REPLACE INTO Products (Category, Article, Name, Rating, Reviews, Price, Link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', data_to_save_sql)
        self.db_name.commit()

    def close_connection(self):
        self.db_name.close()