# Standard library imports for operating system interaction and date/time manipulation.
import os
import datetime

# Third-party imports for handling NetCDF files.
from netCDF4 import Dataset # type: ignore

class L1C:
    """
    A class to read and process NASA PACE Level 1C data files.
    This class is designed to handle data from multiple instruments aboard the PACE satellite,
    including HARP2, SPEXone, and OCI.
    """

    def __init__(self, instrument='HARP2', experimental=False):
        """
        Initializes the L1C data reader class.

        Args:
            instrument (str): The name of the instrument to read data from.
                              Defaults to 'HARP2'.
            experimental (bool): Flag to indicate if the data is from an experimental
                                 product. Defaults to False.
        """
        self.experimental = False
        if instrument.lower() == 'harp2':
            self.instrument = 'HARP2'   # Default instrument
            if experimental == True:
                self.experimental = True
        elif instrument.lower() == 'spexone':
            self.instrument = 'SPEXone'
        elif instrument.lower() == 'oci':
            self.instrument = 'OCI'
        self.setInstrument(self.instrument)
        self.product = 'L1C'        # Default product
        self.projectRGB = True      # Default project to RGB
        self.var_units = {}         # Dictionary to store the units for the variables

        # viewing angle to plot
        self.viewing_angle = 'nadir'    # Default viewing angle options are 'nadir', 'aft' and 'forward'

    def checkFile(self, filename):
        """
        Checks if the filename corresponds to the selected instrument.

        Args:
            filename (str): The name of the file to check.
        
        Returns:
            bool: True if the filename contains the instrument name, False otherwise.
        """
        if self.instrument.lower() in filename.lower():
            return True
        else:
            return False
        
    
    def setInstrument(self, instrument):
        """
        Configures the class properties based on the specified instrument.
        This includes setting up the expected names for geolocation and observation
        variables within the NetCDF files.

        Args:
            instrument (str): The name of the instrument.
        """

        match instrument.lower():

            # At the moment the geoNames and obsNames are hard coded
            case 'harp2':
                self.instrument = 'HARP2'
                self.geoNames = ['latitude', 'longitude', 'scattering_angle', 'solar_zenith_angle', 
                                'solar_azimuth_angle', 'sensor_zenith_angle', 'sensor_azimuth_angle',
                                'height', 'rotation_angle']
                
                self.obsNames = ['i', 'q', 'u', 'dolp'] if not self.experimental else ['i', 'q', 'u', 'dolp', 'sensor1', 'sensor2', 'sensor3']
                self.wavelengthsStr = 'intensity_wavelength'
                self.F0Str = 'intensity_f0'
                self.VAStr = 'sensor_view_angle'

            case 'gapmap':
                self.instrument = 'GAPMAP'
                self.geoNames = ['scattering_angle', 'solar_zenith', 
                                'solar_azimuth', 'sensor_zenith', 'sensor_azimuth',
                                'height']
                self.obsNames = [ 'latitude', 'longitude',  'I', 'Q_over_I', 'U_over_I', 'DOLP']
                self.F0Str = 'intensity_f0'
                self.VAStr = 'sensor_view_angle'

            case 'spexone':
                self.instrument = 'SPEXone'
                self.geoNames = ['latitude', 'longitude', 'scattering_angle', 'solar_zenith_angle', 
                                'solar_azimuth_angle', 'sensor_zenith_angle', 'sensor_azimuth_angle',
                                'height', 'rotation_angle']
                
                
                self.obsNames = ['i', 'q', 'u', 'q_over_i', 'u_over_i', 'dolp']
                self.wavelengthsStr = 'intensity_wavelength'
                self.F0Str = 'intensity_f0'
                self.VAStr = 'sensor_view_angle'
                self.PolWav = 'polarization_wavelength'
                self.PolF0 = 'polarization_f0'

            case 'oci':
                self.instrument = 'OCI'
                self.geoNames = ['latitude', 'longitude', 'scattering_angle', 'solar_zenith_angle', 
                                'solar_azimuth_angle', 'sensor_zenith_angle', 'sensor_azimuth_angle',
                                'height']
                
                self.obsNames = ['i']
                self.wavelengthsStr = 'intensity_wavelength'
                self.F0Str = 'intensity_f0'
                self.VAStr = 'sensor_view_angle'

    def dateStr(self, filepath):
        """
        Extracts and returns the date and time from the filename.

        Args:
            filepath (str): The full path to the data file.

        Returns:
            datetime.datetime: A datetime object representing the observation time.
        """
        # Extract the filename from the filepath
        filename_ = os.path.basename(filepath)

        # Extract the date and time string from the filename
        date_time_str = filename_.split('.')[1]

        # Convert the date and time string to a datetime object
        return datetime.datetime.strptime(date_time_str, '%Y%m%dT%H%M%S')
    
    def unit(self, var, units):
            """
            Stores the units for a given variable in the var_units dictionary.
            
            Args:
                var (str): The name of the variable.
                units (str): The units of the variable.
            """
            self.var_units[var] = units  

    def read(self, filename):
        """
        Reads the data from a specified L1C file.

        Args:
            filename (str): The path to the L1C file.

        Returns:
            dict: A dictionary containing the data extracted from the file.
                  Returns None if the file does not match the instrument.
        """
        

        print(f'Reading {self.instrument} data from {filename}')

        correctFile = self.checkFile(filename)
        if not correctFile:
            print(f'Error: {filename} does not contain {self.instrument} data.')
            return

        dataNC = Dataset(filename, 'r')
        data = {}

        try:

            # get the date time from the filename
            data['date_time'] = self.dateStr(filename)

            # Access the 'observation_data' & 'geolocation_data' group
            time_data = dataNC.groups['bin_attributes']
            obs_data = dataNC.groups['observation_data']
            geo_data = dataNC.groups['geolocation_data']
            sensor_data = dataNC.groups['sensor_views_bands']

            # FIXME: This is just a place holder, needs to be updated
            # Read the time from the L1C file
            
            # Define the variable names
            geo_names = self.geoNames

            # Read the variables
            for var in geo_names:
                try:
                    data[var] = geo_data.variables[var][:]
                except KeyError as e:
                    print(f'Error: {filename} does not contain the required variables.')
                    print('Error:', e)

            # Read the data
            obs_names = self.obsNames

            data['_units'] = {}
            for var in obs_names:
                try:
                    data[var] = obs_data.variables[var][:]

                    # read the units for the variable
                    data['_units'][var] = obs_data.variables[var].units
                    self.unit(var, obs_data.variables[var].units)
                except KeyError as e:
                    print(f'Error: {filename} does not contain the required variables.')
                    print('Error:', e)
                    print('Maybe the file is L1C experimental?')

            # read the F0 and unit
            data['F0'] = sensor_data.variables[self.F0Str][:]
            data['_units']['F0'] = sensor_data.variables[self.F0Str].units
            self.unit(var, obs_data.variables[var].units)

            # read the band angles and wavelengths
            data['view_angles'] = sensor_data.variables[self.VAStr][:]
            data['intensity_wavelength'] = sensor_data.variables[self.wavelengthsStr][:]

            # Polarization based F0 might be needed for SPEXone, since their spectral response is polarization dependent
            if self.instrument == 'SPEXone':
                data['polarization_wavelength'] = sensor_data.variables[self.PolWav][:]
                data['polarization_f0'] = sensor_data.variables[self.PolF0][:]

            # close the netCDF file
            dataNC.close()

            return data

        except KeyError as e:
            print(f'Error: {filename} does not contain the required variables.')
            print('Error:', e)

    
            # close the netCDF file
            dataNC.close()

        
