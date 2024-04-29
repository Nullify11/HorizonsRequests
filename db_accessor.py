import db_credentials as credentials
import mysql.connector

hs_db = mysql.connector.connect(
  host = 'localhost',
  user = 'root',
  password = credentials.password,
  database = 'hs_db'
)

def length(table_name):
    sql = 'SELECT id FROM ' + table_name
    cursor = hs_db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    return len(result)


def select_one_asteroid(id):
    sql = 'SELECT * FROM asteroids WHERE id = ' + str(id)
    cursor = hs_db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# For testing
print(length('asteroids'))
print(length('close_approaches'))
# result = select_one_asteroid(4999999)
# print(type(result))
# print(result[0][13])