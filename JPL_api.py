import time
import requests
import sample_payload as sample

startTime = time.time()

response = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params=sample.payload)

print(f"\nScript took {time.time() - startTime} seconds to run.") 

file_path = "response.txt"
with open(file_path, "w") as outfile:
    outfile.write(response.text)

