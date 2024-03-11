# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 18:08:03 2024

@author: chral
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor
import payload_gen as pg
import os


###################################### For testing
# Files to keep track of which payloads came through succesfully and which do not.
#with open("success_response.txt","w") as f:
#    pass
#with open("errors_response.txt","w") as f:
#    pass
#with open("total_errors.txt","w") as f:
#    pass
######################################

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
    
    # All correct data starts by listing the API version, so we check if gives this response.
    # If it does, we write the text out as usual and add the indicator to a .txt document
    # to keep track of which payloads came through succesfully. If the API version is not listed
    # we do not write the file, but instead write the indicator in another file.
    
    if "API VERSION" in response.text[:11]:
        file_path = f"response{payload[1]}.txt"
        with open(file_path, "w") as outfile:
            outfile.write(response.text)
        # payload[2] contains an instance of a lock
        with payload[2]:
            with open("success_response.txt", "a") as file:
                file.write(f"{payload[1]} ")

def correct_errors(retry, payloads):
    """
    Sends an API request to JPL horizons for all failed requests and saves the response as a text file
    
    Parameters
    ----------
    retry : List
        retry is a list of all the identicators must be run through JPL Horizons
    
    payloads : List
        Payloads is a list of tuples which contains all the payloads and their identicators.
        Each tuple contains the payload as its first element and
        a unique identifier for its second element

    Returns
    -------
    "All done!" when done
    
    """

    # Sends a new request, one at a time (i.e. the slow way), for all the errors.
    # If any fails a the identicator is noted in total_erros.txt
    
    for k in retry:
        i = int(k) #int(retry[k])
        response = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params= setup | payloads[i][0])
        # All valid responses start with the API version. If they fail the one-by-one we note them in total_errors
        if "API VERSION" not in response.text[:11]:
            print("Oui!",i)
            with open("total_errors.txt","a") as file:
                file.write(f"{payloads[i][1]} ")
        else:
            file_path = f"response{payloads[i][1]}.txt"
            with open(file_path, "w") as outfile:
                outfile.write(response.text)
            # Due to how python handles threads opening and closing succes_response
            # most of the files writes correctly into the file. However, every once in a
            # while it will fail to do so, so we check if it indeed is in the file, and
            # if not we write it. Just be on the safe side, we run the response and write
            # out the .txt file anyway.
            with open("success_response.txt", "r+") as file:
                if str(payloads[i][1]) in list(file.readline().split()):
                    print(payloads[i][1],"Already in success_response")
                else:
                    file.write(f"{payloads[i][1]} ")
    return print("All done!")

def thread_forge(retry, num_workers, payloads):
    """
    Handles the threads
    
    Parameters
    ----------
    retry : List
        retry is a list of all the identicators must be run through JPL Horizons.
    
    num_workers : Int
        The number of maximum threads at one time.
    
    payloads : List
        Payloads is a list of tuples which contains all the payloads and their identicators.
        Each tuple contains the payload as its first element and
        a unique identifier for its second element.

    Returns
    -------
    None
    
    """
   
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        executor.map(get_response, [payloads[i] for i in retry])

def retry_requests(num_requests, num_workers, payloads, boundary):
    """
    A psedo-recursive function which runs the thread_forge function with the given retry
    list, until the number of needed requests is reached or below a boundary value.
    
    Parameters
    ----------
    num_requests : Int
        Number of requests the user wants. I.e. the number of simulated asteroids the user
        will recieve.
    
    num_workers : Int
        The number of maximum threads at one time.
    
    payloads : List
        Payloads is a list of tuples which contains all the payloads and their identicators.
        Each tuple contains the payload as its first element and
        a unique identifier for its second element.
    
    boundary : Int or float
        The number of missing requests for which the program will stop using threads and
        "fill the holes" one by one.

    Returns
    -------
    "All done!" if the list retry is empty
    
    """
    
    retry = [j for j in range(num_requests)]

    k=0
    while len(retry) > boundary:
        k +=1
        print("k:",k)
        with open("success_response.txt","r") as f:
            content = f.readline().split()
        content = [int(i) for i in content]
        retry = [item for item in retry if item not in content]
        # If the list is empty, all request went through succesfully
        if not retry:
            return print("All done!")
        thread_forge(retry, num_workers, payloads)
    print("Done with threads")
    correct_errors(retry, payloads)


def create_responses_dir():
    path = 'responses'
    if not os.path.exists(path):
        os.makedirs(path)
###################################################
# For testing
#start_time = time.time()

#payloads = pg.payload_generator("output_file_1000") 

#retry_requests(10,5,payloads,10)


# corrects any errors by taking one at a time.
#correct_errors(payloads)

#end_time = time.time()
#elapsed_time = end_time - start_time
#print(f'Elapsed Time: {elapsed_time}')
####################################################