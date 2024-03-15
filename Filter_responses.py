"""
@author: Kasper
Filters responses from JPL Horizons
"""
import os

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
    
    for i in range(0,len(lis),1):
        # The index [33:41] corrosponds to the number of characters in the line from the
        # response, where the CA distance is.
        if float(lis[i][33:41]) < 4.2635*10**(-5)+tolerance:
            return True, nr_CA
        else:
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

def filter_all(txtname, start_at, tolerance=1*10**(-4)):
    d = dict()
    no_responses = len(os.listdir("responses/"))
    succes_content = [int(i) for i in range(start_at, no_responses, 1)]
    CAs = 0
    for i in succes_content:
        impact, nr_CA = CAEarth(txtname+str(i),tolerance)
        CAs = CAs + nr_CA
        d[txtname+str(i)] = impact
    return d, CAs

#print(sum(filter("response")[0].values()),filter("response")[1]) # For testing