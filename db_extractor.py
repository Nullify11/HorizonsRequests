import mysql.connector
import numpy as np
import os
import db_credentials as db_cred

hs_db = mysql.connector.connect(
  host='localhost',
  user='root',
  password=db_cred.password,
  database='hs_db'
)

cursor = hs_db.cursor()

#def extract_foreign_keys(min_CA_dist):
#    cursor.execute(f"SELECT foreign_keys from close_approaches WHERE CA_Dist <= {min_CA_dist}")
#    result = cursor.fetchall()
#    return [fk(0) for fk in result]

def count_lines(file_path):
    with open(f'{file_path}.txt', 'rb') as f:
        num_lines = sum(1 for _ in f)
    return num_lines

def extract_elements(min_CA_dist):
    cursor.execute(f'SELECT asteroids.id, asteroids.`ec`, asteroids.qr, asteroids.tp, asteroids.om, asteroids.w, asteroids.`in`, asteroids.h \
        FROM asteroids \
        INNER JOIN close_approaches \
        ON asteroids.id = close_approaches.fk_asteroid_id \
        WHERE close_approaches.ca_dist <= {min_CA_dist} AND close_approaches.body = "Earth"')
    result = cursor.fetchall()
    return result

#http://www.braeunig.us/space/plntpos.htm
def plotting_file(min_CA_dist):
    elements_list = extract_elements(min_CA_dist)
    print("SQL done")
    already_inserted = []
    number_of_CA = 0
    with open(f'plotting_files/plotting{min_CA_dist}.txt', 'w') as file:
        for tup in elements_list:
            number_of_CA += 1
            try:
                a = str(float(tup[2])/(1-float(tup[1])))
            except:
                print(tup[2],tup[1])
                a = None
            if tup[0] not in already_inserted:
                file.write(str(tup).strip('()').replace(',','')+f' {a}\n')
                already_inserted.append(tup[0])
            if len(already_inserted) >= 2:
                already_inserted.pop(0)
    number_of_unique_CA = count_lines(f'plotting_files/plotting{min_CA_dist}')
    with open(f'plotting_files/stats{min_CA_dist}.txt', 'w') as file:
        file.write(f'Statistics for {min_CA_dist}\nNumber of CA: {number_of_CA}\nNumber of unique CA asteroids: {number_of_unique_CA}')
    print(f'Created plotting file for {min_CA_dist}')


def cumulative_freq(min_CA_dist):
    cursor.execute(f'SELECT fk_asteroid_id, vrel \
        FROM close_approaches \
        WHERE ca_dist <= {min_CA_dist} AND body = "Earth"')
    result = cursor.fetchall()
    
    #Gravitational constant, the mass of the Earth, and the radius of the Earth
    gravitational_constant = 6.67*10**(-11) # N*m^2*kg^-2
    mass_of_Earth = 5.976*10**(24) # kg
    r_Earth = 4.2635*10**(-5) # AU
    
    prob_dict = {}
    for i in range(len(result)):
        id, relV = result[i]
        relV = relV*1000 #conversion to m/s
        grav_radius = ((2*gravitational_constant*mass_of_Earth)/(relV**2))*6.6845871226706*10**(-12) # AU    
        cross_section_Earth = np.pi*(r_Earth+grav_radius)**2
        cross_section_AU = np.pi*min_CA_dist**2
        impact_probability = cross_section_Earth/cross_section_AU
        if id in prob_dict:
            prob_dict[id] = prob_dict[id] + impact_probability
        else:
            prob_dict[id] = impact_probability
    
    slow_ast = []
    for key in prob_dict:
        if prob_dict[key] > 1:
            slow_ast.append((key, prob_dict[key]))
            prob_dict[key] = 1
    
    total_cumulative_freq = sum(prob_dict.values())
    print(f'Cumulative frequency for {min_CA_dist}:', total_cumulative_freq)
    with open(f'impact_files/cumulative_freq{min_CA_dist}.txt','w') as file:
        file.write(f'Total cumulative impact frequency: {total_cumulative_freq}\n')
        file.write(f'Slow asteroids and their impact frequency before adjustment:\n')
        file.write(str(slow_ast).strip('[]'))
    print(f'Created cumulative frequency file for {min_CA_dist}')

def create_responses_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def file_creation(min_CA_dist):
    create_responses_dir('plotting_files')
    plotting_file(min_CA_dist)

    create_responses_dir('impact_files')
    cumulative_freq(min_CA_dist)

# File creation
r_Earth = 4.2635*10**(-5) # AU

file_creation(0.1)
file_creation(0.01)
file_creation(0.001)
file_creation(0.0001)
file_creation(r_Earth) #Kun for impacts