class L1B:
    """
    A class for reading NASA PACE Level 1B data files.
    This class is tailored for HARP2 instrument data.
    """

    def __init__(self, experimental=False):
        """
        Initializes the L1B data reader class.

        Args:
            experimental (bool): Flag for experimental data products.
        """
        self.instrument = 'HARP2'   # Default instrument
        self.product = 'L1B'        # Default product
        self.projectRGB = True      # Default project to RGB
        self.experimental = False 
        if experimental == True:
            self.experimental = True
        self.setInstrument(self.instrument)
        self.var_units = {}         # Dictionary to store the units for the variables
        

        # viewing angle to plot
        self.viewing_angle = 'nadir'    # Default viewing angle options are 'nadir', 'aft' and 'forward'
    
    def unit(self, var, units):
            """
            Stores the units for a given variable.
            
            Args:
                var (str): The variable name.
                units (str): The unit string.
            """
            self.var_units[var] = units  
    
    def checkFile(self, filename):
        """
        Checks if the filename is for the correct instrument.

        Args:
            filename (str): The file name to check.
        
        Returns:
            bool: True if the file is for the set instrument.
        """
        if self.instrument.lower() in filename.lower():
            return True
        else:
            return False

    def setInstrument(self, instrument):
        """
        Sets up the instrument-specific variable names.

        Args:
            instrument (str): The name of the instrument.
        """

        match instrument.lower():

            # At the moment the geoNames and obsNames are hard coded
            case 'harp2':
                self.instrument = 'HARP2'
                self.geoNames = ['latitude', 'longitude', 'solar_zenith_angle', 
                                'solar_azimuth_angle', 'sensor_zenith_angle', 'sensor_azimuth_angle',
                                'surface_altitude']
                self.obsNames = ['i', 'q', 'u', 'dolp'] if not self.experimental else ['i', 'q', 'u', 'dolp', 'sensor1', 'sensor2', 'sensor3']
                self.wavelengthsStr = 'intensity_wavelength'
        

    def read(self, filename):
        """
        Reads data from the given L1B file.

        Args:
            filename (str): The path to the L1B file.

        Returns:
            dict: A dictionary containing the read data.
        """
        

        print(f'Reading {self.instrument} {self.product} data from {filename}')

        correctFile = self.checkFile(filename)
        if not correctFile:
            print(f'Error: {filename} does not contain {self.instrument} data.')
            return

        dataNC = Dataset(filename, 'r')
        data = {}

        try:

            # Access the 'observation_data' & 'geolocation_data' group
            obs_data = dataNC.groups['observation_data']
            geo_data = dataNC.groups['geolocation_data']
            sensor_data = dataNC.groups['sensor_views_bands']

            # FIXME: This is just a place holder, needs to be updated
            # Read the time from the L1C file
            
            # Define the variable names
            geo_names = self.geoNames

            # Read the variables
            for var in geo_names:
                data[var] = geo_data.variables[var][:]

            # Read the data
            obs_names = self.obsNames

            data['_units'] = {}
            for var in obs_names:
                try:
                    data[var] = obs_data.variables[var][:]

                    # read the units for the variable
                    data['_units'][var] = obs_data.variables[var].units
                    self.unit(var, obs_data.variables[var].units)
                except KeyError as e:
                    print(f'Error: {filename} does not contain the required variables.')
                    print('Error:', e)
                    print('Maybe the file is L1B experimental?')

            # read the F0 and unit
            # data['F0'] = sensor_data.variables['intensity_F0'][:] # FIXME: This is not available in L1B
            # data['_units']['F0'] = sensor_data.variables['intensity_F0'].units # FIXME: This is not available in L1B
            # self.unit(var, obs_data.variables[var].un1its) # FIXME: This is not available in L1B

            # read the band angles and wavelengths
            data['view_angles'] = sensor_data.variables['sensor_view_angle'][:]
            data['intensity_wavelength'] = sensor_data.variables[self.wavelengthsStr][:]
            data['F0'] = sensor_data.variables['intensity_f0'][:]

            # FIXME: Polarization based F0 might be needed for SPEXone, since their spectral response is polarization dependent


            # close the netCDF file
            dataNC.close()

            return data

        except KeyError as e:
            print(f'Error: {filename} does not contain the required variables.')
            print('Error:', e)

    
            # close the netCDF file
            dataNC.close()
