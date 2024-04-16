#!/usr/bin/env python
# Python script to generate HARP2 RGB Images in orthographic projection and plot the orbit using
# multiple L1C files

# Load the required libraries
from nasa_pace_data_reader import L1, plot
from datetime import datetime
import os
import sys
import pickle
import argparse
import gc
from pathlib import Path

# plot libraries
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

def plotL1C(args, fig_, rgb_, temp_num=0, viewIndex=[36, 4, 84]):
    """ Plot the L1C file in orthographic projection"""

    # Read the file
    l1c = L1.L1C()
    try:
        l1c_dict = l1c.read(args.l1c_file)

        # just the filename
        l1c_file = os.path.basename(args.l1c_file)

        # save path join movie directory and filename
        args.save_path = f'{args.movie_dir}/{l1c_file.replace(".nc", ".png")}'

        # Load the plot class (default instrument is HARP2)
        plt_ = plot.Plot(l1c_dict)

        # plot RGB in Orthographic projection with fixed latitude
        lat_0 = None if args.fixed_lat == 0 else 0
        # assert if fixed_lon is between -180 and 180
        assert -180 <= args.fixed_lat <= 180, 'Error: fixed_lat must be between -180 and 180'
        lon_0 = None if args.fixed_lon == 0 else args.fixed_lon


        # normFactor
        # normFactor = args.normFactor
        normFactor = args_.normFactor
        if args.viewIndex >= 4:
            scale_=[0.85, 1.4, 1]
        else:
            scale_ = [1, 1, 1]

        # plot RGB in Orthographic projection
        fig2, ax2, rgb_['rgb_new'][l1c_file], \
            rgb_['rgb_extent'][l1c_file], \
                rgb_['dateline'][l1c_file], rgb_['lon_center'][l1c_file], \
                     rgb_['lat_center'][l1c_file] = plt_.projectedRGB(proj='Orthographic', viewAngleIdx=viewIndex,
                                                            normFactor=normFactor, scale=scale_, saveFig=True, returnRGB=True, # type: ignore
                                                            figsize=(6, 6), noShow=True, savePath=args.save_path,
                                                            lat_0=lat_0, lon_0=lon_0, proj_size=(1200, 600), highResStockImage=True,
                                                            returnTransitionFlag=True)
        
        gc.collect()
        if temp_num > 0:
            # plot the orbit with previous L1C files
            for key in rgb_['rgb_new']:
                if rgb_['dateline'][key]:
                    ax2.imshow(rgb_['rgb_new'][key], origin='lower', extent=rgb_['rgb_extent'][key], transform=ccrs.PlateCarree(central_longitude=rgb_['lon_center'][key]))
                else:
                    ax2.imshow(rgb_['rgb_new'][key], origin='lower', extent=rgb_['rgb_extent'][key], transform=ccrs.PlateCarree())
                gc.collect()
            fig2.savefig(str(args.save_path).replace('.png', '_seq.png'), dpi=args.dpi)
        else:
            fig2.savefig(str(args.save_path).replace('.png', '_seq.png'), dpi=args.dpi)
        
        return ax2
    except Exception as e:
        print(f'Error: {e}')
        if "NetCDF: HDF error" in str(e):
            print(f'Error: {args.l1c_file} has netCDF error')
            print('---'*10)
            os.system(f'rm -f {args.l1c_file}')
            print(f'Error: {args.l1c_file} has been removed')
            print('---'*10)
        return None

