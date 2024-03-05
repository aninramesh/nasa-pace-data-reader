from nasa_pace_data_reader import L1, plot
from matplotlib import pyplot as plt
import numpy as np

# suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Location of the file
fileName = '/Users/aputhukkudy/Downloads/25/PACE_HARP2.20240304T123531.L1B.nc'

# Read the file
l1b = L1.L1B()
l1b_dict = l1b.read(fileName)

# %% Plot a variable
var2plot = 'i'
angleIdx = 3
plt.figure(figsize=(5,10))
im_data = l1b_dict[var2plot][angleIdx,:,:]
vmax = np.percentile(np.ravel(l1b_dict[var2plot][angleIdx,:,:]), 90)
plt.imshow(l1b_dict[var2plot][angleIdx,:,:], vmax=vmax, origin='lower')
plt.colorbar()
plt.title('Variable: {} at viewing angle: {} \nspectral band: {} nm'.format(var2plot, str(l1b_dict['view_angles'][angleIdx]),str(l1b_dict['intensity_wavelength'][angleIdx])))
plt.show()

# %% Project a variable
plt_ = plot.Plot(l1b_dict)
band = 'green'
plt_.setBand(band)
plt_.projectVar(var2plot, viewAngle=-20, level='L1B', saveFig=True)
var2plot = 'dolp'
plt_.projectVar(var2plot, viewAngle=-20, level='L1B', saveFig=True, vmax=0.3)