import mysql.connector
import numpy as np
import os

hs_db = mysql.connector.connect(
  host='localhost',
  user='root',
  password='',
  database='hs_db'
)

cursor = hs_db.cursor()

#def extract_foreign_keys(min_CA_dist):
#    cursor.execute(f"SELECT foreign_keys from close_approaches WHERE CA_Dist <= {min_CA_dist}")
#    result = cursor.fetchall()
#    return [fk(0) for fk in result]

def extract_elements(min_CA_dist):
    cursor.execute(f'SELECT primary_key, `ec`, qr, tp, om, w, `in`, h \
        FROM asteroids \
        INNER JOIN close_approaches \
        ON asteroids.primary_key = close_approaches.foreign_key \
        WHERE close_approaches.CA_Dist <= {min_CA_dist}')
    result = cursor.fetchall()
    return result

#http://www.braeunig.us/space/plntpos.htm
def plotting_file(min_CA_dist):
    elements_list = extract_elements(min_CA_dist)
    str_elements_list = [str(element) for element in elements_list]
    with open(f'plotting_files/plotting{min_CA_dist}.txt','w') as file:
        for tup in str_elements_list:
            a = tup[2]/(1-tup[1])
            file.write(str(tup).strip('()').replace(',','')+f' {a}')
    print(f'Created plotting file for {min_CA_dist}')


def cumulative_freq(min_CA_dist):
    cursor.execute(f'SELECT foreign_key, vrel \
        FROM close_approaches \
        WHERE CA_Dist <= {min_CA_dist}')
    result = cursor.fetchall()
    
    #Gravitational constant, the mass of the Earth, and the radius of the Earth
    gravitational_constant = 6.67*10**(-11) # N*m^2*kg^-2
    mass_of_Earth = 5.976*10**(24) # kg
    r_Earth = 4.2635*10**(-5) # AU
    
    prob_dict = {}
    for i in range(len(result)):
        id, relV = result[i]
        grav_radius = ((2*gravitational_constant*mass_of_Earth)/(relV**2))*6.6845871226706*10**(-12) # AU    
        cross_section_Earth = np.pi*(r_Earth+grav_radius)**2
        cross_section_AU = np.pi*0.1**2
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
        for key in prob_dict:
            file.write('Total cumulative impact frequency:', total_cumulative_freq, \
                '\nSlow asteroids and their impact frequency before adjustment:',\
                str(slow_ast).strip('[]'))
            file.write(str(key),str(prob_dict[key]))
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
file_creation(0.00001)
file_creation(r_Earth) #Kun for impacts