def makeMovieFromImages(movie_dir ,movie_name='movie', px=1600, codec='mpeg4'):
    """ Stitch the images in a directory into a movie
    
    Args:
        dir (str): Path to the directory containing the images
    """

    # List of images
    images = sorted(Path(movie_dir).glob('*L1C.5km.png'))

    # Create the movie using list of images in mac os
    for i, image in enumerate(images):
        os.system(f'convert {image} -resize {px}x{px} {movie_dir}/{i:04d}.png')
        seq_image = str(image).replace('.png', '_seq.png')
        os.system(f'convert {seq_image} -resize {px}x{px} {movie_dir}/{i:04d}_seq.png')
    
    # Create the movie using list of images
    """
    if codec == 'mpeg4':
        os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d.png -vcodec mpeg4 -pix_fmt yuv420p -y {movie_dir}/{movie_name}.mp4')
        os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d_seq.png -vcodec mpeg4 -pix_fmt yuv420p -y {movie_dir}/{movie_name}_seq.mp4')
    elif codec == 'libx264':
        os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d.png -vcodec libx264  -y {movie_dir}/{movie_name}.mp4')
        os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d_seq.png -vcodec libx264 -y {movie_dir}/{movie_name}_seq.mp4')
    elif codec == 'h264':
        os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d.png -c h264 -y {movie_dir}/{movie_name}.mp4')
        os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d_seq.png -c h264  -y {movie_dir}/{movie_name}_seq.mp4')
    
    """
    if codec == 'mpeg4':
        os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d.png -vcodec mpeg4 -crf 0 -y {movie_dir}/{movie_name}.mp4')
        os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d_seq.png -vcodec mpeg4 -crf 0 -y {movie_dir}/{movie_name}_seq.mp4')
    elif codec == 'libx264':
        os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d.png -vcodec libx264  -y {movie_dir}/{movie_name}.mp4')
        os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d_seq.png -vcodec libx264 -y {movie_dir}/{movie_name}_seq.mp4')
    elif codec == 'h264':
        os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d.png -c libx264 -crf 18 -preset ultrafast -pix_fmt yuv420p -y {movie_dir}/{movie_name}.mp4')
        os.system(f'ffmpeg -r 1 -i {movie_dir}/%04d_seq.png -c libx264 -crf 18 -preset ultrafast -pix_fmt yuv420p -y {movie_dir}/{movie_name}_seq.mp4')
    

#--------------------------------------------------------------#
# arguments
#--------------------------------------------------------------#
    
# check if imagemagick and ffmpeg are installed/loaded (in NyX automatically loaded by the spack)
if os.system('which convert') != 0:
    print('Error: imagemagick is not installed')
    print('Please install imagemagick using the following command (NyX): spack load imagemagick')
    if 'nyx' in os.environ['HOSTNAME']:
        os.system('spack load imagemagick')
    else:
        sys.exit(1)

if os.system('which ffmpeg') != 0:
    print('Error: ffmpeg is not installed')
    print('Please install ffmpeg using the following command (NyX): spack load ffmpeg')
    if 'nyx' in os.environ['HOSTNAME']:
        os.system('spack load ffmpeg')
    else:
        sys.exit(1)

#--------------------------------------------------------------#     
# Parse the command-line arguments
#-- required arguments
parser = argparse.ArgumentParser(description='Generate RGB images/movie from L1C files')
parser.add_argument('--l1c_dir', type=str, required=True, help='L1C dir to process')

#-- optional arguments
parser.add_argument('--dpi', type=int, required=False, default=400, help='DPI of the saved figure')
parser.add_argument('--movie-only', type=bool, required=False, default=False, help='Create movie only')
parser.add_argument('--normFactor', type=int, required=False, default=400, help='Normalization factor for the RGB image')
parser.add_argument('--viewIndex', type=int, required=False, default=0, help='Viewing angle for the RGB image option: 0 = -8, 1 = -43, 2 = ~54, 3 = ~22')
parser.add_argument('--fixed_lat', type=int, required=False, default=0, help='Fixed latitude for the orthographic projection')
parser.add_argument('--fixed_lon', type=int, required=False, default=0, help='Fixed longitude for the orthographic projection')
parser.add_argument('--time_range', type=bool, required=False, default=0, help='Time range for the L1C files')

args_ = parser.parse_args()

