from matplotlib import pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap

class Plot:
    def __init__(self, data):
        self.data = data
        self.bandAngles = range(80, 90)
        self.plotDPI = 160

    def setDPI(self, dpi):
        self.plotDPI = dpi if not dpi==None else None
        print('setting dpi to %dppi', self.plotDPI)
        plt.rcParams['figure.dpi'] = self.plotDPI
    

    def plotPixel(self, x, y, dataVar='i', xAxis='scattering_angle'):
        plt.plot(self.data[xAxis][x,y,self.bandAngles], self.data[dataVar][x, y, self.bandAngles, 0])
        plt.xlabel(xAxis)
        plt.ylabel(dataVar)
        plt.show()

    def plotRGB(self):
        # Create a 3D array to store the RGB datas
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
