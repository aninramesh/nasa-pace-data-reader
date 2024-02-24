from nasa_pace_data_reader import L1, plot
from matplotlib import pyplot as plt

# Location of the file
fileName = '/Users/aputhukkudy/Downloads/yaw180/PACE_HARP2.20240223T213922.L1B.nc'

# Read the file
l1b = L1.L1B()
l1b_dict = l1b.read(fileName)

# %% Plot a variable
var2plot = 'i'
angleIdx = 3
plt.figure(figsize=(5,10))
plt.imshow(l1b_dict[var2plot][angleIdx,:,:])
plt.colorbar()
plt.title('Variable: {} at viewing angle: {} \nspectral band: {} nm'.format(var2plot, str(l1b_dict['view_angles'][angleIdx]),str(l1b_dict['intensity_wavelength'][angleIdx])))
plt.show()

# %% Project a variable
plt_ = plot.Plot(l1b_dict)
band = 'green'
plt_.setBand(band)
plt_.projectVar(var2plot, viewAngle=-20, level='L1B', saveFig=True)