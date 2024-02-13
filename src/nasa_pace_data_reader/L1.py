import os
from netCDF4 import Dataset



class L1C:
    """Class for reading
        NASA PACE Level 1C data files.
        
    """

    def __init__(self):
        """Initializes the class."""
        self.instrument = 'HARP2'   # Default instrument
        self.product = 'L1C'        # Default product
        self.projectRGB = True      # Default project to RGB

        # viewing angle to plot
        self.viewing_angle = 'nadir'    # Default viewing angle options are 'nadir', 'aft' and 'forward'
    
    def __instrument__(self, instrument):
        """Sets the instrument."""
        self.instrument = instrument

    def __projectRGB__(self, projectRGB):
        """Sets the projectRGB."""
        self.projectRGB = projectRGB
    
    def __viewing_angle__(self, viewing_angle):
        """Sets the viewing angle."""
        self.viewing_angle = viewing_angle   

    def read(self, filename):
        """Reads the data from the file.
        
        Args:
            filename (str): The name of the file to read.

        Returns:
            dict: A dictionary containing the data.

        """
        print(f'Reading {self.instrument} data from {filename}')

        dataNC = Dataset(filename, 'r')
        data = {}

        try:

            # Access the 'observation_data' & 'geolocation_data' group
            obs_data = dataNC.groups['observation_data']
            geo_data = dataNC.groups['geolocation_data']
            
            # Define the variable names
            geo_names = ['latitude', 'longitude', 'scattering_angle', 'solar_zenith_angle', 
                        'solar_azimuth_angle', 'sensor_zenith_angle', 'sensor_azimuth_angle']

            # Read the variables
            for var in geo_names:
                data[var] = geo_data.variables[var][:]

            # Read the data
            obs_names = ['i', 'q', 'u']
            for var in obs_names:
                data[var] = obs_data.variables[var][:]

            # close the netCDF file
            dataNC.close()

            return data

        except KeyError as e:
            print(f'Error: {filename} does not contain the required variables.')
            print('Error:', e)

    
            # close the netCDF file
            dataNC.close()

        
class L1B:
    """Class for reading
        NASA PACE Level 1B data files.
        
    """

    def __init__(self):
        """Initializes the class."""
        self.instrument = 'HARP2'   # Default instrument
        self.product = 'L1B'        # Default product
        self.projectRGB = True      # Default project to RGB

        # viewing angle to plot
        self.viewing_angle = 'nadir'    # Default viewing angle options are 'nadir', 'aft' and 'forward'
        

    def read(self, filename):
        """Reads the data from the file."""
        print(f'Reading {self.instrument} data from {filename}')

        dataNC = Dataset(filename, 'r')

        try:
            # Read latitude and longitude
            lat = dataNC.variables['latitude'][:]
            lon = dataNC.variables['longitude'][:]

            # Read the data
            data = dataNC.variables['radiance'][:]
            
            # close the netCDF file
            dataNC.close()

        except KeyError:
            print(f'Error: {filename} does not contain the required variables.')
    
            # close the netCDF file
            dataNC.close()


