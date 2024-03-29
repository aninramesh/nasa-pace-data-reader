#!/usr/bin/env python
# Python script to generate HARP2 Projected RGB Images in a single plot
'''
This script is an example of how to use the nasa_pace_data_reader package to generate HARP2 Projected RGB Images in a single plot

The script reads L1C files in a directory and generates a single plot with the HARP2 Projected RGB Images in robinson projection

Created by Anin Puthukkudy (ESI, UMBC)
'''

# Load the required libraries
from nasa_pace_data_reader import L1, plot

# suppress warnings
import warnings
warnings.filterwarnings("ignore")

# other libraries
import os,sys, pickle, argparse, gc
from pathlib import Path
from datetime import datetime
import numpy as np

# plot libraries
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

#--------------------------------------------------------------#
# local functions
#--------------------------------------------------------------#
class Args:
        pass

def L1C_composite(args, rgb_, viewIndex=[36, 4, 84]):
    """Create a composite of the L1C files in the directory
    
    Args:
    
    args: argparse.Namespace
    
    rgb_: dict
        dictionary to store the RGB images and extent
    
    viewIndex: list
        list of view angles for the RGB images
        
    Returns:
    
    rgb_: dict
        dictionary to store the RGB images and extent"""

    # list all the files in the directory
    l1c_files = [f for f in os.listdir(args.l1c_dir) if f.endswith('L1C.5km.nc')]
    
    # sort by filename
    l1c_files.sort()

    # projection size
    proj_size = (600, 300)

    # which variable to plot
    if args.dolp:
        var = 'dolp'
        args.normFactor=50
        viewIndex=[31, 3, 83]
        scale_=[0.8, 1, 1]
    else:
        var = 'i'

    # loop through the files
    for l1c_file in l1c_files:
        # Read the file
        l1c = L1.L1C()
        try:
            file_path = os.path.join(args.l1c_dir, l1c_file)
            l1c_dict = l1c.read(file_path)

            # just the filename
            l1c_file = os.path.basename(file_path)

            # Load the plot class (default instrument is HARP2)
            plt_ = plot.Plot(l1c_dict)

            # plot RGB in Orthographic projection
            if args.viewIndex < 4:
                rgb_['rgb_new'][l1c_file], \
                    rgb_['rgb_extent'][l1c_file], \
                        rgb_['dateline'][l1c_file] = plt_.projectedRGB(var=var, proj='None', viewAngleIdx=viewIndex,
                                                                        normFactor=args.normFactor, saveFig=True, returnRGB=True,
                                                                        figsize=(6, 6), noShow=True, savePath=args.save_path,
                                                                        proj_size=proj_size, returnTransitionFlag=True)
            elif args.viewIndex >= 4 and args.viewIndex < 6:
                
                if not args.dolp:
                    scale_=[0.85, 1.4, 1]

                rgb_['rgb_new'][l1c_file], \
                    rgb_['rgb_extent'][l1c_file], \
                        rgb_['dateline'][l1c_file] = plt_.projectedRGB(var=var, proj='None', viewAngleIdx=viewIndex,
                                                                        normFactor=args.normFactor, scale=scale_, saveFig=True, returnRGB=True,
                                                                        figsize=(6, 6), noShow=True, savePath=args.save_path,
                                                                        proj_size=proj_size, returnTransitionFlag=True)
            else:
                rgb_['rgb_new'][l1c_file],\
                    rgb_['rgb_extent'][l1c_file],\
                        rgb_['dateline'][l1c_file] = plt_.projectedRGB(var=var, proj='None', viewAngleIdx=viewIndex,
                                                                        normFactor=args.normFactor, scale=scale_, saveFig=True, returnRGB=True, rgb_dolp=True,
                                                                        figsize=(6, 6), noShow=True, savePath=args.save_path,
                                                                        proj_size=proj_size, returnTransitionFlag=True)
            
            gc.collect()

        except Exception as e:
            print(f'Error: {e}')
            continue
        
    return rgb_