#--------------------------------------------------------------#
# args = Args()
# args.dpi = args_.dpi
# args.normFactor = args_.normFactor
# args.fixed_lat = args_.fixed_lat

#--------------------------------------------------------------#
# DEBUG
#--------------------------------------------------------------#
# args_ = Args()
# args_.dpi = 300
# args_.normFactor = 400
# args_.fixed_lat = 1
# args_.fixed_lat = 1
# args_.viewIndex = 0
# args_.movie_only = 0
# args_.viewIndex = 1
# args_.l1c_dir = '/Users/aputhukkudy/Downloads/03-11/hipp381/'
#--------------------------------------------------------------#


# List of L1C files from a directory
l1c_dir = Path(args_.l1c_dir)
l1c_files = sorted(Path(l1c_dir).glob('*5km.nc'))

# sort the L1C files by filename
l1c_files = sorted(l1c_files, key=lambda x: x.name)

#--------------------------------------------------------------#
# select l1c_files in a range (start, end) based on the PACE_HARP2.20240311TXXXX*5km.nc to PACE_HARP2.20240311TYYYY*5km.nc
if bool(args_.time_range):
    start = 'PACE_HARP2.20240311T051500'
    end = 'PACE_HARP2.20240311T065000'

    l1c_files = [x for x in l1c_files if start <= x.name <= end]

#--------------------------------------------------------------#

# rgb_ dict
rgb_ = {}
rgb_['rgb_new'] = {}
rgb_['rgb_extent'] = {}
rgb_['dateline'] = {}
rgb_['lon_center'] = {}
rgb_['lat_center'] = {}

#--------------------------------------------------------------

# viewIndex
if args_.viewIndex == 0:
    viewIndex = [36, 4, 84]
elif args_.viewIndex == 1:
    viewIndex = [19, 1, 81]
elif args_.viewIndex == 2:
    viewIndex = [67, 9, 89]
elif args_.viewIndex == 3:
    viewIndex = [49, 6, 86]
elif args_.viewIndex == 4:
    viewIndex = [36, 73, 84]
elif args_.viewIndex == 5:
    viewIndex = [19, 71, 81]
else:
    print('Error: viewIndex must be 0-5')
    sys.exit(1)

# Make a movie from the images
# movie directory
movie_dir = f'{l1c_dir}/movie_{str(args_.viewIndex)}' +'_Idx_lat'+str(args_.fixed_lat)
args_.movie_dir = movie_dir
os.makedirs(movie_dir, exist_ok=True)

# Define the figure handle
fig = plt.figure(dpi=args_.dpi, figsize=(12, 12))

temp_num = 0

# Loop through the L1C files
if not bool(args_.movie_only):
    for l1c_file in l1c_files:
        args_.l1c_file = str(l1c_file)
        args_.save_path = l1c_file.with_suffix('.png')
        print('Projecting RGB for:', args_.l1c_file)
        ax_new = plotL1C(args_, fig, rgb_, temp_num=temp_num, viewIndex=viewIndex)
        temp_num += 1
#--------------------------------------------------------------#
# Save the RGB_ dict
#--------------------------------------------------------------#
        
# Save the RGB dict
savePickle = False
if savePickle:
    with open(f'{movie_dir}/rgb_dict.pkl', 'wb') as f:
        pickle.dump(rgb_, f)
        print(f'RGB dict saved in {movie_dir}/rgb_dict.pkl')

gc.collect()
    
try:
    makeMovieFromImages(movie_dir=movie_dir,  movie_name='FullOrbit', px=1600, codec='h264') if bool(args_.movie_only) else None
except Exception as e:
    print(f'Error: {e}')
    print('No need to worry, the images are saved in the directory, you can create the movie using the following command:')
    print(f'python plotTheOrbitData.py --l1c_dir {l1c_dir} --movie-only 1')
    sys.exit(1)

#-----------------------end of script---------------------------#
