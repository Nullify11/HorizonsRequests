
import numpy as np
import scipy.stats
from db_extractor import count_lines
import itertools
import sys
import matplotlib.pyplot as plt


# ANOVA med hver af parameterne

def str_convert(string): 
    lis = list(string.split(' '))
    return [float(element) for element in lis]

def extract_testingvar(testing_var,testing_variables):
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    
    test_var_number = testing_variables[testing_var]
    
    number_no_CA = count_lines('plotting_files/plotting_no_CA')
    no_ca_var_list = [0]*number_no_CA
    number_CA = count_lines('plotting_files/plotting0.1')
    ca_var_list = [0]*number_CA

    with open('plotting_files/plotting_no_CA.txt', 'r') as file:
        for i in range(number_no_CA):
            content = file.readline()
            lis_content = str_convert(content)
            no_ca_var_list[i] = lis_content[test_var_number]
            sys.stdout.write(next(spinner))  # write the next character
            sys.stdout.flush()                      # flush stdout buffer (actual character display)
            sys.stdout.write('\b')                 # erase the last written char
            if not content:
                break
    with open('plotting_files/plotting0.1.txt', 'r') as file:
        for i in range(number_CA):
            content = file.readline()
            lis_content = str_convert(content)
            ca_var_list[i] = lis_content[test_var_number]
            sys.stdout.write(next(spinner))  # write the next character
            sys.stdout.flush()                      # flush stdout buffer (actual character display)
            sys.stdout.write('\b')                 # erase the last written char
            if not content:
                break
    return ca_var_list, no_ca_var_list

def stat_test():
    testing_variables = {'ec' : 1, 'qr' : 2, 'tp' : 3, 'om' : 4, 'w' : 5, 'in' : 6, 'h' : 7, 'a' : 8}

    for key in testing_variables:
        ca_var_list, no_ca_var_list = extract_testingvar(key, testing_variables)
        anova_test(key, ca_var_list, no_ca_var_list)
        comp_confid_interval(ca_var_list, no_ca_var_list)


def anova_test(testing_var, ca_var_list, no_ca_var_list):
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
    return (((sum([elem-np.mean(data_list) for elem in data_list]))**2)/(len(data_list)))**(1/2)

def comp_confid_interval(ca_var_list, no_ca_var_list):
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

#https://stats.stackexchange.com/questions/2516/are-large-data-sets-inappropriate-for-hypothesis-testing
#https://www.reddit.com/r/AskStatistics/comments/gwafki/q_data_set_is_too_large_and_yields_statistical/


stat_test()