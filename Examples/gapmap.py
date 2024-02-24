# from src.nasa_pace_data_reader import L1
from nasa_pace_data_reader import L1
from nasa_pace_data_reader import plot
import importlib
import numpy as np
import os

# cartopy related imports
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from matplotlib import pyplot as plt
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy import interpolate

# list all files in a directory
# os.listdir('/Users/aputhukkudy/Downloads/')

fileName = '/Users/aputhukkudy/Downloads/L1beta.V01_RO-7.0_PO7.0_YO-83.0.nc'

# Load the L1beta
l1beta_ = L1.L1beta()
gapmap_data = l1beta_.read(fileName)

# print all the keys()
for i in gapmap_data.keys():
    print(i)

# -----
# data shift here
# -----
    
def exportData2CSV(data_dict, var2export= 'image_0',idx=6,
                   filename='gapmap'):
    # export data to csv
    data2export = data_dict[var2export][:,idx,:]

    #save in csv
    np.savetxt('gapmap%s_%s.csv' %(var2export,idx), data2export, delimiter=',')

def projectVar(data_dict, idx=5, var2plot='image_0',
               proj='PlateCarree', filename='gapmap', saveImage=True,
               **kwargs):
    
    # 2D data to plot
    data2plot = data_dict[var2plot][:,idx,:]

    # Get lat lon
    lat = data_dict['Latitude'][:, idx, :]
    lon = data_dict['Longitude'][:, idx, :]

    # center of the plot
    lon_center = (lon.max() + lon.min()) / 2
    lat_center = (lat.max() + lat.min()) / 2

    # default figsize
    figsize = (4, 5)  

    # Prepare figure and axes
    fig = plt.figure(figsize=figsize)

    if proj == 'PlateCarree':
        ax = plt.axes(projection=ccrs.PlateCarree())

        # Set up gridlines and labels
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True)
        gl.xlabels_top = False
        gl.ylabels_right = False
        gl.xlocator = mticker.FixedLocator(np.around(np.linspace(np.nanmin(lon),np.nanmax(lon),6),2))
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
    elif proj == 'Orthographic':
        ax = plt.axes(projection=ccrs.Orthographic(central_longitude=lon_center, central_latitude=lat_center))

     # setup the gridlines
    ax.coastlines()
    ax.set_global()
    ax.set_extent([lon.min(), lon.max(), lat.min(), lat.max()], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.OCEAN, zorder=0) ; ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
    # project image
    im = plt.contourf(lon, lat, data2plot, 600,
                      transform=ccrs.PlateCarree(), **kwargs)
    cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
    plt.colorbar(im, cax=cax)

     # set a margin around the data

    # plt.show()

    if saveImage:
        fig.savefig('gapmap%s_%s_%s.png' %(var2plot,idx, filename), dpi=300, bbox_inches='tight')
    plt.close(fig)

# projectVar(gapmap_data, idx=4, var2plot='image_0')
exportData2CSV(gapmap_data, var2export='image_0',idx=6)
print(gapmap_data['image_0'][0,6,0])
projectVar(gapmap_data, idx=6, var2plot='image_0', vmax=800, vmin=70)

