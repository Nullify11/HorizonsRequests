"""
This module is dedicated to extracting any relevant infomation from the established MySQL database hs_db.
"""

import mysql.connector
import numpy as np
import os
import db_credentials as db_cred

#The user might change depending on how the server is installed. 'root' refers to the top-level user.
#The password is of course one made by the user, hence why the module db_cred.password.py is not in the repository.
hs_db = mysql.connector.connect(
  host='localhost',
  user='root',
  password=db_cred.password,
  database='hs_db'
)

#The cursor points to where any information in the database we want to extract or alter.
cursor = hs_db.cursor()

def count_lines(file_path):
    """
    Counts the number of lines in the selected file.

    Parameters
    ----------
    file_path : str
        The path of where the selected file is located. Must be .txt 
        files and the .txt must not be stated in txtname.
    
    Returns
    -------
    num_lines : int
        The number of lines in the file.

    """
    with open(f'{file_path}.txt', 'rb') as f:
        num_lines = sum(1 for _ in f)
    return num_lines

def extract_elements(min_CA_dist):
    """
    Extracts the list of osculating elements of the NEOs with a close approach distance <= min_CA_dist with the Earth.

    Parameters
    ----------
    min_CA_dist : float
        The close approach distance for which the close approaches is chosen. 
        If the close approach has a close approach distance larger the min_CA_dist, that entry is disregarded.
    
    Returns
    -------
    result : list
        A list of tuples where each specified element in the cursor.execute() constitutes an element in the associated tuple.

    """
    #We only extracts the NEOs which has a close approach distance <= min_CA_dist with the Earth.
    #We extract the NEO's id number, it's eccentricity, it's perihelion distance, it's time of perihelion, it's longitude of ascending node wrt. ecliptic,
    #it's argument of perihelion wrt. ecliptic, it's inclination, and it's absolute magnitude.
    cursor.execute(f'SELECT asteroids.id, asteroids.`ec`, asteroids.qr, asteroids.tp, asteroids.om, asteroids.w, asteroids.`in`, asteroids.h \
        FROM asteroids \
        INNER JOIN close_approaches \
        ON asteroids.id = close_approaches.fk_asteroid_id \
        WHERE close_approaches.ca_dist <= {min_CA_dist} AND close_approaches.body = "Earth"')
    result = cursor.fetchall()
    return result

def extract_close_approach(min_CA_dist):
    """
    Extracts the list of particular data of the NEOs with a close approach distance <= min_CA_dist with the Earth.

    Parameters
    ----------
    min_CA_dist : float
        The close approach distance for which the close approaches is chosen. 
        If the close approach has a CA distance larger the min_CA_dist, that entry is disregarded.
    
    Returns
    -------
    result : list
        A list of tuples where each specified element in the cursor.execute() constitutes an element in the associated tuple.

    """
    cursor.execute(f'SELECT close_approaches.date, close_approaches.body, close_approaches.ca_dist, close_approaches.vrel, close_approaches.fk_asteroid_id \
        FROM asteroids \
        INNER JOIN close_approaches \
        ON asteroids.id = close_approaches.fk_asteroid_id \
        WHERE close_approaches.ca_dist <= {min_CA_dist} AND close_approaches.body = "Earth"')
    result = cursor.fetchall()
    return result

def plotting_file(min_CA_dist):
    """
    Constructs a file consisting of the id number and the osculating elements of the NEOs extracted from the database 
    using the function extract_elements(min_CA_dist).

    Parameters
    ----------
    min_CA_dist : float
        The close approach distance for which the close approaches is chosen. 
        If the close approach has a CA distance larger the min_CA_dist, that entry is disregarded.
    
    Returns
    -------
    None

    """
    elements_list = extract_elements(min_CA_dist)
    print("SQL done")
    already_inserted = []
    number_of_CA = 0
    with open(f'plotting_files/plotting{min_CA_dist}.txt', 'w') as file:
        for tup in elements_list:
            number_of_CA += 1
            try:
                #JPL Horizons operate solely on the perihelion distance qr and the time of perihelion tp. So, altough we have inputtet
                #the mean anomaly and the semi-major axis, these are not in the response files. We opt to recalculate the semi-major
                #axis from the eccentricity and the perihelion distance, rather than extracting it from the generated payloads -
                #these are the same values after all.
                a = str(float(tup[2])/(1-float(tup[1])))
            except:
                print(tup[2],tup[1])
                a = None
            if tup[0] not in already_inserted:
                file.write(str(tup).strip('()').replace(',','')+f' {a}\n')
                already_inserted.append(tup[0])
            #Since there are five million generated NEOs we remove previous entries from the already_inserted list to reduce 
            #computational time.
            if len(already_inserted) >= 2:
                already_inserted.pop(0)
    number_of_unique_CA = count_lines(f'plotting_files/plotting{min_CA_dist}')
    with open(f'plotting_files/stats{min_CA_dist}.txt', 'w') as file:
        file.write(f'Statistics for {min_CA_dist}\nNumber of CA: {number_of_CA}\nNumber of unique CA asteroids: {number_of_unique_CA}')
    print(f'Created plotting file for {min_CA_dist}')

