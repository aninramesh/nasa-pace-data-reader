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
    
# parser = argparse.ArgumentParser(description='Generate RGB images from L1C files')
parser = argparse.ArgumentParser(description='Generate RGB images/movie from L1C files')
parser.add_argument('--l1c_dir', type=str, required=True, help='L1C dir to process')

args_ = parser.parse_args()

# List of L1C files from a directory
l1c_dir = Path(args_.l1c_dir)
l1c_files = sorted(Path(l1c_dir).glob('*.nc'))

# rgb_ dict
rgb_ = {}
rgb_['rgb_new'] = {}
rgb_['rgb_extent'] = {}

# Define the figure handle
fig = plt.figure(dpi=200, figsize=(5, 5))
args = Args()
args.dpi = 200
temp_num = 0

# Loop through the L1C files
for l1c_file in l1c_files:
    
    args.l1c_file = str(l1c_file)
    args.save_path = l1c_file.with_suffix('.png')
    print('Projecting RGB for:', args.l1c_file)
    if temp_num == 0:
        ax_new = plotL1C(args, fig, rgb_)
    else:
        ax_new = plotL1C(args, fig, rgb_, temp_num=temp_num)
    temp_num += 1

# Make a movie from the images
# movie directory
movie_dir = f'{l1c_dir}/movie'
os.makedirs(movie_dir, exist_ok=True)
makeMovieFromImages(l1c_dir, movie_dir=movie_dir,  movie_name='FullOrbit')