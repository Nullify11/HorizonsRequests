# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 14:22:17 2024

@author: chris
"""

import time
import requests
import random as rand
import numpy as np

startTime = time.time()

def generate_payload(payload):
    payload['EC'] = "'" + str(rand.uniform(0, 1)) + "'"
    return payload

def gen_payload_arr(payload, size):
    payloads = []
    for i in range(size):
        payloads.append(generate_payload(payload))
    return np.array(payloads)
        

payload = {
    "format": "text",
    "COMMAND": "';'",   #User-specified small object
    "OBJECT": "'USER_OBJECT'", #Object name
    "ECLIP": "'J2000'",     #Reference ecliptic
    "EPOCH": "'2460329.5'", #Epoch
    "EC": "'.375492882708177'", #Eccentricity
    "QR": "'.8346468735827693'", #Perihelion distance
    "TP": "'2460377.6797868409'", #Perihelion Julian Day number (i.e. where on the curve is our object starting)
    "OM": "'300.1183759806364'", #Longitude of ascending node wrt. ecliptic
    "W": "'243.6585063469079'", #Argument of perihelion wrt. ecliptic
    "IN": "'7.293072730272614'", #Inclination wrt. ecliptic
    "H": "'32.741'", #Absolute magnitude
    "G": "'.150'", #Magnitude slope; can be < 0
    "OBJ_DATA": "'NO'", #Yes, we want the response to tell us the objects inputdata, i.e. the above commands
    "MAKE_EPHEM": "'YES'", #Yes, we would like to see the calculated ephemeris
    "EPHEM_TYPE": "'APPROACH'", #Use close "APPROACH" table or the "VECTORS" table (there is an OBSERVERS table too)
    "CENTER": "'500@0'", #500 for geocentric, 500@0 for sol barycenter, 500@3 for Earth-Moon barycenter
    "START_TIME": "'JD 2458849.5'", #Y-M-D or JD xxxxx  JD 2460329. (2024-01-20)  JD 2460361. (2024-01-21)
    "STOP_TIME": "'JD 2634166.5'",
    "STEP_SIZE": "'1d'",
    #"QUANTITIES": "'1,9'",    #20,23,24,29'",  Only relevant for observer EPHEM_TYPE
}


def get_response(payload, i):
    response = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params=payload)

    print(f"\nScript took {time.time() - startTime} seconds to run.") 

    file_path = f"response{i}.txt"
    with open(file_path, "w") as outfile:
        outfile.write(response.text)


def vectorize_and_time():
    t0 = time.time()

    vfunc = np.vectorize(get_response)
    vfunc(gen_payload_arr(payload, 10), np.arange(10))

    t1 = time.time()

    print(t1)

vectorize_and_time()


