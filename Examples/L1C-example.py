from nasa_pace_data_reader import L1, plot

# Location of the file
fileName = '/Users/aputhukkudy/Downloads/yaw180/PACE_HARP2.20240223T213922.L1C.nc'

# Read the file
l1c = L1.L1C()
l1c_dict = l1c.read(fileName)

# Print the keys and the shape of the data
l1c_dict.keys()
for key in l1c_dict.keys():
    if key != '_units':
        print('{:<24}:{}'.format(key, l1c_dict[key].shape))

# Define the pixel
pixel = [190,200]

# Load the plot class (default instrument is HARP2)
plt_ = plot.Plot(l1c_dict)

# set which band to plot
band = 'Blue'
plt_.setBand(band)

# plot RGB in default plate carree projection
# plt_.projectedRGB()

# plot RGB in with different view angle
plt_.projectedRGB(var='i', viewAngleIdx=[31, 3, 83], normFactor=600, saveFig=True)
plt_.projectedRGB(var='q', viewAngleIdx=[31, 3, 83], scale=2, normFactor=100, saveFig=True)

#%% plot RGB in Orthographic projection
plt_.projectedRGB(proj='Orthographic')

# plot one variable in a specific projection at closest viewing angle to nadir
band = 'nIR'
plt_.setBand(band)
plt_.projectVar('i',  dpi=300)

# Plotting reflectance at closest viewing angle to -35 degrees
plt_.reflectance = True
plt_.projectVar('u',  viewAngle=-35)

#------------------------------------------------

# Read the 'i' for a pixel
iStr ='i'
i = l1c_dict[iStr][pixel[0], pixel[1], plt_.bandAngles]

# Plot the pixel (By default plotting radiance)
# plt_.setBand('all')

plt_.plotPixel(pixel[0], pixel[1])
# 

# Plot the pixel reflectance
plt_.reflectance = True


# define the wavelengths and variables to plot
plt_.setInstrument()

# plot all vars and bands
plt_.plotPixelVars(pixel[0], pixel[1], xAxis='view_angles')


# plot only specific bands and vars
plt_.vars2plot = ['i',  'u']    # Order in the list is the order of plotting
plt_.bands2plot = ['NIR', 'blue']   # Order in the list is the order of plotting

# plot radiance
plt_.reflectance = False # switching back to radiance
plt_.plotPixelVars(pixel[0], pixel[1], bands= plt_.bands2plot, xAxis= 'view_angles',
                   showUnit=False, alpha=0.5, linewidth=0.5) # you can pass any other arguments to the plot function

