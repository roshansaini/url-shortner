import sqlite3

conn=sqlite3.connect("Url.db")
print("Database created Successfully")

conn.execute('''
            CREATE TABLE URLTABLE (
            ID INTEGER PRIMARY KEY AUTOINCREMENT ,
            URL TEXT  UNIQUE NOT NULL ,
            SURL TEXT UNIQUE NOT NULL
            )
            ''')

print("Table created Successfully")
conn.close()