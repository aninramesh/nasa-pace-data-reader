from matplotlib import pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap

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
                    'font.family': 'cmr10',
                    'axes.unicode_minus': False
        })

    def setBandAngles(self, band):
        """Set the band angles for the plot.
        Args:
            bandAngles (list): The band angles for the plot.

        Returns:
            None
        """
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
        fig, ax = plt.subplots(figsize=(3, 2))
        plot_func = ax.plot if axis else plt.plot

        dataVar_, unit_ = self.physicalQuantity(x, y, dataVar, xAxis)

        if axisLabel:
            plt.xlabel(xAxis)
            plt.ylabel(f'{dataVar}\n{unit_}') if unit_ else plt.ylabel(r'R$_%s$' %dataVar)
            plt.title(f'Pixel ({x}, {y}) of the instrument {self.instrument}')
        
        plot_func(self.data[xAxis][x,y,self.bandAngles], dataVar_, **kwargs)
        
        plt.show()

        if returnHandle:
            return fig, ax
        
    def physicalQuantity(self, x, y, dataVar='i', xAxis='scattering_angle',):
        # plot reflectance or radiance
        if self.reflectance and dataVar in ['i', 'q', 'u']:
            # πI/F0
            dataVar_ = self.data[dataVar][x, y, self.bandAngles, 0]*np.pi/self.data['F0'][self.bandAngles, 0]
            unit_= ''
        else:
            dataVar_ = self.data[dataVar][x, y, self.bandAngles, 0]
            unit_ = '('+self.data['_units'][dataVar]+')'
        return dataVar_, unit_

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

                dataVar_, unit_ = self.physicalQuantity(x, y, vars, xAxis)

                # plot the data
                axAll[i,j].plot(self.data[xAxis][x,y,self.bandAngles], dataVar_,
                                '%so-' %colors[j],
                                label= vars if j ==0 else None, **kwargs)
                
                if axisLabel and j == 0:
                    axAll[i,j].set_ylabel(f'{vars}\n{unit_}') if unit_ and showUnit else axAll[i,j].set_ylabel(r'R$_%s$' %vars)
                    axAll[i,j].yaxis.set_label_coords(-0.25,0.5)

                if axisLabel and i == len(self.vars2plot)-1:
                    axAll[i,j].set_xlabel(xAxis)
        plt.suptitle(f'Pixel ({x}, {y}) of the instrument {self.instrument}')
        plt.tight_layout()
        plt.show()

        if saveFig:
            location = f'./{self.instrument}_pixel_{x}_{y}.png'
            figAll.savefig(location, dpi=self.plotDPI)

    def plotRGB(self):
        # Create a 3D array to store the RGB data
        rgb = np.zeros((self.data['i'].shape[0], self.data['i'].shape[1], 3), dtype=np.float32)
        rgb[:, :, 0] = self.data['i']
        rgb[:, :, 1] = self.data['q']
        rgb[:, :, 2] = self.data['u']

        # Plot the RGB image
        plt.imshow(rgb)
        plt.show()

    # Plot projected RGB using Basemap
    def plotProjectedRGB(self, lat, lon):
        # Create a 3D array to store the RGB data
        rgb = np.zeros((self.data['i'].shape[0], self.data['i'].shape[1], 3), dtype=np.float32)
        rgb[:, :, 0] = self.data['i']
        rgb[:, :, 1] = self.data['q']
        rgb[:, :, 2] = self.data['u']

        # Create a Basemap instance
        m = Basemap(projection='cyl', llcrnrlat=lat.min(), urcrnrlat=lat.max(), llcrnrlon=lon.min(), urcrnrlon=lon.max(), resolution='c')

        # Plot the projected RGB image
        m.imshow(rgb)
        plt.show()
