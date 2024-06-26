import mysql.connector
import db_converter as converter
import db_credentials as credentials
import os
import re

hs_db = mysql.connector.connect(
  host = 'localhost',
  user = 'root',
  password = credentials.password,
  database = 'hs_db'
)

def insert_directory(dir_path, directory_num):
  errors = converter.detect_errors(dir_path)
  initial_index = 1000000 * directory_num
  directory = os.listdir(dir_path)
  for i in range(len(directory)):
    if directory[i] not in errors:
      id = initial_index + int(re.findall(r'\d+', directory[i])[0])
      file_path = dir_path + '\\' + directory[i]
      insert_item(file_path, id)
  
  print(f'Insert for directory {dir_path} succesful!')


def insert_item(path, id):
  data = converter.retrieve_data(path, id)
  cursor = hs_db.cursor()

  asteroid_exist = is_in_asteroids(id)

  # notify duplicate asteroid entry
  # if asteroid_exist:
    # print(f'duplicate asteroid entry found for {id} (duplicate ignored)')

  # Insert asteroid data if it does not exist
  if not asteroid_exist:
    sql_insert_asteroid = "INSERT INTO asteroids " + converter.sql_asteroid_fields() + " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql_insert_asteroid, converter.sql_asteroid_values(data))


  for ca in data['close_approaches']:
    ca_exists = is_in_ca(ca[0], ca[-1])

    # notify ca already exists
    # if ca_exists:
      # print(f'duplicate ca entry found for date: {ca[0]} and foreign key {ca[-1]} (duplicate ignored)')

    if not ca_exists:
      sql_insert_close_approach = 'INSERT INTO close_approaches ' + converter.sql_ca_fields() + ' VALUES (%s, %s, %s, %s, %s)'
      cursor.execute(sql_insert_close_approach, tuple(ca))
  
  hs_db.commit()


def is_in_asteroids(id):
  cursor = hs_db.cursor()
  query = 'SELECT id FROM asteroids WHERE id = %s'
  count = cursor.execute(query, (id,))
  result = cursor.fetchone()
  cursor.fetchall()
  return False if result == None else True


def is_in_ca(date:str, fk_asteroid_id):
  cursor = hs_db.cursor()
  query = 'SELECT id FROM close_approaches WHERE date = %s AND fk_asteroid_id = %s'
  count = cursor.execute(query, (date, fk_asteroid_id))
  result = cursor.fetchone()
  cursor.fetchall()
  return False if result == None else True

# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\responses_ONE', 0)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\responses_TWO', 1)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\responses_THREE', 2)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\responses_FOUR', 3)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\responses_FIVE', 4)

# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Christina\\responses_Christina_ONE', 0)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Christina\\responses_Christina_TWO', 1)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Christina\\responses_Christina_THREE', 2)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Christina\\responses_Christina_FOUR', 3)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Christina\\responses_Christina_FIVE', 4)

# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Carsten\\responses_Carsten_ONE', 0)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Carsten\\responses_Carsten_TWO', 1)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Carsten\\responses_Carsten_THREE', 2)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Carsten\\responses_Carsten_FOUR', 3)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Carsten\\responses_Carsten_FIVE', 4)

# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Magnus\\responses_Magnus_ONE', 0)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Magnus\\responses_Magnus_TWO', 1)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Magnus\\responses_Magnus_THREE', 2)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Magnus\\responses_Magnus_FOUR', 3)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Magnus\\responses_Magnus_FIVE', 4)

# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Lasse\\responses_Lasse_ONE', 0)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Lasse\\responses_Lasse_TWO', 1)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Lasse\\responses_Lasse_THREE', 2)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Lasse\\responses_Lasse_FOUR', 3)
# insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Lasse\\responses_Lasse_FIVE', 4)

insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Kasper\\responses_Kasper_ONE', 0)
insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Kasper\\responses_Kasper_TWO', 1)
insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Kasper\\responses_Kasper_THREE', 2)
insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Kasper\\responses_Kasper_FOUR', 3)
insert_directory('C:\\Users\\chral\\OneDrive\\Skrivebord\\all_responses\\Kasper\\responses_Kasper_FIVE', 4)

# practice_insert('responses_THREE', 3833331)