if __name__ == "__main__":

    VERSION = '1.1'

    #-- Screen printing time and version
    mtime_str = datetime.fromtimestamp(
        Path(__file__).stat().st_mtime).isoformat(sep=' ', timespec='seconds')
    print(f'({mtime_str})\n')

    #--------------------------------------------------------------=---
    #-- 1. Command-line arguments/options with argparse
    #--------------------------------------------------------------=---
    
    parser = argparse.ArgumentParser(
                formatter_class=argparse.RawTextHelpFormatter,
                description='HARP2 L1C composite of the day',
                epilog="""
    EXIT Status:
        0   : All is well in the world
        1   : Dunno, something horrible occurred
                """)

    #-- required arguments
    parser.add_argument('--l1c_dir',  type=str, required=True, help='path+filename of the HARP2 Level 1C file')
    parser.add_argument('--save_path', type=str, required=False, help='path to save the composite image')

    #-- optional arguments
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--instrument', type=str, default='HARP2', help='HARP2, or AirHARP2',
                        choices=['HARP2','AirHARP2'])
    parser.add_argument('--dpi', type=int, default=300, help='DPI of the saved figure')
    parser.add_argument('--normFactor', type=int, default=300, help='Normalization factor for the RGB plot')
    parser.add_argument('--label', type=bool, default=True, help='Add label to the RGB plot')
    parser.add_argument('--tag', type=str, default='', help='Tag to add to the filename')
    parser.add_argument('--viewIndex', type=int, default=0, help='Tag to add to the filename')
    parser.add_argument('--dolp', type=bool, default=False, help='Add label to the RGB plot')

    #-- retrieve arguments
    args = parser.parse_args()

    #-- validate arguments
    assert os.path.exists(args.l1c_dir), 'l1c_file does not exist!' 
    assert args.instrument in ['HARP2','AirHARP2'], 'instrument must be HARP2 or AirHARP2'
    assert args.normFactor > 0, 'normFactor must be greater than 0'

    # save the figure in the same directory as the L1C file
    if args.save_path is None:
        print('save_path is not provided. Saving the composite in the same directory as the L1C files')
        # add quicklook/composite to the directory name
        args.save_path = os.path.join(os.path.dirname(args.l1c_dir), 'quicklook/composite')
        # create a new directory
        os.makedirs(args.save_path, exist_ok=True)
    if Path(args.save_path).is_dir():
        os.makedirs(args.save_path, exist_ok=True)
        assert os.path.exists(args.save_path), 'save_path does not exist!'
    else:
        if os.path.dirname(args.save_path)!='':
            os.makedirs(os.path.dirname(args.save_path), exist_ok=True)
            assert os.path.exists(os.path.dirname(args.save_path)), 'save_path does not exist!'

    #--------------------------------------------------------------#
    #-- run the main program
    #--------------------------------------------------------------#
            
    # define the args for debug
    # args = Args()
    # args.l1c_dir = '/Users/aputhukkudy/Downloads/03-28/'
    # args.save_path = '/Users/aputhukkudy/Downloads/03-28/composite'
    # args.normFactor = 400
    # args.dpi = 600
    # args.label = False
    # args.tag = 'test'
    # args.viewIndex = 2
    # args.dolp = False

    # viewIndex
    if args.viewIndex == 0:
        viewIndex = [36, 4, 84]
    elif args.viewIndex == 1:
        viewIndex = [19, 1, 81]
    elif args.viewIndex == 2:
        viewIndex = [67, 9, 89]
    elif args.viewIndex == 3:
        viewIndex = [49, 6, 86]
    elif args.viewIndex == 4:
        viewIndex = [36, 73, 84]
    elif args.viewIndex == 5:
        viewIndex = [19, 71, 81]
    else:
        print('Error: viewIndex must be 0-5')
        sys.exit(1)
            
    # rgb_ dict
    rgb_ = {}
    rgb_['rgb_new'] = {}
    rgb_['rgb_extent'] = {}
    rgb_['dateline'] = {}

    # plot the composite image  
    rgb_ = L1C_composite(args, rgb_, viewIndex=viewIndex)

    #%% plot images
    # plot the composite image in robinson projection
    fig = plt.figure(figsize=(18, 9))
    axm = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson(central_longitude=0))
    fig.patch.set_facecolor('black')
    # set the extent to global
    axm.set_global()

    # add standard background map
    axm.stock_img()

    # add coastlines
    axm.coastlines(lw=0.1)

    # add the RGB image
    for key in rgb_['rgb_new'].keys():

        print(key)

        # clon = 180 if rgb_['dateline'][key] else 0
        # mask the black pane
        rgb_new = np.ma.masked_where(rgb_['rgb_new'][key]== 0, rgb_['rgb_new'][key])
        axm.imshow(rgb_new, origin='lower', extent=rgb_['rgb_extent'][key], transform=ccrs.PlateCarree())

        # add the date
        date = key.split('.')[1]
        # locate the date at the center of the projected image
        print('Longitude: %f, Latitude: %f' %(np.mean(rgb_['rgb_extent'][key][:2]), np.mean(rgb_['rgb_extent'][key][2:])))
        print('Dateline: %s' %rgb_['dateline'][key])
        
        # label
        if args.label:
            axm.text(np.mean(rgb_['rgb_extent'][key][:2]), np.mean(rgb_['rgb_extent'][key][2:]), date[9:],
                    fontsize=6, color='m', ha='center', va='center', bbox=dict(facecolor='white', edgecolor='none', boxstyle='round', pad=0.5, alpha=0.75),
                    transform=ccrs.PlateCarree())

    # set the title
    axm.set_title('HARP2 L1C Composite\n%s' %(date[:8]), fontsize=12, color='tan')
    
    # tight layout
    plt.tight_layout()

    # save the figure
    # add the date to the filename
    os.makedirs(args.save_path, exist_ok=True)
    saveFileName = os.path.join(args.save_path, 'composite_viewIdx-%s-%s-%s.png' %(str(viewIndex[0]),
                                                                                   datetime.now().strftime('%Y-%m-%d'),
                                                                                   args.tag))
    fig.savefig(saveFileName, dpi=args.dpi)
    print(f'Composite saved to {saveFileName}')