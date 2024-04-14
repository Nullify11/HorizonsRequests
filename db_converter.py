import re

def retrieve_data(file_path, id):
    data = {'id' : id}
    file = open(file_path, "r")
    line = file.readline()

    # Finds the line where the word EPOCH first occurs in file
    while 'EPOCH' not in line:
        line = file.readline()

    # Setup regular expression
    numeric_const_pattern = r'[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
    rx_numbers = re.compile(numeric_const_pattern, re.VERBOSE)

    # Appends relevant data to the data dictionary
    data.update(create_dictionary(['ec', 'qr', 'tp'], rx_numbers.findall(file.readline())))
    data.update(create_dictionary(['om', 'w', 'in'], rx_numbers.findall(file.readline())))
    file.readline()
    data.update(create_dictionary(['x', 'y', 'z'], rx_numbers.findall(file.readline())))
    data.update(create_dictionary(['vx', 'vy', 'vz'], rx_numbers.findall(file.readline())))
    
    # Read and append the H value
    file.readline()
    file.readline()
    lst = list_convert(file.readline())[0 : 2]
    data.update(dict_convert(lst))

    # Read until close approaches
    data.update({'close_approaches' : []})
    while 'Close-approach results:' not in line:
        line = file.readline()
    file.readline()
    file.readline()
    file.readline()

    # Append close approaches
    line = file.readline()
    while 'A.D.' in line:
        data['close_approaches'].append(ca_convert(line, id))
        line = file.readline()

    file.close()
    return data


def ca_convert(line, id):
    lst = line.split()
    lst = [lst[1] + ' ' + lst[2] + ' ' + lst[3]] + lst[-3:]
    lst[2] = float(lst[2])
    lst[3] = float(lst[3])
    lst.append(id)
    return lst


def list_convert(line):
    return line.replace('=', ' ').split()


def dict_convert(lst):
    res_dict = {lst[i].lower() : float(lst[i+1]) for i in range(0, len(lst), 2)}
    return res_dict


def sql_asteroid_fields():
    return '(id, `ec`, qr, tp, om, w, `in`, x, y, z, vx, vy, vz, h)'


def create_dictionary(letters, numbers):
    res_dict = {letters[i].lower() : float(numbers[i]) for i in range(len(numbers))}
    return res_dict


def sql_asteroid_values(dict):
    return tuple(dict.values())[:-1]


def sql_ca_fields():
    return '(' + 'date, body, ca_dist, vrel, fk_asteroid_id' + ')'


def str_to_float(list):
    return [float(i) for i in list]


def retrieve_data_test(file_path, id):
    data = {'id' : id}
    file = open(file_path, "r")
    line = file.readline()

    numeric_const_pattern = r'[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
    rx_numbers = re.compile(numeric_const_pattern, re.VERBOSE)

    # Finds the line where the word EPOCH first occurs in file
    while 'EPOCH' not in line:
        line = file.readline()
    
    # Appends relevant data to the data dictionary
    data.update(create_dictionary(['ec', 'qr', 'tp'], rx_numbers.findall(file.readline())))
    data.update(create_dictionary(['om', 'w', 'in'], rx_numbers.findall(file.readline())))
    file.readline()
    data.update(create_dictionary(['x', 'y', 'z'], rx_numbers.findall(file.readline())))
    data.update(create_dictionary(['vx', 'vy', 'vz'], rx_numbers.findall(file.readline())))

    # data.update(dict_convert(list_convert(file.readline())))
    # data.update(dict_convert(list_convert(file.readline())))

    file.close()
    return data


# For testing
# data = retrieve_data('responses_ONE\\response839132.txt', 839132)
# print(data)
# print(sql_asteroid_fields())
# print(sql_asteroid_values(data), type(sql_asteroid_values(data)))
# print(sql_ca_fields())
# print(tuple(data['close_approaches'][0]))

# ca = data['close_approaches'][0]
# ca_tuple = tuple(ca)
# print(ca_tuple, type(ca_tuple))