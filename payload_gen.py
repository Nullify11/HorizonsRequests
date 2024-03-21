"""
@author: Kasper
"""

import numpy as np
import time
import itertools

##### Old code, might be useful?
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
#####

#startTime = time.time()

def payload_dict(H, A, EC, In, MA, OM, W, Epoch=2460310.5, G=0.15):
    """
    Constructs the payload dictionaries needed for JPL Horizons api.
    
    Parameters
    ----------
    H : float
        The absolute magnitude.
    A : float
        The semi-major axis in AU
    EC : float
        The eccentricity
    In : float
        The inclination wrt. ecliptic
    MA : float
        The mean anomoly
    OM : float
        the longitude of ascending node wrt. ecliptic, degrees
    W : float
        Argument of perihelion wrt. ecliptic, degrees
    Epoch : float
        The Julian date number of the epoch. Standard is 2460310.5, i.e. 2024-Jan-01
    G : float
        The magnitude of slope. Standard is .15


    Returns
    -------
    payload : dictionary
        Part of the dictionary needed for JPL Horizons api.
    
    """
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
    #Generates Longitude of ascending node wrt. ecliptic as a random number in [0,360)
    long_asc_node = np.random.uniform(0,360,num_lines)
    return long_asc_node

def arg_of_perihelion(num_lines):
    #Generates perihelion as a random number in [0,360)
    arg_peri = np.random.uniform(0,360,num_lines)
    return arg_peri

# orbital_elements might be more clear than orbital_stats,
# both in this function and in the variable names elsewhere. -CN
def get_orbital_stats(txtname):
    """
    Reads the output file from Neomod2, which gives four of the needed nine elements.
    
    Parameters
    ----------
    txtname : str
        The name of the outputfile from Neomod2

    Returns
    -------
    orbit_stats : tuple
        A tuple of the four elements from Neomod2 (i.e. H, A, EC, IN), the mean anomoly, the
        longitude of the ascending node, the argument of the perihelion, the epoch and the
        magnitude of slope. I.e a tuple looking like (H, A, EC, IN, MA, OM, W, Epoch, G)
    
    """
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
    # Flattens the given list.
    return [leaf for tree in forrest for leaf in tree]
    #return list(itertools.chain.from_iterable(forrest))
    #Flattens a list, i.e. un-nesting a list.

def payload_generator(txtname):
    """
    Generates a list of tuples, where the tuples have a length 2. The first entry in 
    the tuple is the payload dictionay and the second is an identification number.
    Moreover, it stores this list in a file called payloads.txt for safekeeping.
    
    Parameters
    ----------
    txtname : str
        The name of the outputfile from Neomod2

    Returns
    -------
    payload_list : List
        A list of tuples, where the tuples have a length 2. The first entry in 
        the tuple is the payload dictionay and the second is an identification number.
    
    """
    payload_list = []
    orbit_stats = get_orbital_stats(txtname)
    for i in range(0,len(orbit_stats),1):
        payload_list.append(tuple([payload_dict(*orbit_stats[i])])+(i,))
    #Generates a list of tuples, where the tuples have a length 2.
    #The first entry in the tuple is the payload dictionay and the second is an indicator number.
    
    #Writes the generated payloads list. Just in case :)
    with open("payloads.txt","w") as f:
        for line in payload_list:
            f.write(f"{line}\n")
    
    return payload_list


def pay_gen_lock(txtname, lock):
    """
    Returns a list of payloads similar to that of payload_generator but with a lock instance appended to each tuple
    """
    payloads = payload_generator(txtname)
    lock_payloads = []
    for p in payloads:
        lock_payload = p + (lock,)
        lock_payloads.append(lock_payload)
    return lock_payloads


##################################### For testing
#get_orbital_stats("output_file-2")
#print(get_orbital_stats("output_file-2"))
#payload_generator("output_file_1000000")

#print(f"\nScript took {time.time() - startTime} seconds to run.")  # print elapsed time
#####################################
