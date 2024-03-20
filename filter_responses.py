"""
@author: Kasper
Filters responses from JPL Horizons
"""
import os
import requests

def CAEarth(txtname, tolerance=0, pause = False):
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
        Earth. The standard value is set to 0.
        The unit is in AU.

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
        return False, nr_CA, False
    nr_CA = len(lis)
    
    iden = txtname.replace('response', '')
    impact = impact_Earth(lis, iden, tolerance, pause)
    return impact, nr_CA, True

def impact_Earth(CA_list, iden, tolerance, pause = False):
    """
    Looks through the created responses and notes how many close approaches to Earth each
    asteroid has, and if it impacts with the Earth.
    
    Parameters
    ----------
    CA_list : list
        A list of strings of every CA in the particular file.
    
    iden : str, float or int
        The identification number of the particular asteroid.

    tolerance : float
        The added tolarance to the Earth's radius. The radius is chosen because the CA 
        table from JPL Horizons gives the nominal closet approach to the centre of the 
        Earth. The standard value is set to 0.
        The unit is in AU.
    
    pause : bool
        A bool which lets the user see the impact result before continuing.

    Returns
    -------
    bool which depends on the asteroid impacting the Earth or not.
    
    """
    #Gravitational constant and the mass of the Earth
    gravitational_constant = 6.67*10**(-11) # N*m^2*kg^-2
    mass_of_Earth = 5.976*10**(24) # kg
    # The relative velocity (relV) is found at the indicies [43:49] in the string from
    # the JPL Horizons txt file.
    for i in range(0,len(CA_list),1):
        relV = float(CA_list[i][43:49])*1000 # m/s
        grav_radius = ((2*gravitational_constant*mass_of_Earth)/(relV**2))*6.6845871226706*10**(-12) # AU
        # The index [33:41] corrosponds to the number of characters in the line from the
        # response, where the CA distance is.
        if float(CA_list[i][33:41]) < 4.2635*10**(-5)+grav_radius+tolerance:
            if pause == True:
                print(f"Asteroid {iden} impacted!")
                print(f"CA distance: {CA_list[i][33:41]}\nEarth radius + gravitational capture + tolerance: {4.2635*10**(-5)+grav_radius+tolerance}", \
                    f"\nGravitational capture: {grav_radius}\nTolerance: {tolerance}\nRelative velocity: {CA_list[i][43:49]}")
                input("Press enter to continue")
            return True
    return False

def filter_all(txtname, start_at=0, tolerance=0):
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
    
    tolerance : float
        The added tolarance equal to the Earth's radius. The radius is chosen because the CA 
        table from JPL Horizons gives the nominal closet approach to the centre of the 
        Earth. The standard value is set to 0.
        The unit is in AU.

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
    # We check each response file in the "responses/" directory using this script as an anchor.
    for i in succes_content:
        print(i)
        impact, nr_CA, did_CA = CAEarth(txtname+str(i),tolerance)
        unique_CA_asteroids = unique_CA_asteroids + int(did_CA)
        CAs = CAs + nr_CA
        impact_dict[txtname+str(i)] = impact
    return impact_dict, CAs, unique_CA_asteroids

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
    "STEP_SIZE": "'150y'",
    #"TCA3SG_LIMIT": "'14400'",
    #"CALIM_SB": "'0.05'",
    #"CALIM_PL": "'.1, .1, .1, .1, 1.0, 1.0, 1.0, 1.0, .1, .003'",
    #"QUANTITIES": "'1,9'",    #20,23,24,29'",  Only relevant for observer EPHEM_TYPE
}

def ast_impact(impact_dict, payloads):
    """
    If and when an asteroid impacts, this function finds and presents which asteroids impacted, 
    at what distance, at what relative velocity, what the radius criteria for an impact is, the 
    gravitational capture radius, the tolerance level, and the url for which the JPL Horizons 
    system calculated this particular asteroid.
    
    Parameters
    ----------
    impact_dict : dictionary
        A dictionary containing a bool as a value, depending on if the asteroid impacted or not,
        where the keys are the individual name of the response files.
    
    payloads : list
        A list of tuples, where the tuples have a length 3. The first entry in 
        the tuple is the payload dictionay, the second is an identification number, and
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
#a, b, c = filter_all("response",0)
#print(sum(a.values()),b, c) 
#ast_impact(a,"test")
# 0 159933 50993, for 0-166666      Kasper
# 2 160246 51217, for 166667-333332 Carsten
# 0 159487 50814, for 333333-499998 Lasse
# 1 159932 51017, for 499999-666664 Christina
# 3 159081 50830, for 666665-833332 Magnus