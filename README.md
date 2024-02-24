# NASA-PACE-Data-Reader

This repository hosts a Python package designed to read L1C files from NASA PACE instruments, including HARP2, SPEXone, and OCI. Future development plans include the addition of readers for L2 aerosol and surface products.

## Dependencies
---
- Python v3.10 and above

## Installing the library from PyPi

To install the python library "`nasa-pace-data-reader`", follow these steps:

1. Open the command prompt or terminal.
2. Enter the command `pip install nasa-pace-data-reader`.
3. It is recommended to run this command in a separate `pip` or `conda` environment to prevent dependency conflicts.

## Installing from Github source code

1. `cd` to git directory
2. Enter the command `pip install -e ./`

## Building and Uploading the Package (For package maintainers):

To build and upload the package, you can either run the `sh Install.sh` script (ensure to specify the correct version).

---

## Example Usage:

See the example python notebook [Examples/L1C-example.ipynb](https://github.com/aninramesh/nasa-pace-data-reader/blob/main/Examples/L1C-example.ipynb)


Here is a simple example of how to use the package:

```Python
from nasa_pace_data_reader import L1, plot    # library

# Location of the file
fileName = '/Users/aputhukkudy/Downloads/PACE_HARP2.20220321T101844.L1C.5.2KM.V03.SIM2.1_.nc'

# Read the file
l1c = L1.L1C()
l1c_dict = l1c.read(fileName)

# Print the keys and the shape of the data
l1c_dict.keys()
for key in l1c_dict.keys():
    if key != '_units':
        print('{:<24}:{}'.format(key, l1c_dict[key].shape))

# Define the pixel
pixel = [250,300]

# Load the plot class
plt_ = plot.Plot(l1c_dict)

# set which band to plot
band = 'Blue'
plt_.setBand(band)

# Read the 'i' for a pixel
i = l1c_dict['i'][pixel[0], pixel[1], plt_.bandAngles]
print('i:', i)
print('viewing angles:', l1c_dict['view_angles'][plt_.bandAngles])

# Set the dpi
plt_.setDPI(256)

# set which band to plot
band = 'NIR'
plt_.setBand(band)

# Plot the pixel
plt_.plotPixel(pixel[0], pixel[1])

# define the wavelengths and variables to plot
plt_.setInstrument()

# plot all vars and bands
plt_.plotPixelVars(pixel[0], pixel[1])

# plot only specific bands and vars
plt_.vars2plot = ['i', 'q', 'u']    # Order in the list is the order of plotting
plt_.bands2plot = ['NIR', 'blue']   # Order in the list is the order of plotting

# plot 
plt_.plotPixelVars(pixel[0], pixel[1], bands= plt_.bands2plot, alpha=0.5, linewidth=0.5) # you can pass any other arguments to the plot function

# plot RGB image
# Load the plot class
plt_ = plot.Plot(l1c_dict)

# Plot RGB
plt_.plotRGB(scale=1, returnRGB=True)

# plot RGB in default plate carree projection
plt_.projectedRGB()

# plot RGB in Orthographic projection
plt_.projectedRGB(proj='Orthographic')

# plot one variable in a specific projection at closest viewing angle to nadir
band = 'Red'
plt_.setBand(band)
plt_.projectVar('i',  dpi=300)

# Plotting reflectance at closest viewing angle to -35 degrees
plt_.reflectance = True
plt_.projectVar('u',  viewAngle=-35)

```
---

## Change Log:
---
### v0.0.3.19
- Adjustments made to account for the accurate variable name in the L1C file.
- Implemented the option to plot L1B (HARP2).

### v0.0.3.18
- Masked the black pixels in the projected RGB

### v0.0.3.17
- Added the option to load `OCI` L1C file and plot the spectrum

### v0.0.3.16
- The bug related to plotting multiple band data has been resolved.

### v0.0.3.15
- Option to project one variable to the map
- the viewing angle can be specified easily

### v0.0.3.14

- Added the ability to plot projected RGB using `cartopy`.
- Removed `Basemap` library from the dependencies


