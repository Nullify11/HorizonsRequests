# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 18:08:03 2024

@author: chral
"""

import time
import requests
import random as rand
import sample_payload as sample
from concurrent.futures import ThreadPoolExecutor


def generate_payload(payload):
    """
    Generates a payload with a new eccentricity based on an existing payload
    """
    payload['EC'] = "'" + str(rand.uniform(0, 1)) + "'"
    return payload


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
    response = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params=payload[0])

    file_path = f"response{payload[1]}.txt"
    with open(file_path, "w") as outfile:
        outfile.write(response.text)


# specifies the number of requests to send
num_requests = 10

# specify the number of threads
num_workers = 3

start_time = time.time()

with ThreadPoolExecutor(max_workers=num_workers) as executor:
    executor.map(get_response, [(generate_payload(sample.payload), i) for i in range(num_requests)])

end_time = time.time()
elapsed_time = end_time - start_time
print(f'Elapsed Time: {elapsed_time}')
