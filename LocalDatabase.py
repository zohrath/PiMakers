import sqlite3
import time



def check_if_index_exist(index):
    try:
        conn = sqlite3.connect('/home/felix/LocalDatabase.db')
        cursor = conn.execute("SELECT id FROM channels where id = ?", (index))
        conn.close()
        found = false

    except:
        print("something went wrong")
    return found

def add_to_database(list_of_items):
    date = time.strftime("%Y-%m-%d")    #TODO check if this should be done here or ir main
    timeofvalue = time.strftime("%H:%M:%S")
    try:
        conn = sqlite3.connect('/home/felix/LocalDatabase.db');
        print("connected to database");
    except:
        print("Something went wrong");
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





list = {21: ['Hej', 10]};
add_to_database(list)