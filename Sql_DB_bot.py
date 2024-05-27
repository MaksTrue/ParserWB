import sqlite3


class ParsingWB_DB2:
    def __init__(self):
        self.db_name = sqlite3.connect('ParsingWB_v2.db')
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

    async def insert_data(self, data):
            self.cursor.executemany('''
                INSERT OR REPLACE INTO Products (Category, Article, Name, Rating, Reviews, Price, Link)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', data)
            self.db_name.commit()

    def close_connection(self):
        self.db_name.close()