import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             #password='passwd',
                             db='nurre',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `Test` (`Name`, `age`) VALUES ('Bertil', 40)"
        cursor.execute(sql)

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()

    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * FROM Test WHERE age<50"
        cursor.execute(sql) #, ('webmaster@python.org',))
        result = cursor.fetchone()
        print(result)
finally:
    connection.close()





