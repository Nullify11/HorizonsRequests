# -*- coding: utf-8 -*-
"""
@author: Kasper
"""

import time
import multithread_JPL as jp #
import filter_responses as fi
import payload_gen as pg
import threading
import numpy as np

def reset():
    # Resets the succes_response, errors_response, and total_errors files.
    # worked fine, but just adding in some close statements - CN (you can delete this comment once you see it)
    f = open("success_response.txt","w")
    f.close()
    f = open("total_errors.txt","w") 
    f.close()
    f = open("errors_response.txt","w")
    f.close()

def controller(num_requests, num_workers, boundary, payload_file, start_at=0):
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
        
    start_at : int
        Tells the program which response file it should start at.
    
    Returns:
    --------
        time_of_start : float
            The time when the program starts making requests to JPL Horizons.
        
        time_of_end : float
            The time when the program is done making requests to JPL Horizons.
    """
    
    jp.create_responses_dir()
    ### <User interface>
    print("*"*50)
    with open("success_response.txt","r") as f:
        previous_success = len(f.readline().split())
    while True:
        print(f"You have {previous_success} valid responses from JPL Horizons from last session.")
        ask_reset = input("Do you want to continue from last session? [y/n]: ")
        if ask_reset.lower() in ["n","no"]:
            reset()
            print("Success responses and total errors has been reset.")
            with open("payload_seed.txt","w") as file:
                new_seed = np.random.randint(0,1000000)
                np.random.seed(new_seed)
                file.write(f"{new_seed}")
            print("Making new payloads.")
            payloads = pg.pay_gen_lock(payload_file, threading.Lock())
            break
        elif ask_reset.lower() in ["y","yes"]:
            print("Will continue from last session with the same payloads.")
            with open("payload_seed.txt","r") as file:
                prev_seed = int(file.readline())
            np.random.seed(prev_seed)
            print("Making previous payloads.")
            payloads = pg.pay_gen_lock(payload_file, threading.Lock())
            break
        else:
            print("Please enter valid response.")
    print(f"Will make {num_requests} requests with {num_workers} threads and a boundary value of {boundary}.\
        \nThis will take approximately {round((1.37*boundary+num_requests/1.7)/60,5)} minutes or {round((1.37*boundary+num_requests/2)/(60*60),5)} hours.")
    print("*"*50)
    input("Press enter to continue ")
    print("*"*50)
    ### <\User interface>
    
    # Actually requesting JPL Horizons
    time_of_start = time.time()
    
    print("Starts threads (The number k constitutes to the number of recursive threading).")
    
    jp.retry_requests(num_requests, num_workers, payloads, boundary, start_at)
    
    time_of_end = time.time()
    print("*"*45)
    
    # Filter responses
    d, nr_CA, unique_CA_asteroids, total_impact_probability = fi.filter_all("response",start_at)
    print("Nr. of impacts:", sum(d.values()))
    print("Nr. of CA with Earth:", nr_CA)
    print("Nr. of unique asteroids with a CA with Earth:", unique_CA_asteroids)
    print("Total probability of impact:", total_impact_probability)
    fi.ast_impact(d, payloads)
    return time_of_start, time_of_end


########### Control environment

#start_time, end_time = controller(163667, 5, 10, "output_file_1000000", 3000)

###########

#elapsed_time = end_time - start_time
#print(f'Total elapsed Time: {round(elapsed_time/60,5)} minutes or {round(elapsed_time/(60*60),5)} hours.')
