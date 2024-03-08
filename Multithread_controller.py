# -*- coding: utf-8 -*-
"""
@author: Kasper
"""

import time
import multithread_JPL as jp
import Filter_responses as fi
import payload_Gen as pg


def reset():
    with open("success_response.txt","w") as f:
        pass
    with open("total_errors.txt","w") as f:
        pass

def controller(num_requests,num_workers,boundary,payload_file):
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
        \nThis will take approximately {round((1.37*boundary+num_requests/2)/60,8)} minutes or {round((1.37*boundary+num_requests/2)/(60*60),8)} hours.")
    print("*"*45)
    input("Press enter to continue ")
    
    time_of_start = time.time()
    print("Makes payloads.")
    payloads = pg.payload_generator(payload_file)
    print("Starts threads (The number k constitutes to the number of recursive threading).")
    jp.retry_requests(num_requests,num_workers,payloads,boundary)
    time_of_end = time.time()
    while True:
        ask_impacts =input("Run number of impacts? [y/n]: ")
        if ask_impacts.lower() in ["y","yes"]:
            print("Nr. of impacts:",sum(fi.filter("response",num_requests).values()))
            break
        elif ask_impacts.lower() in ["n","no"]:
            break
        else:
            print("Please enter valid response.")
    return time_of_start, time_of_end


########### Control environment

start_time, end_time = controller(100,3,1,"output_file_1000")

###########

elapsed_time = end_time - start_time
print(f'Total elapsed Time: {elapsed_time/60} minutes or {elapsed_time/(60*60)} hours.')