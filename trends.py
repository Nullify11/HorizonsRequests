"""
This module is dedicated to exploring any statistical trends there might be in the results achieved from main.py through extraction of the database.
"""


import numpy as np
import scipy.stats
from db_extractor import count_lines
import itertools
import sys
import matplotlib.pyplot as plt


# One-sided ANOVA with each of the parameters

def str_convert(string):
    """
    Converts stings to a list of floats of each element in the string.

    Parameters
    ----------
    sting : str
        Any string of numbers we wish to convert into a list of said numbers.
        
    Returns
    -------
    Unnamed : list
        A list of floats derived from the inputtet string

    """
    lis = list(string.split(' '))
    return [float(element) for element in lis]

def extract_testingvar(testing_var,testing_variables):
    """
    Extracts the values for the osculating element of interest for all the close approaching NEOs and all the
    NEOs which did not make a close approach.

    Parameters
    ----------
    testing_var : str
        The osculating element of interest.

    testing_variables : dict
        A dictionary of any valid testable osculating elements, where the key is the name of the element (a string) 
        and the value is an associated integer depending on where the elemnt is located in data from db_extractor.py.
        
    Returns
    -------
    ca_var_list : list
        A list of floats of the element given by testing_var for all the close approaching NEOs in the database.
    
    no_ca_var_list : list
        A list of floats of the element given by testing_var for all the NEOs with no close approachs in the database.

    """
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    
    test_var_number = testing_variables[testing_var]
    
    number_no_CA = count_lines('plotting_files/plotting_no_CA')
    no_ca_var_list = [0]*number_no_CA
    number_CA = count_lines('plotting_files/plotting0.1')
    ca_var_list = [0]*number_CA

    #The files in the directory "plotting_files/" are generated in db_extractor.py.
    with open('plotting_files/plotting_no_CA.txt', 'r') as file:
        for i in range(number_no_CA):
            content = file.readline()
            lis_content = str_convert(content)
            no_ca_var_list[i] = lis_content[test_var_number]
            sys.stdout.write(next(spinner))  # write the next character
            sys.stdout.flush()               # flush stdout buffer (actual character display)
            sys.stdout.write('\b')           # erase the last written char
            if not content:
                break
    with open('plotting_files/plotting0.1.txt', 'r') as file:
        for i in range(number_CA):
            content = file.readline()
            lis_content = str_convert(content)
            ca_var_list[i] = lis_content[test_var_number]
            sys.stdout.write(next(spinner))  # write the next character
            sys.stdout.flush()               # flush stdout buffer (actual character display)
            sys.stdout.write('\b')           # erase the last written char
            if not content:
                break
    return ca_var_list, no_ca_var_list

def stat_test():
    """
    The umbrella function which initates the test and tests each osculating element one-by-one.

    Parameters
    ----------
    None
        
    Returns
    -------
    None

    """
    testing_variables = {'ec' : 1, 'qr' : 2, 'tp' : 3, 'om' : 4, 'w' : 5, 'in' : 6, 'h' : 7, 'a' : 8}

    for key in testing_variables:
        ca_var_list, no_ca_var_list = extract_testingvar(key, testing_variables)
        anova_test(key, ca_var_list, no_ca_var_list)
        comp_confid_interval(ca_var_list, no_ca_var_list)


def anova_test(testing_var, ca_var_list, no_ca_var_list):
    """
    Preforms the actual ANOVA test and prints the result to the terminal.

    Parameters
    ----------
    testing_var : str
        The osculating element of interest.

    ca_var_list : list
        A list of floats of the element given by testing_var for all the close approaching NEOs in the database.
    
    no_ca_var_list : list
        A list of floats of the element given by testing_var for all the NEOs with no close approachs in the database.
        
    Returns
    -------
    None

    """
    no_ca_var_list5000 = np.random.choice(no_ca_var_list,5000)
    ca_var_list5000 = np.random.choice(ca_var_list,5000)

    print(testing_var)
    print('Random sampled 5000 ANOVA:', scipy.stats.f_oneway(no_ca_var_list5000,ca_var_list5000))
    print('ANOVA:',scipy.stats.f_oneway(no_ca_var_list,ca_var_list))
    print('Mean no CA:', np.mean(no_ca_var_list), 'Mean CA:', np.mean(ca_var_list))
    #t-test is two-tailed
    print('Random sampled 5000 t-test:',scipy.stats.ttest_ind(no_ca_var_list5000,ca_var_list5000))
    print('t-test:',scipy.stats.ttest_ind(no_ca_var_list,ca_var_list),'\n')
    #plt.hist(no_ca_var_list5000, bins=25)
    #plt.hist(ca_var_list5000, bins=25)
    #plt.show()
    #plt.boxplot(no_ca_var_list5000)
    #plt.boxplot(ca_var_list5000)
    #plt.show()

def std_deviation(data_list):
    """
    Calculates the standard deviation for an inputtet list of data points. 
    Note: numpy already has such a function and it can be used instead.

    Parameters
    ----------
    data_list : list
        Either the ca_var_list or the no_ca_var_list generated in the function extract_testingvar.
        
    Returns
    -------
    Unnamed : float
        The standard deviation of the inputtet list of data points.
    
    """
    return (((sum([elem-np.mean(data_list) for elem in data_list]))**2)/(len(data_list)))**(1/2)

def comp_confid_interval(ca_var_list, no_ca_var_list):
    """
    Calculates the 95% confidence interval of the two lists ca_var_list and no_ca_var_list and print these to the terminal.

    Parameters
    ----------
    ca_var_list : list
        A list of floats of the element given by testing_var for all the close approaching NEOs in the database.
    
    no_ca_var_list : list
        A list of floats of the element given by testing_var for all the NEOs with no close approachs in the database.
        
    Returns
    -------
    None

    """
    mean_diff = np.mean(no_ca_var_list)-np.mean(ca_var_list)
    print('Mean difference:', mean_diff)
    print('Standard deviation CA:', np.std(ca_var_list,ddof=0))
    print('Standard deviation no CA:', np.std(ca_var_list,ddof=0))
    se = (((np.std(ca_var_list,ddof=0)**2)/(len(ca_var_list)))+((np.std(no_ca_var_list,ddof=0)**2)/(len(no_ca_var_list))))**(1/2)
    t = (mean_diff)/se
    print('95 percent confidence interval using t-score:',mean_diff-t*se, mean_diff+t*se)
    print('95 percent confidence interval using 1.96 z-score:',mean_diff-1.96*se, mean_diff+1.96*se)


#anova_test('h')
#anova_test('qr')
#anova_test('in')
#anova_test('a')
#anova_test('ec')
#anova_test('tp')
#anova_test('om')
#anova_test('w')

stat_test()