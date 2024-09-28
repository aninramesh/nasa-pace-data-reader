# Imports
import os
from netCDF4 import Dataset
import datetime
from matplotlib import pyplot as plt
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
from scipy import interpolate

# cartopy related imports
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

class L2:
    """Class for reading
        NASA PACE Level 2 product files.
        
    """

    def __init__(self):
        """Initializes the class."""
        self.instrument = 'HARP2'   # Default instrument
        self.product = 'GRASP-Anin' # Default product
        self.var_units = {}
        self.setInstrument()

    def setInstrument(self, instrument=None):
        """Sets the instrument.
        
        Args:
            instrument (str): The instrument name.

        """
        self.instrument = instrument if instrument else 'HARP2'
        self.l2product = self.instrument + '-' + self.product

        match self.l2product.lower():

            case 'harp2-grasp-anin':

                self.geoNames = ['latitude', 'longitude']
                self.geophysicalNames = ['aot', 'aot_fine', 'aot_coarse', 'fmf',
                                         'mi', 'mr',
                                         'ssa_total', 'angstrom', 'alh', 'spherFrac',
                                         'rv_fine', 'rv_coarse',
                                         'reff_coarse', 'reff_fine', 'vd',
                                         'surfaceAlbedo', 'brdfP1', 'brdfP2', 'brdfP3',
                                         'bpdfP1', 'waterP1', 'waterP2', 'waterP3', 'windspeed']
                
                self.diagnosticNames = ['chi2', 'n_iter', 'quality_flag']

    def read(self, filename):
        """Reads the data from the file.
        
        Args:
            filename (str): The name of the file to read.

        Returns:
            dict: A dictionary containing the data.

        """
        

        print(f'Reading {self.instrument}-{self.product} products from {filename}...')

        correctFile = self.checkFile(filename)
        if not correctFile:
            print(f'Error: {filename} does not contain {self.instrument}-{self.product} L2 file.')
            return

        dataNC = Dataset(filename, 'r')
        data = {}
        data['_units'] = {}

        try:

            # HACK: get the date time from the filename 
            data['date_time'] = dataNC.date_created

            # Access the 'geophysical_data' & 'geolocation_data' group
            geophysical_data = dataNC.groups['geophysical_data']
            geo_data = dataNC.groups['geolocation_data']
            sensor_data = dataNC.groups['sensor_band_parameters']
            diagnostic_data = dataNC.groups['diagnostic_data']

            # diagnostic data
            for var in self.diagnosticNames:
                data[var] = diagnostic_data.variables[var][:]

            # Define the variable names
            geo_names = self.geoNames

            # Read the variables
            for var in geo_names:
                data[var] = geo_data.variables[var][:]

            # Read the data
            geophysical_names = self.geophysicalNames

            data['_units'] = {}
            for var in geophysical_names:
                try:
                    data[var] = geophysical_data.variables[var][:]

                    # read the units for the variable
                    data['_units'][var] = geophysical_data.variables[var].units
                    self.unit(var, geophysical_data.variables[var].units)
                except KeyError as e:
                    print(f'Error: {filename} does not contain the required variables.')
                    print('Error:', e)
                    print('Maybe the file is L1C experimental?')

            # read the F0 and unit
            data['wavelengths'] = sensor_data.variables['wavelength'][:]
            data['_units']['wavelengths'] = sensor_data.variables['wavelength'].units
            self.unit(var, geophysical_data.variables[var].units)

            # close the netCDF file
            dataNC.close()

            # add to the object
            self.l2_dict = data

            return data

        except KeyError as e:
            print(f'Error: {filename} does not contain the required variables.')
            print('Error:', e)

    
            # close the netCDF file
            dataNC.close()

    def unit(self, var, units):
            """Returns the units for the variable."""
            self.var_units[var] = units 
    
    def checkFile(self, filename):
        """Checks if the file is a correct L2 file.
        
        Args:
            filename (str): The name of the file to check.

        Returns:
            bool: True if the file is correct, False otherwise.

        """
        try:
            dataNC = Dataset(filename, 'r')
            # check if the metadata is present and is correct
            if 'title' not in dataNC.ncattrs():
                dataNC.close()
                return False
            else:
                if dataNC.title != 'PACE HARP2 Level-2 data':
                    dataNC.close()
                    return False
            dataNC.close()
            return True
        except:
            return False
    

    # Plotting functions
    def projectVar(self, var, wavelength=None,
                   proj='PlateCarree', dpi=300,
                   noAxisTicks=False,
                   black_background=False, ax=None, fig=None,
                   chi2Mask=None, saveFig=False, rgb_extent=None,
                   horizontalColorbar=False, limitTriangle= [0, 0],
                   savePath=None, aod_mask=None,
                **kwargs):
        """Plots the variable in a specific projection.

        Args:
            var (str): The variable to plot.
            viewAngle (float): The viewing angle.
            proj (str): The projection to use.
            dpi (int): The resolution of the plot.

        """
        assert proj in ['PlateCarree', 'Orthographic'], 'Error: Invalid projection.'
        # assert var in self.diagnosticNames[:] or var in self.geophysicalNames[:], 'Error: Invalid variable.'
        
        # no viewing angle only wavelength
        lat = self.l2_dict['latitude']
        lon = self.l2_dict['longitude']

        # wavelength
        if wavelength is None:
            wavelength = 550
        else:
            assert wavelength in self.l2_dict['wavelengths'], 'Error: Invalid wavelength.'

        # get the index of the wavelength
        idx = np.where(self.l2_dict['wavelengths'] == wavelength)[0][0]

        # get the variable
        if var in ['chi2', 'n_iter', 'quality_flag',
                        'reff_coarse', 'reff_fine', 'vd',
                        'windspeed', 'angstrom', 'alh', 'spherFrac']:
            data = self.l2_dict[var][:, :]
        else:
            data = self.l2_dict[var][:, :, idx]

        # create the plot
        if ax is None:
            fig = plt.figure(figsize=(3, 3), dpi=dpi)
            ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        if black_background:
            # Set the background color to black
            fig.patch.set_facecolor('black')
            # set the font color to white
            plt.rcParams['text.color'] = 'tan'
            plt.rcParams['axes.labelcolor'] = 'grey'
            plt.rcParams['xtick.color'] = 'tan'
            plt.rcParams['ytick.color'] = 'tan'
            # title font color
            plt.rcParams['axes.titlecolor'] = 'white'
            plt.rcParams['axes.edgecolor'] = 'tan'
            plt.rcParams['axes.facecolor'] = 'tan'

        if var in ['chi2', 'n_iter', 'quality_flag',
                    'reff_coarse', 'reff_fine', 'vd',
                    'windspeed', 'angstrom', 'alh', 'spherFrac']:
            ax.set_title(f'{var}')
        else:
            ax.set_title(f'{var} at {wavelength} nm')
        ax.coastlines()
        # background
        ax.add_feature(cfeature.LAND, alpha=0.5)
        ax.add_feature(cfeature.OCEAN, alpha=0.5)
        ax.add_feature(cfeature.LAKES, alpha=0.1)
        ax.add_feature(cfeature.RIVERS, alpha=0.1)
        # ax.add_feature(cfeature.BORDERS, linestyle='--', lw=0.5)

        # plot the variable
        # mask data if chi2mask is provided
        if chi2Mask is not None:
            data = np.ma.masked_where(chi2Mask, data)

        # mask data if aod_mask is provided
        if aod_mask is not None:
            data = np.ma.masked_where(aod_mask, data)
            
        if rgb_extent is not None:
            im = ax.imshow(data, origin='lower', extent=rgb_extent, transform=ccrs.PlateCarree(), **kwargs)
        else:
            im = ax.pcolormesh(lon, lat, data, transform=ccrs.PlateCarree(), **kwargs)
        divider = make_axes_locatable(ax)
        if horizontalColorbar:
            ax_cb = divider.new_vertical(size="5%", pad=0.65, axes_class=plt.Axes)
        else:
            ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

        fig.add_axes(ax_cb)

        # add horizontal colorbar
        orientation = 'vertical'
        if horizontalColorbar:
            orientation = 'horizontal'
            # vmax in kwargs then end of the colorbar with a triangle
            if 'vmax' in kwargs or 'vmin' in kwargs:
                # add a triangle at the end of the colorbar if vmax and vmin are provided
                if 'vmax' in kwargs and 'vmin' in kwargs:
                    if limitTriangle[0] and limitTriangle[1]:
                        plt.colorbar(im, cax=ax_cb, orientation=orientation, extend='both')
                    elif limitTriangle[0]:
                        plt.colorbar(im, cax=ax_cb, orientation=orientation, extend='min')
                    elif limitTriangle[1]:
                        plt.colorbar(im, cax=ax_cb, orientation=orientation, extend='max')
            else:
                plt.colorbar(im, cax=ax_cb, orientation=orientation)
        else:
            if 'vmax' in kwargs or 'vmin' in kwargs:
                # add a triangle at the end of the colorbar if vmax and vmin are provided
                if limitTriangle[0] and limitTriangle[1]:
                    plt.colorbar(im, cax=ax_cb, orientation=orientation, extend='both')
                elif limitTriangle[0]:
                    plt.colorbar(im, cax=ax_cb, orientation=orientation, extend='min')
                elif limitTriangle[1]:
                    plt.colorbar(im, cax=ax_cb, orientation=orientation, extend='max')
            else:
                plt.colorbar(im, cax=ax_cb)

        # set colorbar label
        if var not in ['chi2', 'n_iter', 'quality_flag']:
            plt.colorbar(im, cax=ax_cb, orientation=orientation).set_label(self.var_units[var])

        # # add gridlines and lat lon labels
        # if not noAxisTicks and ax is not None:
        #     gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
        #                     linewidth=0.2, color='gray', alpha=0.2, linestyle='--')
        #     gl.xlabels_top = False
        #     gl.ylabels_right = False
        #     gl.xformatter = LONGITUDE_FORMATTER
        #     gl.yformatter = LATITUDE_FORMATTER
        #     gl.xlabel_style = {'size': 8}
        #     gl.ylabel_style = {'size': 8}
        #     gl.xlabel_text = True
        #     gl.ylabel_text = True

        if black_background:
            #reset the font color
            plt.rcParams['text.color'] = 'black'
            plt.rcParams['axes.labelcolor'] = 'black'
            plt.rcParams['xtick.color'] = 'black'
            plt.rcParams['ytick.color'] = 'black'
            # title font color
            plt.rcParams['axes.titlecolor'] = 'black'
            plt.rcParams['axes.edgecolor'] = 'black'
            plt.rcParams['axes.facecolor'] = 'white'

        # save the image withouth the axis and gridlines with the transparent background
        if saveFig:
            if savePath is None:
                fig.savefig(f'{var}_wavelength_{wavelength}_nm.png', dpi=dpi, transparent=True)
            else:
                # make sure the path exists
                if not os.path.exists(savePath):
                    os.makedirs(savePath)
                full_path = os.path.join(savePath, f'{var}_wavelength_{wavelength}_nm.png')
                fig.savefig(full_path, dpi=dpi, transparent=True)
        
        plt.show()


