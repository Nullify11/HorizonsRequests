"""
@author: Kasper
Filters responses from JPL Horizons
"""

import numpy as np

#"Earth  "+str(8.5269*10**(-4)+tolerance)

def CAEarth(txtname,tolerance=1*10**(-4)):
    file = open(txtname+".txt", "r")
    lis=[]
    while True:
        content = file.readline()
        if "Earth  " in content:
            lis.append(content)
        if not content:
            break
    file.close()
    
    ### Nr. CA
    '''d = dict()
    d["Nr. CA"] = len(lis)
    for i in range(0,len(lis),1):
        if float(lis[i][33:41])<8.5269*10**(-4)+tolerance:
            d["Impact"] = lis[i]
    '''
    for i in range(0,len(lis),1):
        if float(lis[i][33:41])<8.5269*10**(-4)+tolerance:
            impact = True
    return impact

def filter(txtname,N,tolerance=1*10**(-4)):
    d = dict()
    for i in range(0,N,1):
        d[txtname+str(i)] = CAEarth(txtname,tolerance)
    return d

print(filter("response",1))







