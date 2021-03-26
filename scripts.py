from pyswmm import Simulation
from pyswmm import Nodes, Links, Subcatchments
from shutil import copyfile
import random
import csv
import os
import pandas as pd
import numpy as np

INP_FILE = 'C:\\Users\\Christina\\Documents\\EPA SWMM Projects\\Newport_Baseline\\Newport_Baseline_WithLID_20190418.inp'

def save_simulation_results(inp_file, csv_output, polluts, nodes=None, step=60, 
                            debug=False):
    '''
    Parameters
        - inp_file   : as used for SWMM simulation
        - csv_output : the file to save the results in
        - polluts    : the subset of pollutants to record
        - nodes      : a subset of nodes to observe; if None, use all nodes
        - step       : the number of seconds in between each result (min=5secs)
        - debug      : if True, print out 
    '''
    polluts = list(polluts) # In case a set is given
    with Simulation(inp_file) as sim, open(csv_output, 'w', newline='') as f:
        print('\nStarting run')
        sim.step_advance(step) 
        
        nodes = [n for n in Nodes(sim) if nodes is None or n.nodeid in nodes]
    
        writer = csv.writer(f)
        writer.writerow(['DateTime', 'NodeID', *polluts])
        for step in sim:
            for n in nodes:
                data = [sim.current_time, n.nodeid, 
                        *[n.pollut_quality[pollut] for pollut in polluts]]
                writer.writerow(data)
                if debug:
                    print(data)
        print('Finished run')

def rand_subcatchments(inp_file, csv_output, n_subc=None, rep=1, debug=False):
    '''
    Outputs randomized subcatchments to a csv file
    Parameters: 
        - inp_file   : as used for SWMM simulation
        - csv_output : the file to save results in
        - n_subc     : if a number between 0.0 and 1.0 is provided, then get a 
                       percentage of subcatchments;
                       if an integer above 1 is provided, then use that number 
                       of subcatchments
        - rep        : number of repetitions to produce
    '''
    
    assert type(n_subc) == float and 0.0 <= n_subc <= 1.0 or \
           type(n_subc) == int   and n_subc >= 1, \
           'n_subc must be a float in (0.0,1.0) or an int >= 1'
    
    with Simulation(inp_file) as sim, open(csv_output, 'w', newline='') as f:
        subc = [s.subcatchmentid for s in Subcatchments(sim)]
        
        if type(n_subc) == float:
            n_subc = round(len(subc) * n_subc)
        
        writer = csv.writer(f)
        for _ in range(rep):
            writer.writerow(random.sample(subc, n_subc))

def get_nodes(filename):
    nodes = []
    with open(filename, 'r') as nodefile:
        for line in nodefile:
            nodes.append(line.strip())
    return nodes


def rand_locations(csv_output, n_locations):
    '''
    Outputs n random input locations to a csv file
    Parameters:
        - csv_output  : the file to save results in
        - n_locations : if a number between 0.0 and 1.0 is provided, then 
                        return a percentage of locations;
                        if an integer above 1 is provided, then return that 
                        number of locations
    '''
    # Find the unique locations
    path = './WaterQualityFiles'
    filenames = os.listdir(path)
    locations = set()
    [locations.add(f.split('_')[0]) for f in filenames]

    # Determine number of locations to find
    if n_locations >= 0 and n_locations <= 1:
        n_locations *= len(locations)

    # Find random locations
    string = ''
    for i in range(n_locations):
        rand = random.randint(0, n_locations-1)
        string += str(list(locations)[rand]) + ','
        locations.remove(list(locations)[rand])

    # Write to file
    f = open(csv_output, 'w')
    f.write(string[:-1])
    f.close()

def delete_lines(line_start, line_end):
    '''
    Deletes lines from each file in the WaterQualityFiles directory
    Parameters:
        - line_start  : the first line number that needs to be deleted
                        in the WaterQualityFiles directory
        - line_end    : the last line number that needs to be deleted  
    '''
    
    # Iterate through each file
    path = './WaterQualityFiles/'
    for filename in os.listdir(path):

        # Open read & write file
        f_read = open(path+filename, 'r')
        f_write = open(path+'temp.txt', 'w')

        # Copy information except the lines specified
        for i, line in enumerate(f_read):
            if i >= line_start-1 and i <= line_end-1:
                continue
            f_write.write(line)
        
        # Clean up opened files
        f_read.close()
        f_write.close()
        os.remove(path+filename)
        os.rename(path+'temp.txt', path+filename)

def find_threshold(orig_file, pollutant):
    '''
    Returns 2*max pollution value in the orig_file
    Parameters:
        - orig_file : name of the sim results without pollutant modifications
        - pollutant : name of column in csv file
    '''
    
    df = pd.read_csv(orig_file)
    threshold = max(df[pollutant])
    print('Found threshold')
    return threshold

 
def threshold_nodes(threshold, mod_file, out_file, pollutant):
    '''
    Outputs the nodes that had pollution levels greater than the threshold
    Parameters:
        - threshold : maximum value of pollution tolerated
        - mod_file  : name of sim results with pollutant modifications
        - out_file  : name of output file
        - pollutant : name of column in mod_file
    '''
    # Load data into dataframe
    df = pd.read_csv(mod_file)
    df = df.loc[df[pollutant] > threshold]

    # Create dictionary of node-time mapping
    nodes = {}
    for index, row in df.iterrows():
        if row['NodeID'] not in nodes:
            nodes[row['NodeID']] = row['DateTime']
   
    # Write dictionary to file
    with open(out_file, 'w') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in nodes.items():
            writer.writerow([key, value])


