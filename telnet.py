# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 16:33:56 2024

@author: chral

currently unfinished
"""

import telnetlib as telnet

def get_command_string(values:dict):
    command = ''
    for key in values:
        command += f'{key}= {values[key]} '
    return command


values = {
    "EPOCH": "2460329.5", #Epoch
    "EC": ".375492882708177", #Eccentricity
    "QR": ".8346468735827693", #Perihelion distance
    "TP": "2460377.6797868409", #Perihelion Julian Day number (i.e. where on the curve is our object starting)
    "OM": "300.1183759806364", #Longitude of ascending node wrt. ecliptic
    "W": "243.6585063469079", #Argument of perihelion wrt. ecliptic
    "IN": "7.293072730272614", #Inclination wrt. ecliptic
    "H": "32.741", #Absolute magnitude
    "G": ".150", #Magnitude slope; can be < 0
}


HOST = 'horizons.jpl.nasa.gov'
PORT = 6775

command = get_command_string(values)

# telnet unfinished test request (Kasper has made a longer one that works)
tn = telnet.Telnet(HOST, PORT)
print(tn.read_until(b'Horizons>'))
tn.write(b';\n')
print(tn.read_until(b':'))
tn.write(b'EPOCH= 2460329.5 EC= .375492882708177 QR= .8346468735827693 TP= 2460377.6797868409 OM= 300.1183759806364 W= 243.6585063469079 IN= 7.293072730272614 H= 32.741 G= .150')
print(tn.read_until(b':'))
tn.write(b'\r\n')
print(tn.read_until(b':'))
tn.write(b'J200\n')
print(tn.read_until(b':'))
tn.write(b'BOB\n')
print(tn.read_all())
tn.close()





