"""
@author: Kasper
"""

import numpy as np
import time
import itertools

"""file = open(txtname+".txt", "r")
    i=0
    while True:
        content = file.readline().split()
        #orbit_stats[i] = tuple([float(i) for i in flatten([content,[float(mean_anom[i])]])])+(1,1,1,1)
        orbit_stats[i] = tuple([float(i) for i in content])+(1,1,1,1)
        #I think assigning might be slightly faster than appending.
        #orbit_stats.append(tuple([float(i) for i in content])+(1,1,1,1,1))
        if i == 5:
            break
        if not content:
            break
        i+=1
    file.close()
    orbit_stats.pop(-1)"""

startTime = time.time()

def payload_dict(H, A, EC, In, MA, OM, W, Epoch=2460310.5, G=0.15):
    payload = {
        "H": f"'{H}'", #Absolute magnitude
        "A": f"'{A}'", #Semi-major axis
        "EC": f"'{EC}'", #Eccentricity
        "IN": f"'{In}'", #Inclination wrt. ecliptic
        "MA": f"'{MA}'", #Mean anomaly
        "OM": f"'{OM}'", #Longitude of ascending node wrt. ecliptic
        "W": f"'{W}'", #Argument of perihelion wrt. ecliptic
        "EPOCH": f"'{Epoch}'", #Epoch, 2460310.5 = 2024-Jan-01
        "G": f"'{G}'", #Magnitude slope; can be < 0
    }
    return payload

def mean_anomaly(num_lines):
    #Generates mean anomaly (MA) as a random number in [0,360)
    mean_anom = np.random.uniform(0,360,num_lines)
    return mean_anom

def long_of_ascending_node(num_lines):
    #Generates mean anomaly (MA) as a random number in [0,360)
    long_asc_node = np.random.uniform(0,360,num_lines)
    return long_asc_node

def arg_of_perihelion(num_lines):
    #Generates mean anomaly (MA) as a random number in [0,360)
    arg_peri = np.random.uniform(0,360,num_lines)
    return arg_peri

def get_orbital_stats(txtname):
    #Counts the number of lines in txtname
    with open(txtname+".txt", "r+b") as f:
        num_lines = sum(1 for _ in f)
    mean_anom = mean_anomaly(num_lines) 
    long_asc_node = long_of_ascending_node(num_lines)
    arg_peri = arg_of_perihelion(num_lines)
    
    orbit_stats = [0]*(num_lines+1)  #np.zeros(num_lines+1, dtype=object)
    
    with open(txtname+".txt", "r") as file:
        i=0
        while True:
            if i == num_lines:
                break
            content = file.readline().split() #reads and spilts data into the first four orbital elements needed in the payload.
            orbit_stats[i] = tuple([float(j) for j in flatten([content,[float(mean_anom[i])],[float(long_asc_node[i])],[float(arg_peri[i])]])])+(2460310.5,0.15)
            #The above makes the i'th entry in orbit_stats a tuple of the four orbital elements from txtname.txt and the five generated elements.
            #I think assigning might be slightly faster than appending.
            #orbit_stats.append(tuple([float(i) for i in content])+(1,1,1,1,1))
            if not content:
                break
            i+=1
    orbit_stats.pop(-1)
    return orbit_stats

def flatten(forrest):
    return [leaf for tree in forrest for leaf in tree]
    #return list(itertools.chain.from_iterable(forrest))
    #Flattens a list, i.e. un-nesting a list.

def payload_generator(txtname):
    payload_list = []
    orbit_stats = get_orbital_stats(txtname)
    for i in range(0,len(orbit_stats),1):
        payload_list.append(tuple([payload_dict(*orbit_stats[i])])+(i,))
    #Generates a list of tuples, where the tuples have a length 2.
    #The first entry in the tuple is the payload dictionay and the second is an indicator number.
    return payload_list


#get_orbital_stats("output_file-2")
#print(get_orbital_stats("output_file-2"))
payload_generator("output_file_1000000")

print(f"\nScript took {time.time() - startTime} seconds to run.")  # print elapsed time
