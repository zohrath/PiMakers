import sqlite3

def create_test_db():

    conn=sqlite3.connect('testdb.db') #TODO: specify directory
    print("Database created and opened succesfully")

    c = conn.cursor()

    c.execute("CREATE TABLE columns(id int PRIMARY KEY, name string)")
    c.execute("CREATE TABLE measurements(id int, date int, time int, measurement int), PRIMARY KEY(id, date, time));")

