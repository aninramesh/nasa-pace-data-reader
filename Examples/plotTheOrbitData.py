#!/usr/bin/env python
# Python script to generate HARP2 RGB Images in orthographic projection and plot the orbit using
# multiple L1C files

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

#--------------------------------------------------------------#
# local functions
#--------------------------------------------------------------#

class Args:
        pass

def plotL1C(args, fig_, rgb_, temp_num=0):

    # Read the file
    l1c = L1.L1C()
    try:
        l1c_dict = l1c.read(args.l1c_file)

        # just the filename
        l1c_file = os.path.basename(args.l1c_file)

        # Load the plot class (default instrument is HARP2)
        plt_ = plot.Plot(l1c_dict)

        # plot RGB in Orthographic projection
        fig2, ax2, rgb_['rgb_new'][l1c_file], rgb_['rgb_extent'][l1c_file]= plt_.projectedRGB(proj='Orthographic',
                                                                                        normFactor=600, saveFig=True, returnRGB=True,
                                                                                        figsize=(5, 5), noShow=True, savePath=args.save_path)
        
        if temp_num > 0:
            # plot the orbit with previous L1C files
            for key in rgb_['rgb_new']:
                ax2.imshow(rgb_['rgb_new'][key], origin='lower', extent=rgb_['rgb_extent'][key], transform=ccrs.PlateCarree())
            fig2.savefig(str(args.save_path).replace('.png', '_seq.png'), dpi=args.dpi)
        else:
            fig2.savefig(str(args.save_path).replace('.png', '_seq.png'), dpi=args.dpi)
        
        return ax2
    except Exception as e:
        print(f'Error: {e}')
        if "NetCDF: HDF error" in str(e):
            print(f'Error: {args.l1c_file} has netCDF error')
            print('---'*10)
            os.system('rm -f {args.l1c_file}')
            print(f'Error: {args.l1c_file} has been removed')
            print('---'*10)
        return None

def makeMovieFromImages(dir, movie_dir = f'{dir}/movie',movie_name='movie'):
    """ Stitch the images in a directory into a movie
    
    Args:
        dir (str): Path to the directory containing the images
    """

    # List of images
    images = sorted(Path(dir).glob('*L1C.png'))

    # Create the movie using list of images in mac os
    for i, image in enumerate(images):
        os.system(f'convert {image} -resize 1000x1000 {movie_dir}/{i:04d}.png')
        seq_image = str(image).replace('.png', '_seq.png')
        os.system(f'convert {seq_image} -resize 1000x1000 {movie_dir}/{i:04d}_seq.png')
    
    # Create the movie using list of images
    os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d.png -vcodec mpeg4 -y {movie_dir}/{movie_name}.mp4')
    os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d_seq.png -vcodec mpeg4 -y {movie_dir}/{movie_name}_seq.mp4')
    

#--------------------------------------------------------------#
# arguments
#--------------------------------------------------------------#
    
# check if imagemagick and ffmpeg are installed/loaded (in NyX automatically loaded by the spack)
if os.system('which convert') != 0:
    print('Error: imagemagick is not installed')
    print('Please install imagemagick using the following command (NyX): spack load imagemagick')
    if os.hostname() == 'nyx':
        os.system('spack load imagemagick')
    else:
        sys.exit(1)

if os.system('which ffmpeg') != 0:
    print('Error: ffmpeg is not installed')
    print('Please install ffmpeg using the following command (NyX): spack load ffmpeg')
    if os.hostname() == 'nyx':
        os.system('spack load ffmpeg')
    else:
        sys.exit(1)

#--------------------------------------------------------------#
        
# Parse the command-line arguments
#-- required arguments
parser = argparse.ArgumentParser(description='Generate RGB images/movie from L1C files')
parser.add_argument('--l1c_dir', type=str, required=True, help='L1C dir to process')

#-- optional arguments
parser.add_argument('--dpi', type=int, required=False, default=200, help='DPI of the saved figure')
parser.add_argument('--movie-only', type=bool, required=False, default=False, help='Create movie only')

args_ = parser.parse_args()
#--------------------------------------------------------------#

# List of L1C files from a directory
l1c_dir = Path(args_.l1c_dir)
l1c_files = sorted(Path(l1c_dir).glob('*.nc'))

# sort the L1C files by filename
l1c_files = sorted(l1c_files, key=lambda x: x.name)

#--------------------------------------------------------------#

# rgb_ dict
rgb_ = {}
rgb_['rgb_new'] = {}
rgb_['rgb_extent'] = {}

#--------------------------------------------------------------#
args = Args()
args.dpi = args_.dpi

# Define the figure handle
fig = plt.figure(dpi=args.dpi, figsize=(5, 5))

temp_num = 0

# Loop through the L1C files
if not bool(args_.movie_only):
    for l1c_file in l1c_files:
        
        args.l1c_file = str(l1c_file)
        args.save_path = l1c_file.with_suffix('.png')
        print('Projecting RGB for:', args.l1c_file)
        ax_new = plotL1C(args, fig, rgb_, temp_num=temp_num)
        temp_num += 1
#--------------------------------------------------------------#
    
# Make a movie from the images
# movie directory
movie_dir = f'{l1c_dir}/movie'
os.makedirs(movie_dir, exist_ok=True)
try:
    makeMovieFromImages(l1c_dir, movie_dir=movie_dir,  movie_name='FullOrbit')
except Exception as e:
    print(f'Error: {e}')
    print('No need to worry, the images are saved in the directory, you can create the movie using the following command:')
    print(f'python plotTheOrbitData.py --l1c_dir {l1c_dir} --movie-only 1')
    sys.exit(1)

#-----------------------end of script---------------------------#