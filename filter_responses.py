"""
@author: Kasper
Filters responses from JPL Horizons
"""
import os
import requests
import numpy as np
import itertools
import sys

def CAEarth(txtname, pause = False):
    """
    Looks through the created responses and notes how many close approaches to Earth each
    asteroid has, and if it impacts with the Earth.
    
    Parameters
    ----------
    txtname : str
        The name of what the response files the function will look through. Must be .txt 
        files and the .txt must not be stated in txtname.

    Returns
    -------
    Tuple : The tuple consists of two values, a bool, an integer, and another bool.
    The first bool depends on if the asteroid hit or not.
    The integer counts how many closed approaches the asteroids have collectivly.
    The second bool depends on if the asteroid had a CA with the Earth or not.
    
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
    
    # If the list is empty, no close approaches happened and there could therefore
    # not have been an impact either.
    if not lis:
        nr_CA = 0
        return False, nr_CA, False, 0
    nr_CA = len(lis)
    
    iden = txtname.replace('response', '')
    impact = impact_Earth(lis, iden, pause)
    impact_probability = CA_impact_probabitlity(lis)
    return impact, nr_CA, True, impact_probability

def impact_Earth(CA_list, iden, pause = False):
    """
    Looks through the created responses and notes how many close approaches to Earth each
    asteroid has, and if it impacts with the Earth.
    
    Parameters
    ----------
    CA_list : list
        A list of strings of every CA in the particular file.
    
    iden : str, float or int
        The identification number of the particular asteroid.
    
    pause : bool
        A bool which lets the user see the impact result before continuing.

    Returns
    -------
    bool which depends on the asteroid impacting the Earth or not.
    
    """
    for i in range(0,len(CA_list),1):
        # The index [33:41] corrosponds to the number of characters in the line from the
        # response, where the CA distance is.
        if float(CA_list[i][33:41]) < 4.2635*10**(-5):
            if pause == True:
                print(f"Asteroid {iden} impacted!")
                print(f"CA distance: {CA_list[i][33:41]}\nEarth radius: {4.2635*10**(-5)}\nRelative velocity: {CA_list[i][43:49]}")
                input("Press enter to continue")
            return True
    return False

def CA_impact_probabitlity(CA_list):
    """
    Calculates the probabitilty that an asteriod impacts with the Earth on it's close
    approach with the Earth. It does this by dividing the cross section of the Earth's
    radius + the gravitational capture radius by the cross section of radius 0.1 AU.
    
    Parameters
    ----------
    CA_list : list
        A list of strings of every CA in the particular file.

    Returns
    -------
    asteroid_impact_probability : float
        The probability that this particular asteroid impacts during one of it's CA.
    
    """
    #Gravitational constant, the mass of the Earth, and the radius of the Earth
    gravitational_constant = 6.67*10**(-11) # N*m^2*kg^-2
    mass_of_Earth = 5.976*10**(24) # kg
    r_Earth = 4.2635*10**(-5) # AU
    # The relative velocity (relV) is found at the indicies [43:49] in the string from
    # the JPL Horizons txt file.
    asteroid_impact_probability = 0
    for i in range(0,len(CA_list),1):
        relV = float(CA_list[i][43:49])*1000 # m/s
        grav_radius = ((2*gravitational_constant*mass_of_Earth)/(relV**2))*6.6845871226706*10**(-12) # AU
        cross_section_Earth = np.pi*(r_Earth+grav_radius)**2
        cross_section_AU = np.pi*0.1**2
        impact_probability = cross_section_Earth/cross_section_AU
        asteroid_impact_probability = asteroid_impact_probability + impact_probability
    return asteroid_impact_probability



def filter_all(txtname, start_at=0):
    """
    Filters the responses into which impacted with the Earth, how many close approaches
    (CA) did the asteroids collectivly have, and how many unique asteroids made a CA.
    The function retruns a dictionary which notes if an asteroid impacts with
    the Earth, it returns the number of close approaches, and the number of unique
    asteroids with CA with the Earth.
    
    Parameters
    ----------
    txtname : str
        The name of what the response files the function will look through. Must be .txt 
        files and the .txt must not be stated in txtname.
    
    start_at : int
        The response file number the filter should start at. Note that it runs for a 
        total number of how many files are in the "response/" directory, so it will 
        return an error if one starts at a number such that
        the number of files in the directory + start_at exceeds the greatest response
        file number.

    Returns
    -------
    Tuple : The tuple consists of three values, a dictionary and two integers.
    The dictionary is composed of a key which is each of the responses where the value is a
    bool which depends on if the asteroid hit or not.
    The first integer counts how many close approaches the asteroids have collectivly.
    The second integer counts how many unique asteroids had a CA with the Earth
    
    """
    impact_dict = dict()
    nr_responses = len(os.listdir("responses/"))
    succes_content = [int(i) for i in range(start_at, nr_responses+start_at, 1)]
    CAs = 0
    unique_CA_asteroids = 0
    total_impact_probability = 0
    # A spinner to see that the program is running as intended.
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    # We check each response file in the "responses/" directory using this script as an anchor.
    for i in succes_content:
        #print(i)
        impact, nr_CA, did_CA, impact_probability = CAEarth(txtname+str(i))
        unique_CA_asteroids = unique_CA_asteroids + int(did_CA)
        CAs = CAs + nr_CA
        if impact_probability > 1:
            print(i,impact_probability)
            impact_probability = 1
        total_impact_probability = total_impact_probability + impact_probability
        impact_dict[txtname+str(i)] = impact
        sys.stdout.write(next(spinner))  # write the next character
        sys.stdout.flush()                      # flush stdout buffer (actual character display)
        sys.stdout.write('\b')                 # erase the last written char
    return impact_dict, CAs, unique_CA_asteroids, total_impact_probability

# Does it carry over from payload_gen when it is imported into multithread_controller?
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
    "STEP_SIZE": "'1d'",
    #"TCA3SG_LIMIT": "'14400'",
    #"CALIM_SB": "'0.05'",
    "CALIM_PL": "'0, 0, .1, 0, 0, 0, 0, 0, 0, 0'",
    #"QUANTITIES": "'1,9'",    #20,23,24,29'",  Only relevant for observer EPHEM_TYPE
}

def ast_impact(impact_dict, payloads):
    """
    If and when an asteroid impacts, this function finds and presents which asteroids impacted, 
    at what distance, at what relative velocity, what the radius criteria for an impact is, the 
    gravitational capture radius, and the url for which the JPL Horizons 
    system calculated this particular asteroid.
    
    Parameters
    ----------
    impact_dict : dictionary
        A dictionary containing a bool as a value, depending on if the asteroid impacted or not,
        where the keys are the individual name of the response files.
    
    payloads : list
        A list of tuples, where the tuples have a length 3. The first entry in 
        the tuple is the payload dictionary, the second is an identification number, and
        the third being a thread lock. Only the two first are used here.

    Returns
    -------
    None
    
    """
    while True:
        ask = input("Should the program pause for every impact? [y/n]: ")
        if ask.lower() in ["y","yes"]:
            ask_pause = True
            break
        elif ask.lower() in ["n","no"]:
            ask_pause = False
            break
        print("Please enter a valid response")

    response_keys = [key for key, val in impact_dict.items() if val == 1 or val == True]

    for key in response_keys:
        i = int(key.replace('response', ''))
        CAEarth(key, pause = ask_pause)
        response = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params= setup | payloads[i][0])
        print(f"NEO {i} used the API url:\n", response.url)

################################################ For testing
#a, b, c, d = filter_all("response",1000)
#print(sum(a.values()),b, c, d) 
#ast_impact(a,"test")
# 0 159933 50993, for 0-166666      Kasper
# 2 160246 51217, for 166667-333332 Carsten
# 0 159487 50814, for 333333-499998 Lasse
# 1 159932 51017, for 499999-666664 Christina
# 3 159081 50830, for 666665-833332 Magnus
