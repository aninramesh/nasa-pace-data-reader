from nasa_pace_data_reader import L1, plot

# suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Define the location of the file
fileOCI = '/Users/aputhukkudy/Downloads/OCI-Dark/South/PACE_OCI.20240307T054913.L1C.5km.nc'

# Read the file
l1c = L1.L1C(instrument='OCI')
l1c_dict = l1c.read(fileOCI)

#--------------------------------------------------------------
# Print the keys and the shape of the data (Just to see what is in the file)
l1c_dict.keys()
for key in l1c_dict.keys():
    if key != '_units':
        try:
            print('{:<24}:{}'.format(key, l1c_dict[key].shape))
        except AttributeError:
            print('Error reading the key: {}'.format(key))
#--------------------------------------------------------------

# Define the pixel
pixel = [77,206]

# Load the plot class (default instrument is HARP2)
plt_ = plot.Plot(l1c_dict, instrument = 'OCI')

# Read the 'i' for a pixel
iStr ='i'
i = l1c_dict[iStr][pixel[0], pixel[1], plt_.bandAngles]

plt_.plotRGB(normFactor=300, scale=1, saveFig=False, dpi=300)
# plt_.projectedRGB(normFactor=300, scale=1, saveFig=False, dpi=300)

#%%
# Plot the pixel (By default plotting radiance)
plt_.plotPixel(pixel[0], pixel[1], dataVar='i', linewidth=0.5, alpha=0.5, ms=1, marker='o', linestyle='-')

# plot reflectance for the same pixel with some kwargs
plt_.reflectance = True
plt_.plotPixel(pixel[0], pixel[1], dataVar='i',  color= 'r',
               linewidth=0.5, alpha=0.5, ms=1, marker='o', 
               linestyle='-', label='Reflectance', xlim=[300, 900],
               maskFlag=False)
