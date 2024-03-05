#!/usr/bin/env python3
'''
HARP2 L1A Reader -- Rachel Smith 20240217
Modified -- Anin
'''
#%%
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os, sys
from netCDF4 import Dataset
from pathlib import Path

'''
Add more groups and variable as needed
'''

# index of line
idx = -1
# maximum count
iMax = 8192
# define the bins
predefined_bin = np.linspace(0, iMax, 100)

def plotHist(fileName, idx=-1, iMax=8192, bins_=100):
    '''
    Plot the histogram of the sensors
    
    Args:
    fileName: str (default=None) path to the file
    idx: int (default=2) index of the line, -1 for all the lines
    iMax: int (default=8192) maximum count
    bins_: int (default=100) number of bins or predefined bins

    Returns:
    counts_1: numpy array
    counts_2: numpy array
    counts_3: numpy array
    '''
    runAllLines = False if idx > -1 else True

    if not os.path.exists(fileName):
        print('File not found: {}'.format(fileName))
        return None
    
    HARP2_L1A = Dataset(fileName)
    sensor1 = HARP2_L1A.groups['image_data']['sensor1'][:] #sensor1(frames=471, lines=90, pixels=646)
    sensor2 = HARP2_L1A.groups['image_data']['sensor2'][:]
    sensor3 = HARP2_L1A.groups['image_data']['sensor3'][:]
    
    if runAllLines:
        idx = range(sensor1.shape[1])

        counts_1 = np.zeros(bins_.shape[0]-1)
        counts_2 = np.zeros(bins_.shape[0]-1)
        counts_3 = np.zeros(bins_.shape[0]-1)

        for i in idx:
            # plot the histogram for the given line
            counts_1_i, _, _, = plt.hist(np.ravel(sensor1[:,i,:].data), bins=bins_)
            counts_2_i, _, _, = plt.hist(np.ravel(sensor2[:,i,:].data), bins=bins_)
            counts_3_i, _, _, = plt.hist(np.ravel(sensor3[:,i,:].data), bins=bins_)

            # add the counts
            counts_1 += counts_1_i
            counts_2 += counts_2_i
            counts_3 += counts_3_i

    else:
        # plot the histogram for the given line
        counts_1, _, _, = plt.hist(np.ravel(sensor1[:,idx,:].data), bins=bins_)
        counts_2, _, _, = plt.hist(np.ravel(sensor2[:,idx,:].data), bins=bins_)
        counts_3, _, _, = plt.hist(np.ravel(sensor3[:,idx,:].data), bins=bins_)
    plt.close()

    # close the net cdf file
    HARP2_L1A.close()

    return counts_1, counts_2, counts_3

# run it for all the files in a directory
# Change the directory if passed as an argument
if len(sys.argv) > 1:
    HARP2_dir = sys.argv[1]
    # check if the directory exists
    if not os.path.exists(HARP2_dir):
        print('Directory not found: {}'.format(HARP2_dir))
        sys.exit(1)
else:
    # change this to the directory where the files are located (only used if the directory is not passed as an argument)
    HARP2_dir = '/Users/aputhukkudy/Downloads/25'

# get all the files with matching pattern `PACE_HARP2*.L1A.nc`
files = list(Path(HARP2_dir).rglob('PACE_HARP2*.L1A.nc'))

# plot the histogram (for all the sensors in the same plot)
plotHistogram = False

# initialize the counts
counts_1_Total = np.zeros(predefined_bin.shape[0]-1)
counts_2_Total = np.zeros(predefined_bin.shape[0]-1)
counts_3_Total = np.zeros(predefined_bin.shape[0]-1)

# loop through the files
for file in files:
    print(file)
    try:
        counts_1, counts_2, counts_3 = plotHist(file, idx, iMax, predefined_bin)
        counts_1_Total += counts_1
        counts_2_Total += counts_2
        counts_3_Total += counts_3
        
        # plot the histogram (for all the sensors in the same plot)
        if plotHistogram:
            plt.plot(predefined_bin[1:], counts_1, label='sensor1')
            plt.plot(predefined_bin[1:], counts_2, label='sensor2')
            plt.plot(predefined_bin[1:], counts_3, label='sensor3')
            plt.legend()
            plt.show()
    except Exception as e:
        print('Error reading the file: {}'.format(file))
        print('Error: {}'.format(e))
        continue
    
# plot the histogram (for all the sensors in the same plot) after reading all the files
plt.hist(predefined_bin[1:], bins=predefined_bin, weights=counts_1_Total, label='sensor1', alpha=0.3)
plt.hist(predefined_bin[1:], bins=predefined_bin, weights=counts_2_Total, label='sensor2', alpha=0.3)
plt.hist(predefined_bin[1:], bins=predefined_bin, weights=counts_3_Total, label='sensor3', alpha=0.3)
plt.legend()
plt.xlabel('Counts')
plt.ylabel('Frequency')
plt.title('%s \n HARP2 L1A Histogram' %HARP2_dir)
# keep the x axis in log scale
plt.yscale('log')
plt.show()

# save the histogram plot
plt.savefig('%s/histogram.png' %HARP2_dir, dpi=int(300), bbox_inches='tight')
print( f'Saved histogram.png to {HARP2_dir}')

# save the histogram data to a txt file
with open('%s/sensor1.txt' %HARP2_dir, 'w') as f:
    f.write('Bin Counts\n')
    np.savetxt(f, np.vstack((predefined_bin[1:], counts_1_Total)).T, fmt='%s', delimiter=' ', newline='\n', header='', footer='', comments='# ', encoding=None)
    print( f'Saved sensor1.txt to {HARP2_dir}')
    f.close()
with open('%s/sensor2.txt' %HARP2_dir, 'w') as f:
    f.write('Bin Counts\n')
    np.savetxt(f, np.vstack((predefined_bin[1:], counts_2_Total)).T, fmt='%s', delimiter=' ', newline='\n', header='', footer='', comments='# ', encoding=None)
    print( f'Saved sensor2.txt to {HARP2_dir}')
    f.close()
with open('%s/sensor3.txt' %HARP2_dir, 'w') as f:
    f.write('Bin Counts\n')
    np.savetxt(f, np.vstack((predefined_bin[1:], counts_3_Total)).T, fmt='%s', delimiter=' ', newline='\n', header='', footer='', comments='# ', encoding=None)
    print( f'Saved sensor3.txt to {HARP2_dir}')
    f.close()