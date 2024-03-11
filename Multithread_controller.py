# -*- coding: utf-8 -*-
"""
@author: Kasper
"""

import time
import multithread_JPL as jp
import Filter_responses as fi
import payload_Gen as pg


def reset():
    # Resets the succes_response, errors_response, and total_errors files.
    with open("success_response.txt","w") as f:
        pass
    with open("total_errors.txt","w") as f:
        pass
    with open("errors_response.txt","w") as f:
        pass

def controller(num_requests,num_workers,boundary,payload_file):
    """
    Controls the program. Runs the "user interface", generates the payloads needed,
    starts the threads, and filters the responses. And it times how long it takes for all
    the wished requests to be created.

    Parameters:
    -----------
    num_requests : Int
        Number of requests the user wants. I.e. the number of simulated asteroids the user
        will recieve.
    
    num_workers : Int
        The number of maximum threads at one time.
    
    boundary : Int or float
        The number of missing requests for which the program will stop using threads and
        "fill the holes" one by one.

    payload_file : str
        The total name of the output file from Neomod2 including .txt.
    
    Returns:
    --------
        time_of_start : float
            The time when the program starts making requests to JPL Horizons.
        
        time_of_end : float
            The time when the program is done making requests to JPL Horizons.
    """
    ### <User interface>
    print("*"*45)
    with open("success_response.txt","r") as f:
        previous_success = len(f.readline().split())
    while True:
        print(f"You have {previous_success} valid responses from JPL Horizons from last session.")
        ask_reset = input("Do you want to continue from last session? [y/n]: ")
        if ask_reset.lower() in ["n","no"]:
            reset()
            print("Success responses and total errors has been reset.")
            break
        elif ask_reset.lower() in ["y","yes"]:
            print("Will continue from last threading.")
            break
        else:
            print("Please enter valid response.")
    print(f"Will make {num_requests} requests with {num_workers} threads and a boundary value of {boundary}.\
        \nThis will take approximately {round((1.37*boundary+num_requests/1.7)/60,8)} minutes or {round((1.37*boundary+num_requests/2)/(60*60),8)} hours.")
    print("*"*45)
    input("Press enter to continue ")
    print("*"*45)
    ### <\User interface>
    
    # Actually requesting JPL Horizons
    time_of_start = time.time()
    print("Makes payloads.")
    payloads = pg.payload_generator(payload_file)
    print("Starts threads (The number k constitutes to the number of recursive threading).")
    
    jp.retry_requests(num_requests,num_workers,payloads,boundary)
    
    time_of_end = time.time()
    print("*"*45)
    
    # Filter responses
    while True:
        ask_impacts =input("Run number of impacts? [y/n]: ")
        if ask_impacts.lower() in ["y","yes"]:
            d, nr_CA = fi.filter("response")
            print("Nr. of impacts:", sum(d.values()))
            print("Nr. of CA with Earth:", nr_CA)
            break
        elif ask_impacts.lower() in ["n","no"]:
            break
        else:
            print("Please enter valid response.")
    return time_of_start, time_of_end


########### Control environment

start_time, end_time = controller(100,5,10,"output_file_10000")

###########

elapsed_time = end_time - start_time
print(f'Total elapsed Time: {round(elapsed_time/60,5)} minutes or {round(elapsed_time/(60*60),5)} hours.')