def cumulative_freq(min_CA_dist):
    """
    Constructs a file consisting of the cumulative impact frequency of the NEOs extracted from the database 
    using the function extract_elements(min_CA_dist), as well as noting any NEO with a frequency over 1, and what
    this frequency was before reducing it to 1.

    Parameters
    ----------
    min_CA_dist : float
        The close approach distance for which the close approaches is chosen. 
        If the close approach has a CA distance larger the min_CA_dist, that entry is disregarded.
    
    Returns
    -------
    None

    """
    #If one where to specify the size of the concering NEOs also, create an INNER JOIN on the asteroids.id and the
    #foreign key from close_approaches and add "AND asteroids.h < {size of asteroid in h}" to the last line.
    cursor.execute(f'SELECT fk_asteroid_id, vrel \
        FROM close_approaches \
        WHERE ca_dist <= {min_CA_dist} AND body = "Earth"')
    result = cursor.fetchall()

    #Gravitational constant, the mass of the Earth, and the radius of the Earth
    gravitational_constant = 6.67*10**(-11) # N*m^2*kg^-2
    mass_of_Earth = 5.976*10**(24) # kg
    r_Earth = 4.2635*10**(-5) # AU
    
    #Calculating the cumulative impact frequency as in filter_responses.py.
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
    
    #Noting any slow moving asteroids and their impact frequency before reducing it to 1.
    slow_ast = []
    for key in prob_dict:
        if prob_dict[key] > 1:
            slow_ast.append((key, prob_dict[key]))
            prob_dict[key] = 1
    
    #Creating a file of the total cumulative impact frequency and the slow moving asteroids.
    total_cumulative_freq = sum(prob_dict.values())
    print(f'Cumulative frequency for {min_CA_dist}:', total_cumulative_freq)
    with open(f'impact_files/cumulative_freq{min_CA_dist}.txt','w') as file:
        file.write(f'Total cumulative impact frequency: {total_cumulative_freq}\n')
        file.write(f'Slow asteroids and their impact frequency before adjustment:\n')
        file.write(str(slow_ast).strip('[]'))
    print(f'Created cumulative frequency file for {min_CA_dist}')

def extract_no_ca():
    """
    Extracts osculating elements and the id of the NEOs which did not make a close approach and creates a file of these values.

    Parameters
    ----------
    None
    
    Returns
    -------
    None

    """
    cursor.execute('SELECT asteroids.id, asteroids.`ec`, asteroids.qr, asteroids.tp, asteroids.om, asteroids.w, asteroids.`in`, asteroids.h\
                    FROM asteroids\
                    WHERE id\
                    NOT IN (SELECT fk_asteroid_id FROM close_approaches WHERE body = "Earth")')
    result = cursor.fetchall()
    with open('plotting_files/plotting_no_CA.txt', 'w') as file:
        already_inserted = []
        for tup in result:
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
        
def extract_number_files():
    """
    Extracts the ids of the NEOs in the database and writes them in a seperate file on a single line.

    Parameters
    ----------
    None
    
    Returns
    -------
    None

    """
    cursor.execute('SELECT id FROM asteroids')
    result = cursor.fetchall()
    lis = [0]*5*(10**6)
    for tup in result:
        lis[tup[0]] = str(tup).strip('()').replace(',','')
    
    with open('plotting_files/number_files.txt', 'w') as file:
        file.write(str(lis).strip('[]').replace("'",'').replace(',',''))


def create_responses_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def file_creation(min_CA_dist):
    """
    The umbrella file creation function which initiates the extraction and the file creation.

    Parameters
    ----------
    min_CA_dist : float
        The close approach distance for which the close approaches is chosen. 
        If the close approach has a CA distance larger the min_CA_dist, that entry is disregarded.
    
    Returns
    -------
    None

    """
    create_responses_dir('plotting_files')
    plotting_file(min_CA_dist)

    create_responses_dir('impact_files')
    cumulative_freq(min_CA_dist)

def extract_sizes(min_h, max_h):
    """
    Prints how many asteroids are in different catagories of sizes determined by the absolute magnitude.

    Parameters
    ----------
    min_h : float
        The minimum allowed absolute magnitude.

    max_h : float
        The maximum allowed absolute magnitude.

    Returns
    -------
    None

    """
    print("Begin")
    cursor.execute(f'SELECT id \
        FROM asteroids \
        WHERE h > {min_h} AND h < {max_h}')
    resulta = cursor.fetchall()
    print("18<h<22",len(resulta))
    cursor.execute(f'SELECT id \
        FROM asteroids \
        WHERE h < {min_h}')
    resultb = cursor.fetchall()
    print("h<18",len(resultb))
    cursor.execute(f'SELECT id \
        FROM asteroids')
    resultc = cursor.fetchall()
    print("all",len(resultc))
    cursor.execute(f'SELECT id \
        FROM asteroids \
        WHERE h = {max_h}')
    resultd = cursor.fetchall()
    print("h=22",len(resultd))
    cursor.execute(f'SELECT id \
        FROM asteroids \
        WHERE h = {min_h}')
    resulte = cursor.fetchall()
    print("h=18",len(resulte))
    cursor.execute(f'SELECT id \
        FROM asteroids \
        WHERE h >= {max_h} OR h <= {min_h}')
    resultf = cursor.fetchall()
    print("h>=22 or h<=18",len(resultf))

#extract_sizes(18, 22)





# File creation
r_Earth = 4.2635*10**(-5) # AU

#file_creation(0.1)
#file_creation(0.01)
#file_creation(0.001)
#file_creation(0.0001)
#file_creation(r_Earth) #Only the impacts
#print(extract_close_approach(r_Earth))

#extract_no_ca()
extract_number_files()
