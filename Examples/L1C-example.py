from nasa_pace_data_reader import L1, plot

# suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Location of the file
fileName = '/Users/aputhukkudy/Downloads/PACE_HARP2.20240228T125638.L1C.nc'

# Read the file
l1c = L1.L1C()
l1c_dict = l1c.read(fileName)

# Print the keys and the shape of the data
l1c_dict.keys()
for key in l1c_dict.keys():
    if key != '_units' and key != 'date_time':
        try:
            print('{:<24}:{}'.format(key, l1c_dict[key].shape))
        except AttributeError:
            print('Error reading the key: {}'.format(key))
            

# Define the pixel
pixel = [330,440]

# Load the plot class (default instrument is HARP2)
plt_ = plot.Plot(l1c_dict)

# set which band to plot
band = 'Blue'
plt_.setBand(band)
'''
# plot RGB in default plate carree projection
plt_.plotRGB(normFactor=300, saveFig=True, dpi=300)

plt_.projectedRGB(normFactor=300, saveFig=True, dpi=300)

# plot RGB in with different view angle
plt_.projectedRGB(var='i', viewAngleIdx=[31, 3, 83], normFactor=300, saveFig=True)
# plt_.projectedRGB(var='q', viewAngleIdx=[31, 3, 83], scale=2, normFactor=100, saveFig=True)

#%% plot RGB in Orthographic projection
plt_.projectedRGB(proj='Orthographic', normFactor=300, saveFig=True, dpi=300)

# plot one variable in a specific projection at closest viewing angle to nadir
band = 'nIR'
plt_.setBand(band)
plt_.projectVar('i',  dpi=300)

# Plotting reflectance at closest viewing angle to -35 degrees
plt_.reflectance = True
plt_.projectVar('u',  viewAngle=-35)
'''
#------------------------------------------------
#%% plot RGB in Orthographic projection
# plt_.projectedRGB(proj='Orthographic', normFactor=300, saveFig=True, dpi=300)

# Read the 'i' for a pixel
iStr ='i'
i = l1c_dict[iStr][pixel[0], pixel[1], plt_.bandAngles]

# Plot the pixel (By default plotting radiance)
# plt_.setBand('all')
plt_.projectedRGB(normFactor=300, saveFig=True, dpi=300)
plt_.plotPixel(pixel[0], pixel[1])

# Plot the pixel reflectance
plt_.reflectance = True
# plt_.plotPixelVars(pixel[0], pixel[1], xAxis='view_angles')

# define the wavelengths and variables to plot
plt_.setInstrument()

# plot all vars and bands
plt_.plotPixelVars(pixel[0], pixel[1], xAxis='view_angles', alpha=0.5, linewidth=0.5, ms=2)

plt_.reflectance = False # switching back to radiance
plt_.plotPixelVars(pixel[0], pixel[1], xAxis='scattering_angle')

# plot only specific bands and vars
plt_.vars2plot = ['i',  'dolp']    # Order in the list is the order of plotting
plt_.bands2plot = ['blue', 'green', 'red', 'nir']   # Order in the list is the order of plotting

# plot radiance
plt_.reflectance = True
plt_.plotPixelVars(pixel[0], pixel[1], bands= plt_.bands2plot, xAxis= 'view_angles',
                   showUnit=False, alpha=0.5, linewidth=0.5) # you can pass any other arguments to the plot function
plt_.reflectance = False
plt_.plotPixelVars(pixel[0], pixel[1], bands= plt_.bands2plot, xAxis= 'scattering_angle',
                   showUnit=False, alpha=0.5, linewidth=0.5) # you can pass any other arguments to the plot function
