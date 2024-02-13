# NASA-PACE-Data-Reader

This repository hosts a Python package designed to read L1C files from NASA PACE instruments, including HARP2, SPEXone, and OCI. Future development plans include the addition of readers for L2 aerosol and surface products.

## Building and Uploading the Package:

To build and upload the package, you can either run the `sh Install.sh` script (ensure to specify the correct version).

---

## Example Usage:

Here is a simple example of how to use the package:

```Python
from nasa_pace_data_reader import L1

# Location of the file
fileName = '/Users/aputhukkudy/Downloads/PACE_HARP2.20220321T101844.L1C.5.2KM.V03.SIM2.1_.nc'

# Read the file
l1c = L1.L1C()
l1c_dict = l1c.read(fileName)

# Print the keys and the shape of the data
[print('{:>24}: {}'.format(key, l1c_dict[key].shape)) for key in l1c_dict.keys()][0]

pixel = [250,300]

# Load the plot class
plt_ = plot.Plot(l1c_dict)

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
```

---

## Change Log:

---

## Key Improvements:

