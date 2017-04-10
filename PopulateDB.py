import sqlite3
import os.path
import

def create_db():

    if os.path.exists('/home/felix/Documents/testtest.db'):
        print("Database already exists")
    else:
        try:
            conn=sqlite3.connect('/home/felix/Documents/testtest.db') #TODO: specify directory
            print("Database created and opened succesfully")
            c = conn.cursor()
            c.execute("CREATE TABLE columns(id int PRIMARY KEY, name string);")
            c.execute("CREATE TABLE measurements(id int, date text, time text, measurement real, PRIMARY KEY(id, date, time));")
            conn.close()
        except:
            Print("Something went wrong")

create_test_db()
