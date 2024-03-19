"""
@author: Kasper
Filters responses from JPL Horizons
"""
import os
import requests

def CAEarth(txtname,tolerance=4.2635*10**(-5)):
    """
    Looks through the created responses and notes how many close approaches to Earth each
    asteroid has, and if it impacts with the Earth.
    
    Parameters
    ----------
    txtname : str
        The name of what the response files the function will look through. Must be .txt 
        files and the .txt must not be stated in txtname.
    
    tolerance : float
        The added tolarance to the Earth's radius. The radius is chosen because the CA 
        table from JPL Horizons gives the nominal closet approach to the centre of the 
        Earth. The standard value is set to the Earths radius.
        The unit is in AU.

    Returns
    -------
    Tuple : The tuple consists of two values, a bool and a integer.
    The bool depends on if the asteroid hit or not.
    The integer counts how many closed approaches the asteroids have collectivly.
    
    """
    file = open("responses/"+txtname+".txt", "r")
    lis=[]
    while True:
        content = file.readline()
        if "Earth  " in content:
            lis.append(content)
        if not content:
            break
    file.close()
    
    nr_CA = len(lis)
    if not lis:
        nr_CA = 0
        return False, nr_CA
    
    #Gravitational konstant and the mass of the Earth
    G = 6.67*10**(-11) # N*m^2*kg^-2
    M = 5.976*10**(24) # kg
    for i in range(0,len(lis),1):
        relV = float(lis[i][43:49])*1000 # m/s
        r_g = ((2*G*M)/(relV**2))*6.6845871226706*10**(-12) # AU
        # The index [33:41] corrosponds to the number of characters in the line from the
        # response, where the CA distance is.
        if float(lis[i][33:41]) < 4.2635*10**(-5)+r_g+tolerance:
            print(f"Asteroid {txtname.replace('response', '')} impacted!")
            print(f"CA distance: {lis[i][33:41]}, Earth radius + gravitational lensing: {4.2635*10**(-5)+r_g+tolerance}", r_g, tolerance)
            return True, nr_CA
    return False, nr_CA

def filter(txtname,tolerance=1*10**(-4)):
    """
    Filters the responses and retruns a dictionary which notes if an asteroid impacts with
    the Earth, and it returns the number of close approaches.
    
    Parameters
    ----------
    txtname : str
        The name of what the response files the function will look through. Must be .txt 
        files and the .txt must not be stated in txtname.
    
    tolerance : float
        The added tolarance to the Earth's radius. The radius is chosen because the CA 
        table from JPL Horizons gives the nominal closet approach to the centre of the 
        Earth. The standard value is set to the Earths radius.
        The unit is in AU.

    Returns
    -------
    Tuple : The tuple consists of two values, a dictionary and a integer.
    The dictionary is composed of a key which is each of the responses where the value is a
    bool which depends on if the asteroid hit or not.
    The integer counts how many closed approaches the asteroids have collectivly.
    
    """
    d = dict()
    # As multithread_JPL may skip some payloads as the response for
    # those may not be valid, we read the success_response file and iterate over these.
    with open("success_response.txt") as f:
        succes_content = list(f.readline().split())
    succes_content = [int(i) for i in succes_content]
    CAs = 0
    for i in succes_content:
        impact, nr_CA = CAEarth(txtname+str(i),tolerance)
        CAs = CAs + nr_CA
        d[txtname+str(i)] = impact
    return d, CAs

def filter_all(txtname, start_at=0, tolerance=4.2635*10**(-5)):
    d = dict()
    no_responses = len(os.listdir("responses/"))
    succes_content = [int(i) for i in range(start_at, no_responses+start_at, 1)]
    CAs = 0
    for i in succes_content:
        impact, nr_CA = CAEarth(txtname+str(i),tolerance)
        CAs = CAs + nr_CA
        d[txtname+str(i)] = impact
    return d, CAs

def impact_stats(txtname, iden, tolerance=4.2635*10**(-5)):
    file = open("responses/"+txtname+".txt", "r")
    lis=[]
    while True:
        content = file.readline()
        if "Earth  " in content:
            lis.append(content)
        if not content:
            break
    file.close()
    
    nr_CA = len(lis)
    print(f"NEO {iden} had {nr_CA} CA with the Earth.")

    G = 6.67*10**(-11) # N*m^2*kg^-2
    M = 5.976*10**(24) # kg
    for i in range(0,len(lis),1):
        relV = float(lis[i][43:49])*1000 # m/s
        r_g = ((2*G*M)/(relV**2))*6.6845871226706*10**(-12) # AU
        # The index [33:41] corrosponds to the number of characters in the line from the
        # response, where the CA distance is.
        if float(lis[i][33:41]) < 4.2635*10**(-5)+r_g+tolerance:
            print(lis[i])
            print(f"NEO {iden} has a CA distance of {float(lis[i][33:41])},\na gravitational radius of {r_g} AU, and a relative velocity of {float(lis[i][43:49])} km/s")
            return

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

def ast_impact(d, payloads):
    response_keys = [key for key, val in d.items() if val == 1 or val == True]

    for key in response_keys:
        i = int(key.replace('response', ''))
        impact_stats(key, i)
        response = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params= setup | payloads[i][0])
        print(f"NEO {i} used the API url:\n", response.url)

a, b = filter_all("response",166667)
print(sum(a.values()),b) # For testing
ast_impact(a,0)
# 0 159933, for 0-166667
# 0 159487, for 333333-499998