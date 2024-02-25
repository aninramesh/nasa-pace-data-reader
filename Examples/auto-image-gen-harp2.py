#!/usr/bin/env python
# Python script to generate HARP2 RGB Images

# Load the required libraries
from nasa_pace_data_reader import L1, plot

import argparse
from datetime import datetime
import os,sys
from pathlib import Path
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# suppress warnings
import warnings
warnings.filterwarnings("ignore")

class Args:
        pass

def plotL1C(args):
    # Read the file
    l1c = L1.L1C()
    l1c_dict = l1c.read(args.l1c_file)

    # Load the plot class (default instrument is HARP2)
    plt_ = plot.Plot(l1c_dict)

    # define the figure and axis handles
    fig_ = plt.figure(dpi=args.dpi, figsize=(12, 9))

    # plot RGB in default plate carree projection
    ax1 = fig_.add_subplot(221, projection=ccrs.PlateCarree())
    plt_.projectedRGB(normFactor=600, noShow=True, ax=ax1, setTitle=False)
    ax1.set_title('Intensity\n(R=670 nm, G=550 nm, B=440 nm)')

    # plot RGB in with different view angle
    ax2 = fig_.add_subplot(222, projection=ccrs.PlateCarree())
    plt_.projectedRGB(var='i', viewAngleIdx=[36, 73, 84], normFactor=600,
                       scale=[0.85, 1.4, 1], ax=ax2, noShow=True, setTitle=False)
    # plt_.projectedRGB(var='q', viewAngleIdx=[31, 3, 83], scale=2, normFactor=100, saveFig=True)
    ax2.set_title('Intensity\n(R=670 nm, G=870 nm, B=440 nm)')

    # project dolp
    ax3 = fig_.add_subplot(223, projection=ccrs.PlateCarree())
    plt_.projectedRGB(var='dolp', viewAngleIdx=[31, 3, 83], normFactor=50,
                       scale=[0.8, 1, 1], ax=ax3, rgb_dolp=True, noShow=True, setTitle=False)
    ax3.set_title('Polarized Radiance\n(R=670 nm, G=550 nm, B=440 nm)')

    # plot one variable in a specific projection at closest viewing angle to nadir
    ax4 = fig_.add_subplot(224, projection=ccrs.PlateCarree())
    plt_.projectedRGB(var='dolp', normFactor=50, scale=[0.8, 1, 1], ax=ax4,
                       rgb_dolp=True, noShow=True, setTitle=False)
    ax4.set_title('Polarized Radiance\n(R=670 nm, G=870 nm, B=440 nm)')

    fig_.suptitle(f'HARP2 L1C Quicklook\n {l1c_dict["date_time"]} UTC')
    try:
        fig_.savefig(args.save_path, dpi=args.dpi)
        print(f'Quicklook saved to {args.save_path}')
    except Exception as e:
        print(f'Error saving the figure: {e}')
        return 1

    # plot RGB in Orthographic projection
    plt_.projectedRGB(proj='Orthographic', normFactor=600, saveFig=True,
                    figsize=(5, 5), noShow=True, savePath=args.save_path.replace('.png', '_orthographic.png'))

    return 0

if __name__ == "__main__":

    VERSION = '1.0'

    #-- Screen printing time and version
    mtime_str = datetime.fromtimestamp(
        Path(__file__).stat().st_mtime).isoformat(sep=' ', timespec='seconds')
    print(f'quicklook_harp2_l1c v{VERSION} ({mtime_str})\n')

    #--------------------------------------------------------------=---
    #-- 1. Command-line arguments/options with argparse
    #--------------------------------------------------------------=---

    parser = argparse.ArgumentParser(
                formatter_class=argparse.RawTextHelpFormatter,
                description='HARP2 L1C Quick look Processor',
                epilog="""
    EXIT Status:
        0   : All is well in the world
        1   : Dunno, something horrible occurred
                """)

    #-- required arguments
    parser.add_argument('--l1c_file',  type=str, required=True, help='path+filename of the HARP2 Level 1C file')
    parser.add_argument('--save_path', type=str, required=False, help='path to the quicklook png file')

    #-- optional arguments
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--instrument', type=str, default='HARP2', help='HARP2, or AirHARP2',
                        choices=['HARP2','AirHARP2'])
    parser.add_argument('--dpi', type=int, default=300, help='DPI of the saved figure')

    #-- retrieve arguments
    args = parser.parse_args()

    #-- validate arguments
    assert os.path.exists(args.l1c_file),     'l1c_file does not exist!' 
    assert args.instrument in ['HARP2','AirHARP2'], 'instrument must be HARP2 or AirHARP2'

    # save the figure in the same directory as the L1C file
    if args.save_path is None:
        args.save_path = os.path.join(os.path.dirname(args.l1c_file),
                                      os.path.basename(args.l1c_file).replace('.nc', '_quicklook.png'))
    if Path(args.save_path).is_dir():
        assert os.path.exists(args.save_path), 'save_path does not exist!'
        args.save_path = os.path.join(args.save_path, os.path.basename(args.l1c_file).replace('.nc', '_quicklook.png'))
    else:
        if os.path.dirname(args.save_path)!='':
            assert os.path.exists(os.path.dirname(args.save_path)), 'save_path does not exist!'

    #-- run the main program

    
    # args = Args()
    # args.l1c_file = '/Users/aputhukkudy/Downloads/az180_r.7/PACE_HARP2.20240224T104106.L1C.nc'
    # args.save_path = '/Users/aputhukkudy/Downloads/az180_r.7/PACE_HARP2.20240224T104106.L1C_quicklook.png'
    # args.dpi = 300
            
    # run the main program
    sys.exit(plotL1C(args))

