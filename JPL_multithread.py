# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 18:08:03 2024

@author: chral
"""

import time
import requests
import random as rand
from concurrent.futures import ThreadPoolExecutor
import payload_Gen as pg

setup = {
    "format": "text",
    "COMMAND": "';'",   #User-specified small object
    "OBJECT": "'USER_OBJECT'", #Object name
    "ECLIP": "'J2000'",     #Reference ecliptic
    "OBJ_DATA": "'NO'", #No, we do not want the response to tell us the objects inputdata, i.e. the above commands, since they are shown again in the EPHEM table
    "MAKE_EPHEM": "'YES'", #Yes, we would like to see the calculated ephemeris
    "EPHEM_TYPE": "'APPROACH'", #Use close "APPROACH" table or the "VECTORS" table (there is an OBSERVERS table too)
    "CENTER": "'500@0'", #500 for geocentric, 500@0 for Sol barycenter, 500@3 for Earth-Moon barycenter
    "START_TIME": "'JD 2458849.5'", #Y-M-D or JD xxxxx  JD 2460329. (2024-01-20)  JD 2460361. (2024-01-21)
    "STOP_TIME": "'JD 2515097.5'",
    "STEP_SIZE": "'150y'",
    #"TCA3SG_LIMIT": "'14400'",
    #"CALIM_SB": "'0.05'",
    #"CALIM_PL": "'.1, .1, .1, .1, 1.0, 1.0, 1.0, 1.0, .1, .003'",
    #"QUANTITIES": "'1,9'",    #20,23,24,29'",  Only relevant for observer EPHEM_TYPE
}


def generate_payload(payload):
    """
    Generates a payload with a new eccentricity based on an existing payload
    """
    payload['EC'] = "'" + str(rand.uniform(0, 1)) + "'"
    return payload

def get_response(payload):
    """
    Sends an API request to JPL horizons and saves the response as a text file
    
    Parameters
    ----------
    payload : Tuple
        Payload is a tuple that contains the payload as its first element and
        a unique identifier for the created text file as its second element

    Returns
    -------
    None.

    """
    response = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params= setup | payload[0])
    file_path = f"response{payload[1]}.txt"

    with open(file_path, "w") as outfile:
        outfile.write(response.text)



# specifies the number of requests to send
num_requests = 10

# specify the number of threads
num_workers = 3

start_time = time.time()

payloads = pg.payload_generator("output_file") #output_file is a sample file of ten payloads needed in the generator

with ThreadPoolExecutor(max_workers=num_workers) as executor:
    executor.map(get_response, [payloads[i] for i in range(num_requests)])

#for i in range(10):
#    print("https://ssd.jpl.nasa.gov/api/horizons.api", f"?{setup | payloads[i][0]}")

end_time = time.time()
elapsed_time = end_time - start_time
print(f'Elapsed Time: {elapsed_time}')
