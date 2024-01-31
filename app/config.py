import os
import psycopg2


class DBManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="db",
            database="db_comic",
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'])

    def get_connection(self):
        return self.conn
