from nasa_pace_data_reader import L1, plot

# suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Define the location of the file
fileOCI = '/Users/aputhukkudy/Downloads/PACE/03-09/PACE_SPEXONE.20240309T115927.L1C.5km.nc'

# Read the file
l1c = L1.L1C(instrument='SPEXOne')
l1c_dict = l1c.read(fileOCI)

#--------------------------------------------------------------
# Print the keys and the shape of the data (Just to see what is in the file)
l1c_dict.keys()
for key in l1c_dict.keys():
    if key != '_units' and key != 'date_time':
        try:
            print('{:<24}:{}'.format(key, l1c_dict[key].shape))
        except AttributeError:
            print('Error reading the key: {}'.format(key))
#--------------------------------------------------------------

# Define the pixel
pixel = [68,260-244]

# Load the plot class (default instrument is HARP2)
plt_ = plot.Plot(l1c_dict, instrument = 'SpeXone')
plt_.setDPI(160)
# Read the 'i' for a pixel
iStr ='i'
i = l1c_dict[iStr][pixel[0], pixel[1], plt_.bandAngles]

plt_.setBand('HARP2')
# # Plot the pixel with radiance as the default. By default, the pixel is plotted in 10 bands. For 'i', every 40 spectral bands out of 400 are skipped. For dolp, every 5th band is plotted.
plt_.plotPixel(pixel[0], pixel[1], dataVar='i', linewidth=1, alpha=0.5, ms=1, marker='o', linestyle='-')
plt_.plotPixel(pixel[0], pixel[1], dataVar='i', linewidth=1, ms=1, marker='o', linestyle='-', xAxis='view_angles')
# plot reflectance for the same pixel with some kwargs
plt_.reflectance = True
plt_.plotPixel(pixel[0], pixel[1], dataVar='dolp',
                linewidth=1, ms=1, marker='o', 
                linestyle='-', label='Reflectance', xAxis='view_angles',)
# %%
plt_.reflectance = False
plt_.setBand('HARP2')
plt_.plotPixelVars(pixel[0], pixel[1], xAxis='view_angles', alpha=0.5, linewidth=0.5, ms=2)