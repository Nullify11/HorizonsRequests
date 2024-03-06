# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 18:08:03 2024

@author: chral
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor
import payload_Gen as pg

# Files to keep track of which payloads came through succesfully and which do not.
with open("success_response.txt","w") as f:
    pass
with open("errors_response.txt","w") as f:
    pass
with open("total_errors.txt","w") as f:
    pass

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
        with open("success_response.txt", "a") as file:
            file.write(f"{payload[1]} ")
    else:
        with open("errors_response.txt", "a") as file:
            file.write(f"{payload[1]} ")

def correct_errors(retry,payloads):
    """
    Sends an API request to JPL horizons for all failed requests and saves the response as a text file
    
    Parameters
    ----------
    payloads : List
        Payloads is a list of tuples which contains all the payloads and their identicators.
        Each tuple contains the payload as its first element and
        a unique identifier for its second element

    Returns
    -------
    "All done!" when done
    
    """
    #error_i = []
    # Creates an error_i list which is the list of all the failed requests
    #with open("errors_response.txt","r") as f:
    #    while True:
    #        content = f.readline().split()
    #        error_i.append(content)
    #        if not content:
    #            break

    #error_i = pg.flatten(error_i)
    
    # If the list is empty, all request went through succesfully
    #if not error_i:
    #    return print("All done!")
    # Removes an empty entry at the end of the list.
    #error_i.pop(-1)
    
    # Sends a new request, one at a time (i.e. the slow way), for all the errors.
    # If any fails a the identicator is noted in total_erros.txt
    
    for k in retry:
        i = int(k) #int(error_i[k])
        response = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params= setup | payloads[i][0])
        if "API VERSION" not in response.text[:11]:
            print("Oui!",i)
            with open("total_errors.txt","a") as file:
                file.write(f"{payloads[i][1]} ")
        else:
            file_path = f"response{payloads[i][1]}.txt"
            with open(file_path, "w") as outfile:
                outfile.write(response.text)
            #print("Non!",i)
    return print("All done!")



def thread_forge(retry,num_workers,payloads):
    #retry = [j for j in range(num_requests)]

    
    #with open("success_response.txt","r") as f:
    #    content = f.readline().split()
    #    j = 0
    #    while True:
    #        if j == len(content):
    #            break
    #        i = content[j]
    #        retry.remove(int(i))
    #        j += 1
    
    # If the list is empty, all request went through succesfully
    #if not retry:
    #    return print("All done!")
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        executor.map(get_response, [payloads[i] for i in retry])

def retry_requests(num_requests,num_workers,payloads,boundary):
    retry = [j for j in range(num_requests)]

    k=0
    while len(retry) > boundary:
        k +=1
        with open("success_response.txt","r") as f:
            content = f.readline().split()
            j = 0+num_requests-len(retry)
            while True:
                if j == len(content):
                    break
                i = content[j]
                retry.remove(int(i))
                j += 1
        print(retry)
        # If the list is empty, all request went through succesfully
        if not retry:
            return print("All done!")
        thread_forge(retry,num_workers,payloads)
    correct_errors(retry,payloads)


# specifies the number of requests to send
#num_requests = 1000

# specify the number of threads
#num_workers = 10

start_time = time.time()

payloads = pg.payload_generator(f"output_file_100") 

retry_requests(100,6,payloads,10)

print("Done with threads")

# corrects any errors by taking one at a time.
#correct_errors(payloads)

end_time = time.time()
elapsed_time = end_time - start_time
print(f'Elapsed Time: {elapsed_time}')
