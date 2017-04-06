import sqlite3
import time



def check_if_index_exist(index):
    try:
        conn = sqlite3.connect('/home/felix/LocalDatabase.db');
        cur = conn.cursor()
    except:
        print("second connection didnt work")

    try:
        replacement = (index,)
        sqlstatement = "select id from channels where id = ?"
        cur.execute(sqlstatement, replacement)
        value = cur.fetchone()
        conn.close()
    except:
        print("The select query didnt work")
    if value == None:
       return False
    else:
       return True

def add_to_database(list_of_items):
    date = time.strftime("%Y-%m-%d")    #TODO check if this should be done here or ir main
    timeofvalue = time.strftime("%H:%M:%S")
    try:
        conn = sqlite3.connect('/home/felix/LocalDatabase.db');
        print("connected to database");
    except:
        print("Something went wrong1");
    try:
        for index in list_of_items:

            id = index
            list = list_of_items[index]
            name = list[0]
            measurementvalue = list[1]

            found = check_if_index_exist(id)

            print(found)
            if found:
                conn.execute("INSERT INTO measurements VALUES(?,?,?,?)", (id, date, timeofvalue, measurementvalue))
            else:
                conn.execute("INSERT INTO channels VALUES(?, ?)", (id, name))
                conn.execute("INSERT INTO measurements VALUES(?,?,?,?)", (id, date, timeofvalue, measurementvalue))

        conn.commit()
        conn.close()
    except:
        print("wrong with adding")
        conn.rollback()





list = {100: ['Hej', 10]};
add_to_database(list)
