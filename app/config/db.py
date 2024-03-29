import psycopg2
import os

class DBManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ['POSTGRES_HOST_DB'],
            database=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'])

    def get_connection(self):
        return self.conn
    
connection = DBManager().get_connection()