def diff_nodes(orig_file, mod_file, out_file, pollutant):
    '''
    Outputs the nodes that had pollution levels greater than the threshold
    Parameters:
        - threshold : maximum value of pollution tolerated
        - mod_file  : name of sim results with pollutant modifications
        - out_file  : name of output file
        - pollutant : name of column in mod_file
    '''
    # Load data into dataframe
    df0 = pd.read_csv(orig_file)
    df1 = pd.read_csv(mod_file)

    # Find differences
    df = column_names = ['DateTime', 'NodeID', pollutant]
    df = pd.DataFrame(columns = column_names)
    for i, j in zip(df0.iterrows(), df1.iterrows()):
        row0 = i[1]
        row1 = j[1]
        if row0[pollutant] != row1[pollutant]:
            df.loc[len(df.index)] = row1
    print(df)

    # Create dictionary of node-time mapping
    nodes = {}
    for index, row in df.iterrows():
        if row['NodeID'] not in nodes:
            nodes[row['NodeID']] = row['DateTime']
   
    # Write dictionary to file
    with open(out_file, 'w') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in nodes.items():
            writer.writerow([key, value])


def run_locations(pollutant):
    '''
    Runs the simulation multiple times. Each time the simulation is run, a 
        different pollution area's value is changed to 82.374, which is double 
        the 'Cu' threshold. Then, we find the nodes that were affected after 
        each run. This is stored in a file in ./Output/Diff/{location}.csv
    Parameters:
        - pollutant : pollutant to observe
    '''

    maximum = find_threshold('./Output/Original/'+pollutant+'.csv', pollutant)
    threshold = 0

    # Find the unique locations
    path = './WaterQualityFiles/'
    filenames = os.listdir(path)
    locations = set()
    [locations.add(f.split('_')[0]) for f in filenames]

    # Iterate through each location
    for l in list(locations):
        print('Starting ' + l)

        # Copy the file to save the old data
        name = l + '_' + pollutant
        modname = path + name + '.dat'
        '''copyfile(modname, 'tmp')
        moddata = open(modname, 'w')
        origdata = open('tmp', 'r')
        
        # Write modified pollutant data
        for i, line in enumerate(origdata):
            if i == 2214:                                                   # TODO: change value according to date
                date, time, value = line.split()
                moddata.write('1/21/2010\t9:59\t'+value+'\n')               # before
                moddata.write('1/21/2010\t10:00\t'+str(maximum*2)+'\n')     # dump
                moddata.write('1/21/2010\t12:00\t'+value+'\n')              # after
            else:
                moddata.write(line)

        # Close files
        moddata.close()
        origdata.close()

        # Run pipeline 
        save_simulation_results(INP_FILE, './Output/Modified/'+name+'.csv', [pollutant], step=30*60)'''
        diff_nodes('./Output/Original/'+pollutant+'.csv', './Output/Modified/'+name+'.csv', './Output/Diff/'+name+'.csv', pollutant)
        #threshold_nodes(threshold, './Output/Modified/'+name+'.csv', './Output/Diff/'+name+'.csv', pollutant)
        
        # Replaced modified pollutant data
        '''os.remove(modname)
        os.rename('tmp', modname)'''

        print('Finished ' + l)
        print('')


def create_matrix(pollutant, nodes_file, matrix_file, locations_file):

    # Find the unique locations
    path = './Output/Diff/'
    filenames = os.listdir(path)
    set_locations = set()
    [set_locations.add(f.split('_')[0]) for f in filenames]
    locations = list(set_locations)

    # Set up numpy array
    nodes = get_nodes(nodes_file)
    matrix = np.matrix(np.zeros((len(locations), len(nodes))), dtype='timedelta64[s]')
    time0 = np.datetime64('2010-01-21 10:00:00')

    # Iterate through each location
    for l_index, l in enumerate(locations):
        with open(path+l+'_'+pollutant+'.csv', 'r') as readfile:
            for line in readfile:
                line = line.strip()
                
                # Get node information
                n_name = line.split(',')[0]
                if not line.split():
                    continue
                time1 = np.datetime64(line.split(',')[1])
                td = time1 - time0
                n_index = nodes.index(n_name)

                # Update matrix
                
                matrix[l_index, n_index] = td

    # Write locations
    write_locations = open(locations_file, 'w')
    write_locations.write('\n'.join(locations))
    write_locations.close()
    print(matrix.shape)

    # Write matrix
    np.savetxt(matrix_file, matrix, fmt='%s', delimiter=',')


if __name__ == '__main__':
    
    #delete_lines(2196, 2197)
    run_locations('Cu')
    create_matrix('Cu', 'nodes.txt', 'matrix.csv', 'locations.csv')
    #save_simulation_results(INP_FILE, './Output/Original/Cu.csv', ['Cu'], step=30*60)
    #save_simulation_results(INP_FILE, './Output/Modified/EColi.csv', ['EColi'], step=30*60)
    #rand_locations('./Output/locations.csv', 5)
    #threshold = find_threshold('./Output/Original/Cu.csv', 'Cu')
    #threshold_nodes(threshold, './Output/Modified/CMF03@PINCRK@F01_Cu.csv', './Output/Diff/CMF03@PINCRK@F01_Cu.csv', 'Cu')

    #rand_subcatchments(INP_FILE, 'SWMM_Subcatchments.csv', n_subc=0.02, rep=10)
    #rand_subcatchments(INP_FILE, 'SWMM_Subcatchments.csv', n_subc=5, rep=10)