class L1beta:
    """
    A class for reading NASA PACE Level 1 beta data files, specifically for the GAPMAP instrument.
    """

    def __init__(self):
        """Initializes the L1beta data reader class."""
        self.instrument = 'GAPMAP'   # Default instrument
        self.product = 'L1beta'        # Default product
        

    def read(self, filename):
        """
        Reads data from the given L1beta file.
        
        Args:
            filename (str): The path to the L1beta file.
            
        Returns:
            dict: A dictionary containing the read data.
        """
        print(f'Reading {self.instrument} data from {filename}')

        dataNC = Dataset(filename, 'r')

        # define the groups
        img_data = dataNC.groups['IMAGE_DATA']
        nav_data = dataNC.groups['NAVIGATION']

        # define the variables
        img_data_vars = ['image_0', 'image_45', 'image_90', 'image_135', 'Latitude', 'Longitude', 'Surface_Altitude']
        nav_data_vars = ['JD', 'Date', 'Time']

        # define output dict
        data = {}

        try:

            # load the variables from the group img_data
            for key_ in img_data_vars:
                data[key_] = img_data.variables[key_][:]
            
            for key_ in nav_data_vars:
                data[key_] = nav_data.variables[key_][:]

            # close the netCDF file
            dataNC.close()

        except KeyError:
            print(f'Error: {filename} does not contain the required variables.')
    
            # close the netCDF file
            dataNC.close()
    
        # return the data
        return data