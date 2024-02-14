import os
from matplotlib import pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from scipy import interpolate

# cartopy related imports
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

class Plot:
    def __init__(self, data):
        self.data = data
        self.band = 'blue'
        self.bandAngles = range(80, 90)
        self.plotDPI = 160
        self.instrument = 'HARP2'
        self.reflectance = False
        self.setPlotStyle()


    def setPlotStyle(self):
        """Set the plot style for the plot.
        Args:
            None
        """
        plt.rcParams.update({
                    'xtick.direction': 'in',
                    'ytick.direction': 'in',
                    'ytick.right': 'True',
                    'xtick.top': 'True',
                    'mathtext.fontset': 'cm',
                    'figure.dpi': self.plotDPI,
                    'font.family': 'sans-serif',
                    'font.sans-serif': ['Tahoma'],
                    'axes.unicode_minus': False
        })


    def setBandAngles(self, band=None):
        """Set the band angles for the plot.
        Args:
            bandAngles (list): The band angles for the plot.

        Returns:
            None
        """
        band = self.band if band == None else band
        if self.instrument == 'HARP2':
            band_angle_ranges = {
                'blue': range(80, 90),
                'green': range(0, 10),
                'red': range(10, 70),
                'nir': range(70, 80)
            }
            self.bandAngles = band_angle_ranges.get(band, None)
        else:
            print('Instrument not supported yet. Please use HARP2.')


    def setBand(self, band):
        """Set the band for the plot.
        Args:
            band (str): The band for the plot.

        Returns:
            None
        """
        band_ = band.lower()
        assert band_ in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'], 'Invalid band'
        self.band = band_

        # set the angle specification based on the instrument
        self.setBandAngles(self.band)
        print(f'Band set to {self.band}')


    def setDPI(self, dpi):
        """Set the DPI for the plot.
        Args:
            dpi (int): The DPI for the plot.

        Returns:
            None
        """
        self.plotDPI = dpi if not dpi==None else None
        print('setting dpi to %d ppi' %self.plotDPI)
        plt.rcParams['figure.dpi'] = self.plotDPI


    def setInstrument(self, instrument=None):
        """Set the instrument for the plot.
        Args:
            instrument (str): The instrument for the plot.

        Returns:
            None
        """
        if instrument == None:
            instrument = self.instrument
        else:
            assert instrument.lower() in ['harp2', 'spexone', 'oci'], 'Invalid instrument'
            self.instrument = instrument

        if self.instrument == 'HARP2':
            self.bands = ['blue', 'green', 'red', 'nir']
            self.allBandAngles = [self.setBandAngles(band) for band in self.bands]

            # variable to plot
            self.vars2plot = ['i', 'q', 'u', 'dolp']

        print(f'Instrument set to {self.instrument}')


    def plotPixel(self, x, y, dataVar='i', xAxis='scattering_angle',
                  axis=None, axisLabel=True, returnHandle=False,
                    **kwargs):
        """Plot the data for a pixel.

        Args:
            x (int): The x coordinate of the pixel.
            y (int): The y coordinate of the pixel.
            dataVar (str): The variable to plot.
            xAxis (str): The x-axis variable.

        Returns:
            None
        """
        assert xAxis in ['scattering_angle', 'view_angles'], 'Invalid x-axis variable'
        fig, ax = plt.subplots(figsize=(3, 2))
        plot_func = ax.plot if axis else plt.plot

        xData_, dataVar_, unit_ = self.physicalQuantity(x, y, dataVar, xAxis=xAxis)

        if axisLabel:
            plt.xlabel(xAxis)
            plt.ylabel(f'{dataVar}\n{unit_}') if unit_ else plt.ylabel(r'R$_%s$' %dataVar)
            plt.title(f'Pixel ({x}, {y}) of the instrument {self.instrument}')
        
        plot_func(xData_, dataVar_, **kwargs)
        
        plt.show()

        if returnHandle:
            return fig, ax
        
    def physicalQuantity(self, x, y, dataVar='i', xAxis='scattering_angle',):
        """Get the physical quantity for the plot.

        Args:
            x (int): The x coordinate of the pixel.
            y (int): The y coordinate of the pixel.
            dataVar (str): The variable to plot.
            xAxis (str): The x-axis variable.

        Returns:
            xData_ (np.ndarray): The x-axis data.
            dataVar_ (np.ndarray): The y-axis data.
            unit_ (str): The unit of the data.
        """
        # plot reflectance or radiance
        if self.reflectance and dataVar in ['i', 'q', 'u']:
            # πI/F0
            dataVar_ = self.data[dataVar][x, y, self.bandAngles, 0]*np.pi/self.data['F0'][self.bandAngles, 0]
            unit_= ''
        else:
            dataVar_ = self.data[dataVar][x, y, self.bandAngles, 0]
            unit_ = '('+self.data['_units'][dataVar]+')' if not dataVar == 'dolp' else ''
        
        # for the scattering angle
        if xAxis == 'scattering_angle':
            xData_ = self.data[xAxis][x, y, self.bandAngles]
        # for the view angles
        elif xAxis == 'view_angles':
            xData_ = self.data[xAxis][self.bandAngles]

        return xData_, dataVar_, unit_

    def setFigure(self, figsize=(10, 5), **kwargs):
        """Set the figure size for the plot.
        Args:
            figsize (tuple): The figure size for the plot.

        Returns:
            None
        """

        if self.plotAll:
            # define the number of subplots
            print(f'...Setting the subplots with number of bands {len(self.bands2plot)} and number of variables {len(self.vars2plot)}')
            fig_, ax_ = plt.subplots(nrows = len(self.vars2plot), 
                                     ncols=len(self.bands2plot),
                                     figsize=figsize, sharex=True, **kwargs)
            
            return fig_, ax_


    
    # plot all bands in a single plot
    def plotPixelVars(self, x, y, xAxis='scattering_angle',
                     bands = None, saveFig=False,
                     axis=None, axisLabel=True, showUnit=True,
                    **kwargs):
        """
        Plot all bands for a pixel.

        Args:
            x (int): The x coordinate of the pixel.
            y (int): The y coordinate of the pixel.
            xAxis (str, optional): The x-axis variable. Defaults to 'scattering_angle'.
            bands (list, optional): List of bands to plot. If None, all bands are plotted. Defaults to None.
            saveFig (bool, optional): If True, the figure is saved. Defaults to False.
            axis (matplotlib.axes.Axes, optional): The axes object to draw the plot onto. If None, a new figure and axes are created. Defaults to None.
            axisLabel (bool, optional): If True, labels are added to the axes. Defaults to True.
            **kwargs: Variable length argument list to pass to the plot function.

        Returns:
            None
        """
        assert xAxis in ['scattering_angle', 'view_angles'], 'Invalid x-axis variable'
        if bands is None:
            self.plotAll = True
        self.bands2plot = self.bands if bands is None else bands

        # based on the instrument, set the band angles 
        if axis is None:
            # Define the size of each subplot
            subplot_size = (2, 1)
            rows = len(self.vars2plot)
            cols = len(self.bands2plot)

            # Calculate the figure size to keep a good aspect ratio
            figsize = (subplot_size[0] * cols, subplot_size[1] * rows)
            figAll, axAll = self.setFigure(figsize=figsize)
        else:
            axAll = axis

        # define color strings based on the length of the bands try to preserve the color
        colors = ['C%d' %i for i in range(cols)]
        
        # plot the data over different bands and variables
        for i, vars in enumerate(self.vars2plot):
            for j, band in enumerate(self.bands2plot):
                # Set the title for the column
                axAll[i,j].set_title(band) if i == 0 else None

                xData_, dataVar_, unit_ = self.physicalQuantity(x, y, vars, xAxis=xAxis)

                # plot the data
                axAll[i,j].plot(xData_, dataVar_,
                                '%so-' %colors[j],
                                label= vars if j ==0 else None, **kwargs)
                
                # set the labels
                if axisLabel and j == 0:
                    if (unit_ and showUnit):
                        axAll[i,j].set_ylabel(f'{vars}\n{unit_}') 
                    elif self.reflectance:
                        axAll[i,j].set_ylabel(r'R$_%s$' %vars) if not vars == 'dolp' else axAll[i,j].set_ylabel(vars)
                    else:
                        axAll[i,j].set_ylabel(vars)
                    axAll[i,j].yaxis.set_label_coords(-0.25,0.5)

                if axisLabel and i == len(self.vars2plot)-1:
                    axAll[i,j].set_xlabel(xAxis)

        plt.suptitle(f'Pixel ({x}, {y}) of the instrument {self.instrument}')
        plt.tight_layout()
        plt.show()

        # if saveFig is True, save the figure
        if saveFig:
            location = f'./{self.instrument}_pixel_{x}_{y}.png'
            figAll.savefig(location, dpi=self.plotDPI)

    def plotRGB(self, var='i', viewAngleIdx=[38, 4, 84],
                 scale= 1, normFactor=200, returnRGB=False,
                 plot=True, **kwargs):
        """Plot the RGB image of the instrument.

        Args:
            var (str, optional): The variable to plot. Defaults to 'i'.
            viewAngleIdx (list, optional): The view angle indices. Defaults to [38, 4, 84].
            scale (int, optional): The scale factor. Defaults to 1.
            normFactor (int, optional): The normalization factor. Defaults to 200.
            returnRGB (bool, optional): If True, the RGB data is returned. Defaults to False.
            plot (bool, optional): If True, the RGB image is plotted. Defaults to True.
            **kwargs: Variable length argument list to pass to the plot function.

        Returns:
            None
        """

        # find the index to plot
        idx = viewAngleIdx

        # Check the number of indices
        assert len(idx) == 3, 'Invalid number of indices'

        # Create a 3D array to store the RGB data
        rgb = np.zeros((self.data[var].shape[0], self.data[var].shape[1], 3), dtype=np.float32)
        rgb[:, :, 0] = self.data[var][:,:,idx[0],0]
        rgb[:, :, 1] = self.data[var][:,:,idx[1],0]
        rgb[:, :, 2] = self.data[var][:,:,idx[2],0]

        # if normFactor is scalar, divide the RGB by the scalar else divide in a loop
        if not isinstance(normFactor, int):
            for i in range(3):
                rgb[:, :, i] = rgb[:, :, i]/normFactor[i]*scale
        else:
            rgb = rgb/normFactor*scale
        # copy the rgb to a new variable

        # Plot the RGB image
        if plot:
            plt.imshow(rgb)
            plt.title(f'RGB image of the instrument {self.instrument}\n using "{var}" variable at angles {idx[0]}, {idx[1]}, {idx[2]}')
            plt.show()

        if returnRGB:
            self.rgb = rgb


    # Plot projected RGB using Cartopy
    def projectedRGB(self, rgb=None, scale=1, ax=None,
                     var='i', viewAngleIdx=[38, 4, 84],
                     normFactor=200, proj='PlateCarree',
                    **kwargs):
        """Plot the projected RGB image of the instrument using Cartopy.

        Args:
            rgb (np.ndarray, optional): The RGB data. Defaults to None.
            scale (int, optional): The scale factor. Defaults to 1.
            ax (matplotlib.axes.Axes, optional): The axes object to draw the plot onto. If None, a new figure and axes are created. Defaults to None.
            var (str, optional): The variable to plot. Defaults to 'i'.
            viewAngleIdx (list, optional): The view angle indices. Defaults to [38, 4, 84].
            normFactor (int, optional): The normalization factor. Defaults to 200.
            proj (str, optional): The projection method. Defaults to 'PlateCarree'.
            **kwargs: Variable length argument list to pass to the plot function.

        Returns:
            None
        """

        # if RGB does not exist, run the plotRGB method
        if rgb is None:
            self.plotRGB(var=var, viewAngleIdx=viewAngleIdx, scale=scale, normFactor=normFactor, returnRGB=True, plot=False,
                               **kwargs)

        # Check the shape of the RGB data
        assert self.rgb.shape[2] == 3, 'Invalid RGB data'

        # Get the latitude and longitude
        lat = self.data['latitude']
        lon = self.data['longitude']

        # Prepare figure and axes
        if ax is None:
            fig = plt.figure(figsize=(4, 5))

        rgb_new, nlon, nlat = self.meshgridRGB(lon, lat, return_mapdata=False) #Created projection image

        
        # Plotting in the axes
        lon_center = (lon.max() + lon.min()) / 2
        lat_center = (lat.max() + lat.min()) / 2

        # Create a border of the images        
        rgb_extent = [nlon.min(), nlon.max(), nlat.min(), nlat.max()]

        # Check the projection type
        if proj == 'Orthographic':
            # Create an Orthographic projection
            ax = plt.axes(projection=ccrs.Orthographic(lon_center, lat_center))
            ax.stock_img()
            ax.set_global()
            # Display the image in the projection
            ax.imshow(rgb_new, origin='lower', vmin=0, vmax=0.5, extent=rgb_extent, transform=ccrs.PlateCarree())

        elif proj == 'PlateCarree':
            # Create a PlateCarree projection
            ax = plt.axes(projection=ccrs.PlateCarree())
            # Set up gridlines and labels
            gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color='white', alpha=0.2, linestyle='--')
            gl.xlabels_top = False
            gl.ylabels_right = False
            gl.xlocator = mticker.FixedLocator(np.around(np.linspace(np.nanmin(nlon),np.nanmax(nlon),6),2))
            gl.xformatter = LONGITUDE_FORMATTER
            gl.yformatter = LATITUDE_FORMATTER
            # Display the image in the projection
            ax.imshow(rgb_new, origin='lower', vmin=0, vmax=0.5, extent=rgb_extent)
            # Add coastline feature
            ax.add_feature(cfeature.COASTLINE, edgecolor='black')

        else:
            # Handle invalid projection type
            print('Invalid projection method')

        # set a margin around the data
        ax.set_xmargin(0.05)
        ax.set_ymargin(0.05)

        plt.box(on=None)
        plt.show()


    def meshgridRGB(self, LON, LAT, proj_size=(905,400), return_mapdata=False):
        """Project the RGB data using meshgrid.

        This function takes longitude and latitude data along with optional parameters and returns the projected RGB data.
        
        Args:
            self (object): The instance of the class.
            LON (np.ndarray): The longitude data.
            LAT (np.ndarray): The latitude data.
            proj_size (tuple, optional): The size of the projection. Defaults to (905,400).
            return_mapdata (bool, optional): If True, the map data is returned. Defaults to False.
                
        Returns:
            np.ndarray: The projected RGB data.
            
        Raises:
            None
            
        Examples:
            # Create an instance of the class
            plot = Plot()
            
            # Define longitude and latitude data
            lon_data = np.array([0, 1, 2, 3, 4])
            lat_data = np.array([0, 1, 2, 3, 4])
            
            # Call the meshgridRGB function
            rgb_data = plot.meshgridRGB(lon_data, lat_data)
        """
        # for each color channel, the code sets the border pixels of the image to 0. 
        rr = self.rgb[:,:,0]
        rr[0:-1,0] = 0
        rr[0:-1,-1] = 0
        rr[0,0:-1] = 0
        rr[-1,0:-1] = 0
        gg = self.rgb[:,:,1]
        gg[0:-1,0] = 0
        gg[0:-1,-1] = 0
        gg[0,0:-1] = 0
        gg[-1,0:-1] = 0
        bb = self.rgb[:,:,2]
        bb[0:-1,0] = 0
        bb[0:-1,-1] = 0
        bb[0,0:-1] = 0
        bb[-1,0:-1] = 0

        # The code calculates the maximum and minimum latitude (mx_lat and mn_lat)
        # and longitude (mx_lon and mn_lon) from the LAT and LON arrays. 
        # It then calculates the midpoint of the latitude (lat0) and longitude (lon0)
        
        # Calculate the maximum and minimum latitude and longitude
        mx_lat = np.max(LAT)
        mn_lat = np.min(LAT)
        mx_lon = np.max(LON)
        mn_lon = np.min(LON)

        # Calculate the midpoint of the latitude and longitude
        lat0 = 1/2.*(mn_lat+mx_lat)
        lon0 = 1/2.*(mn_lon+mx_lon)

        # Set the size of the new projected image
        x_new = proj_size[0]
        y_new = proj_size[0]

        # Create 1D arrays of evenly spaced values between the min and max longitude and latitude
        xx = np.linspace(mn_lon,mx_lon,x_new)
        yy = np.linspace(mn_lat,mx_lat,y_new)

        # Create a 2D grid of coordinates
        newxx, newyy = np.meshgrid(xx,yy)

        # Interpolate the red, green, and blue color channels at the new grid points
        newrr = interpolate.griddata( (LON.ravel(),LAT.ravel()), rr.ravel(), (newxx.ravel(), newyy.ravel()), method='nearest',fill_value=0 )
        newgg = interpolate.griddata( (LON.ravel(),LAT.ravel()), gg.ravel(), (newxx.ravel(), newyy.ravel()), method='nearest',fill_value=0 )
        newbb = interpolate.griddata( (LON.ravel(),LAT.ravel()), bb.ravel(), (newxx.ravel(), newyy.ravel()), method='nearest',fill_value=0 )

        # Reshape the color channels to the size of the new image
        newrr = newrr.reshape(x_new,y_new)
        newgg = newgg.reshape(x_new,y_new)
        newbb = newbb.reshape(x_new,y_new)

        # Clip the color values to the range [0, 1] and remove any pixels where any of the color channels are 0
        newrr[newrr>1] = 1
        newrr[newrr<0] = 0
        newrr[newbb==0] = 0
        newrr[newgg==0] = 0

        newgg[newgg>1] = 1
        newgg[newgg<0] = 0
        newgg[newbb==0] = 0
        newgg[newrr==0] = 0

        newbb[newbb>=1] = 1
        newbb[newbb<0] = 0
        newbb[newrr==0] = 0
        newbb[newgg==0] = 0

        # Create a new 3D array for the projected RGB image
        rgb_proj = np.zeros([np.shape(newrr)[0],np.shape(newrr)[1],3])

        # Set the red, green, and blue channels of the new image
        rgb_proj[:,:,0] = newrr
        rgb_proj[:,:,1] = newgg
        rgb_proj[:,:,2] = newbb

        # If return_mapdata is True, return the map data
        if return_mapdata:
            return rgb_proj, (lon0,lat0), ((mn_lon,mx_lon),(mn_lat,mx_lat))
        else:
            return rgb_proj,xx,yy
        
