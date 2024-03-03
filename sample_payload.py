# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 18:25:00 2024

@author: chral
File containing a sample payload that is guaranteed to have a
very close approach with earth.
"""

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
