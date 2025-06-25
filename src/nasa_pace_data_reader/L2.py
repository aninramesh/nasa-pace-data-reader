# Standard library and third-party imports for data handling, plotting, and scientific computation.
import os
import datetime
import numpy as np
from netCDF4 import Dataset
from scipy import interpolate

# Matplotlib and related imports for plotting.
from matplotlib import pyplot as plt
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Cartopy imports for geographical plotting.
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

class L2:
    """
    A class for reading and processing NASA PACE Level 2 product files.
    This class is primarily designed for HARP2 data processed with the GRASP-Anin algorithm.
    """

    def __init__(self):
        """Initializes the L2 data reader class."""
        self.instrument = 'HARP2'   # Default instrument
        self.product = 'GRASP-Anin' # Default product
        self.var_units = {}
        self.setInstrument()

    def setInstrument(self, instrument=None):
        """
        Configures the class for a specific instrument and product.

        Args:
            instrument (str, optional): The name of the instrument. Defaults to 'HARP2'.
        """
        self.instrument = instrument if instrument else 'HARP2'
        self.l2product = self.instrument + '-' + self.product

        match self.l2product.lower():

            case 'harp2-grasp-anin':
                # Define the names of geolocation, geophysical, and diagnostic variables.
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
        """
        Reads data from a specified L2 file.

        Args:
            filename (str): The path to the L2 file.

        Returns:
            dict: A dictionary containing the data from the file.
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

            # Access the different data groups within the NetCDF file.
            geophysical_data = dataNC.groups['geophysical_data']
            geo_data = dataNC.groups['geolocation_data']
            sensor_data = dataNC.groups['sensor_band_parameters']
            diagnostic_data = dataNC.groups['diagnostic_data']

            # Read diagnostic data.
            for var in self.diagnosticNames:
                data[var] = diagnostic_data.variables[var][:]

            # Read geolocation data.
            geo_names = self.geoNames
            for var in geo_names:
                data[var] = geo_data.variables[var][:]

            # Read geophysical data.
            geophysical_names = self.geophysicalNames
            data['_units'] = {}
            for var in geophysical_names:
                try:
                    data[var] = geophysical_data.variables[var][:]
                    # Store the units for each variable.
                    data['_units'][var] = geophysical_data.variables[var].units
                    self.unit(var, geophysical_data.variables[var].units)
                except KeyError as e:
                    print(f'Error: {filename} does not contain the required variables.')
                    print('Error:', e)
                    print('Maybe the file is L1C experimental?')

            # Read sensor band parameters.
            data['wavelengths'] = sensor_data.variables['wavelength'][:]
            data['_units']['wavelengths'] = sensor_data.variables['wavelength'].units
            self.unit(var, geophysical_data.variables[var].units)

            # Close the NetCDF file.
            dataNC.close()

            # Store the data dictionary in the class instance.
            self.l2_dict = data

            return data

        except KeyError as e:
            print(f'Error: {filename} does not contain the required variables.')
            print('Error:', e)

    
            # close the netCDF file
            dataNC.close()

    def unit(self, var, units):
            """
            Stores the units for a given variable.

            Args:
                var (str): The variable name.
                units (str): The unit string.
            """
            self.var_units[var] = units 
    
    def checkFile(self, filename):
        """
        Checks if the file is a valid L2 file for the specified product.

        Args:
            filename (str): The name of the file to check.

        Returns:
            bool: True if the file is a valid L2 file, False otherwise.
        """
        try:
            dataNC = Dataset(filename, 'r')
            # Check for the presence and correctness of the 'title' attribute.
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
        """
        Plots a specified variable on a geographical projection.

        Args:
            var (str): The variable to plot.
            wavelength (float, optional): The wavelength to plot. Defaults to 550 nm.
            proj (str, optional): The map projection to use. Defaults to 'PlateCarree'.
            dpi (int, optional): The resolution of the plot. Defaults to 300.
            noAxisTicks (bool, optional): If True, axis ticks are not shown. Defaults to False.
            black_background (bool, optional): If True, the plot background is black. Defaults to False.
            ax (matplotlib.axes.Axes, optional): An existing axes object to plot on. Defaults to None.
            fig (matplotlib.figure.Figure, optional): An existing figure object. Defaults to None.
            chi2Mask (np.ndarray, optional): A mask to apply to the data based on chi-squared values. Defaults to None.
            saveFig (bool, optional): If True, the figure is saved. Defaults to False.
            rgb_extent (list, optional): The extent of the plot. Defaults to None.
            horizontalColorbar (bool, optional): If True, a horizontal colorbar is used. Defaults to False.
            limitTriangle (list, optional): Specifies if triangles should be added to the colorbar limits. Defaults to [0, 0].
            **kwargs: Additional keyword arguments for the plotting function.
        """
        assert proj in ['PlateCarree', 'Orthographic'], 'Error: Invalid projection.'
        
        lat = self.l2_dict['latitude']
        lon = self.l2_dict['longitude']

        # Set the wavelength for the plot.
        if wavelength is None:
            wavelength = 550
        else:
            assert wavelength in self.l2_dict['wavelengths'], 'Error: Invalid wavelength.'

        # Get the index for the specified wavelength.
        idx = np.where(self.l2_dict['wavelengths'] == wavelength)[0][0]

        # Get the data for the specified variable.
        if var in ['chi2', 'n_iter', 'quality_flag',
                        'reff_coarse', 'reff_fine', 'vd',
                        'windspeed', 'angstrom', 'alh', 'spherFrac']:
            data = self.l2_dict[var][:, :]
        else:
            data = self.l2_dict[var][:, :, idx]

        # Create the plot figure and axes.
        if ax is None:
            fig = plt.figure(figsize=(3, 3), dpi=dpi)
            ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        if black_background:
            # Configure plot for a black background.
            fig.patch.set_facecolor('black')
            plt.rcParams['text.color'] = 'tan'
            plt.rcParams['axes.labelcolor'] = 'grey'
            plt.rcParams['xtick.color'] = 'tan'
            plt.rcParams['ytick.color'] = 'tan'
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
        # Add geographical features to the plot.
        ax.add_feature(cfeature.LAND, alpha=0.5)
        ax.add_feature(cfeature.OCEAN, alpha=0.5)
        ax.add_feature(cfeature.LAKES, alpha=0.1)
        ax.add_feature(cfeature.RIVERS, alpha=0.1)

        # Plot the data.
        if chi2Mask is not None:
            data = np.ma.masked_where(chi2Mask, data)

        # mask data if aod_mask is provided
        if aod_mask is not None:
            data = np.ma.masked_where(aod_mask, data)
            
        if rgb_extent is not None:
            im = ax.imshow(data, origin='lower', extent=rgb_extent, transform=ccrs.PlateCarree(), **kwargs)
        else:
            im = ax.pcolormesh(lon, lat, data, transform=ccrs.PlateCarree(), **kwargs)
        
        # Add a colorbar.
        divider = make_axes_locatable(ax)
        if horizontalColorbar:
            ax_cb = divider.new_vertical(size="5%", pad=0.65, axes_class=plt.Axes)
        else:
            ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

        fig.add_axes(ax_cb)

        orientation = 'vertical'
        if horizontalColorbar:
            orientation = 'horizontal'
            if 'vmax' in kwargs or 'vmin' in kwargs:
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
                if limitTriangle[0] and limitTriangle[1]:
                    plt.colorbar(im, cax=ax_cb, orientation=orientation, extend='both')
                elif limitTriangle[0]:
                    plt.colorbar(im, cax=ax_cb, orientation=orientation, extend='min')
                elif limitTriangle[1]:
                    plt.colorbar(im, cax=ax_cb, orientation=orientation, extend='max')
            else:
                plt.colorbar(im, cax=ax_cb)

        # Set the colorbar label.
        if var not in ['chi2', 'n_iter', 'quality_flag']:
            plt.colorbar(im, cax=ax_cb, orientation=orientation).set_label(self.var_units[var])

        if black_background:
            # Reset plot parameters to default.
            plt.rcParams['text.color'] = 'black'
            plt.rcParams['axes.labelcolor'] = 'black'
            plt.rcParams['xtick.color'] = 'black'
            plt.rcParams['ytick.color'] = 'black'
            plt.rcParams['axes.titlecolor'] = 'black'
            plt.rcParams['axes.edgecolor'] = 'black'
            plt.rcParams['axes.facecolor'] = 'white'

        # Save the figure if requested.
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


