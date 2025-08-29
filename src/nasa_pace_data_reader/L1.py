import os
from netCDF4 import Dataset  # type: ignore
import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class L1C:
    """Class for reading
    NASA PACE Level 1C data files.

    """

    def __init__(self, instrument: str = "HARP2", experimental: bool = False) -> None:
        """Initializes the class."""
        self.experimental = False
        if instrument.lower() == "harp2":
            self.instrument = "HARP2"  # Default instrument
            if experimental:
                self.experimental = True
        elif instrument.lower() == "spexone":
            self.instrument = "SPEXone"
        elif instrument.lower() == "oci":
            self.instrument = "OCI"
        self.setInstrument(self.instrument)
        self.product = "L1C"  # Default product
        self.projectRGB = True  # Default project to RGB
        self.var_units = {}  # Dictionary to store the units for the variables

        # viewing angle to plot
        self.viewing_angle = (
            "nadir"  # Default viewing angle options are 'nadir', 'aft' and 'forward'
        )

    # function to check if the file has the name of instrument
    def checkFile(self, filename: str) -> bool:
        """Checks if the file has the name of the instrument.

        Args:
            filename (str): The name of the file.

        Returns:
            bool: True if the file has the name of the instrument, False otherwise.

        """
        if self.instrument.lower() in filename.lower():
            return True
        else:
            return False

    def setInstrument(self, instrument: str) -> None:
        """Sets the instrument.

        Args:
            instrument (str): The name of the instrument.

        Returns:
            None
        """

        match instrument.lower():
            # At the moment the geoNames and obsNames are hard coded
            case "harp2":
                self.instrument = "HARP2"
                self.geoNames = [
                    "latitude",
                    "longitude",
                    "scattering_angle",
                    "solar_zenith_angle",
                    "solar_azimuth_angle",
                    "sensor_zenith_angle",
                    "sensor_azimuth_angle",
                    "height",
                    "rotation_angle",
                ]

                self.obsNames = (
                    ["i", "q", "u", "dolp"]
                    if not self.experimental
                    else ["i", "q", "u", "dolp", "sensor1", "sensor2", "sensor3"]
                )
                self.wavelengthsStr = "intensity_wavelength"
                self.F0Str = "intensity_f0"
                self.VAStr = "sensor_view_angle"

            case "gapmap":
                self.instrument = "GAPMAP"
                self.geoNames = [
                    "scattering_angle",
                    "solar_zenith",
                    "solar_azimuth",
                    "sensor_zenith",
                    "sensor_azimuth",
                    "height",
                ]
                self.obsNames = [
                    "latitude",
                    "longitude",
                    "I",
                    "Q_over_I",
                    "U_over_I",
                    "DOLP",
                ]
                self.F0Str = "intensity_f0"
                self.VAStr = "sensor_view_angle"

            case "spexone":
                self.instrument = "SPEXone"
                self.geoNames = [
                    "latitude",
                    "longitude",
                    "scattering_angle",
                    "solar_zenith_angle",
                    "solar_azimuth_angle",
                    "sensor_zenith_angle",
                    "sensor_azimuth_angle",
                    "height",
                    "rotation_angle",
                ]

                self.obsNames = ["i", "q", "u", "q_over_i", "u_over_i", "dolp"]
                self.wavelengthsStr = "intensity_wavelength"
                self.F0Str = "intensity_f0"
                self.VAStr = "sensor_view_angle"
                self.PolWav = "polarization_wavelength"
                self.PolF0 = "polarization_f0"

            case "oci":
                self.instrument = "OCI"
                self.geoNames = [
                    "latitude",
                    "longitude",
                    "scattering_angle",
                    "solar_zenith_angle",
                    "solar_azimuth_angle",
                    "sensor_zenith_angle",
                    "sensor_azimuth_angle",
                    "height",
                ]

                self.obsNames = ["i"]
                self.wavelengthsStr = "intensity_wavelength"
                self.F0Str = "intensity_f0"
                self.VAStr = "sensor_view_angle"

    def dateStr(self, filepath: str) -> datetime.datetime:
        """Returns the date string."""
        # Extract the filename from the filepath
        filename_ = os.path.basename(filepath)

        # Extract the date and time string from the filename
        date_time_str = filename_.split(".")[1]

        # Convert the date and time string to a datetime object
        return datetime.datetime.strptime(date_time_str, "%Y%m%dT%H%M%S")

    def unit(self, var: str, units: str) -> None:
        """Returns the units for the variable."""
        self.var_units[var] = units

    def read(self, filename: str) -> Dict:
        """Reads the data from the file.

        Args:
            filename (str): The name of the file to read.

        Returns:
            dict: A dictionary containing the data.

        """

        logger.info(f"Reading {self.instrument} data from {filename}")

        correctFile = self.checkFile(filename)
        if not correctFile:
            message = f"{filename} does not contain {self.instrument} data."
            logger.error(message)
            raise ValueError(message)

        try:
            dataNC = Dataset(filename, "r")
            data = {}

            # get the date time from the filename
            data["date_time"] = self.dateStr(filename)

            # Access the 'observation_data' & 'geolocation_data' group

            obs_data = dataNC.groups["observation_data"]
            geo_data = dataNC.groups["geolocation_data"]
            sensor_data = dataNC.groups["sensor_views_bands"]

            # FIXME: This is just a place holder, needs to be updated
            # Read the time from the L1C file

            # Define the variable names
            geo_names = self.geoNames

            # Read the variables
            for var in geo_names:
                try:
                    data[var] = geo_data.variables[var][:]
                except KeyError as e:
                    message = (
                        f"{filename} does not contain the required variable: {var}"
                    )
                    logger.error(message)
                    raise ValueError(message) from e

            # Read the data
            obs_names = self.obsNames

            data["_units"] = {}
            for var in obs_names:
                try:
                    data[var] = obs_data.variables[var][:]

                    # read the units for the variable
                    data["_units"][var] = obs_data.variables[var].units
                    self.unit(var, obs_data.variables[var].units)
                except KeyError as e:
                    message = f"{filename} does not contain the required variable: {var}. Maybe the file is L1C experimental?"
                    logger.error(message)
                    raise ValueError(message) from e

            # read the F0 and unit
            try:
                data["F0"] = sensor_data.variables[self.F0Str][:]
                data["_units"]["F0"] = sensor_data.variables[self.F0Str].units
                self.unit("F0", sensor_data.variables[self.F0Str].units)
            except KeyError as e:
                message = (
                    f"{filename} does not contain the required variable: {self.F0Str}"
                )
                logger.error(message)
                raise ValueError(message) from e

            # read the band angles and wavelengths
            try:
                data["view_angles"] = sensor_data.variables[self.VAStr][:]
                data["intensity_wavelength"] = sensor_data.variables[
                    self.wavelengthsStr
                ][:]
            except KeyError as e:
                message = f"{filename} does not contain the required variable: {self.VAStr} or {self.wavelengthsStr}"
                logger.error(message)
                raise ValueError(message) from e

            # Polarization based F0 might be needed for SPEXone, since their spectral response is polarization dependent
            if self.instrument == "SPEXone":
                try:
                    data["polarization_wavelength"] = sensor_data.variables[
                        self.PolWav
                    ][:]
                    data["polarization_f0"] = sensor_data.variables[self.PolF0][:]
                except KeyError as e:
                    message = f"{filename} does not contain the required polarization variables for SPEXone"
                    logger.error(message)
                    raise ValueError(message) from e

            # close the netCDF file
            dataNC.close()

            return data

        except Exception as e:
            logger.error(f"Unexpected error reading {filename}: {str(e)}")
            if "dataNC" in locals():
                dataNC.close()
            raise


class L1B:
    """Class for reading
    NASA PACE Level 1B data files.

    """

    def __init__(self, experimental: bool = False) -> None:
        """Initializes the class."""
        self.instrument = "HARP2"  # Default instrument
        self.product = "L1B"  # Default product
        self.projectRGB = True  # Default project to RGB
        self.experimental = False
        if experimental:
            self.experimental = True
        self.setInstrument(self.instrument)
        self.var_units = {}  # Dictionary to store the units for the variables

        # viewing angle to plot
        self.viewing_angle = (
            "nadir"  # Default viewing angle options are 'nadir', 'aft' and 'forward'
        )

    def unit(self, var: str, units: str) -> None:
        """Returns the units for the variable."""
        self.var_units[var] = units

    # function to check if the file has the name of instrument
    def checkFile(self, filename: str) -> bool:
        """Checks if the file has the name of the instrument.

        Args:
            filename (str): The name of the file.

        Returns:
            bool: True if the file has the name of the instrument, False otherwise.

        """
        if self.instrument.lower() in filename.lower():
            return True
        else:
            return False

    def setInstrument(self, instrument: str) -> None:
        """Sets the instrument.

        Args:
            instrument (str): The name of the instrument.

        Returns:
            None
        """

        match instrument.lower():
            # At the moment the geoNames and obsNames are hard coded
            case "harp2":
                self.instrument = "HARP2"
                self.geoNames = [
                    "latitude",
                    "longitude",
                    "solar_zenith_angle",
                    "solar_azimuth_angle",
                    "sensor_zenith_angle",
                    "sensor_azimuth_angle",
                    "surface_altitude",
                ]
                self.obsNames = (
                    ["i", "q", "u", "dolp"]
                    if not self.experimental
                    else ["i", "q", "u", "dolp", "sensor1", "sensor2", "sensor3"]
                )
                self.wavelengthsStr = "intensity_wavelength"

    def read(self, filename: str) -> Dict:
        """Reads the data from the file.

        Args:
            filename (str): The name of the file to read.

        Returns:
            dict: A dictionary containing the data.

        """

        logger.info(f"Reading {self.instrument} {self.product} data from {filename}")

        correctFile = self.checkFile(filename)
        if not correctFile:
            message = f"{filename} does not contain {self.instrument} data."
            logger.error(message)
            raise ValueError(message)

        try:
            dataNC = Dataset(filename, "r")
            data = {}

            # Access the 'observation_data' & 'geolocation_data' group
            obs_data = dataNC.groups["observation_data"]
            geo_data = dataNC.groups["geolocation_data"]
            sensor_data = dataNC.groups["sensor_views_bands"]

            # FIXME: This is just a place holder, needs to be updated
            # Read the time from the L1C file

            # Define the variable names
            geo_names = self.geoNames

            # Read the variables
            for var in geo_names:
                try:
                    data[var] = geo_data.variables[var][:]
                except KeyError as e:
                    message = (
                        f"{filename} does not contain the required variable: {var}"
                    )
                    logger.error(message)
                    raise ValueError(message) from e

            # Read the data
            obs_names = self.obsNames

            data["_units"] = {}
            for var in obs_names:
                try:
                    data[var] = obs_data.variables[var][:]

                    # read the units for the variable
                    data["_units"][var] = obs_data.variables[var].units
                    self.unit(var, obs_data.variables[var].units)
                except KeyError as e:
                    message = f"{filename} does not contain the required variable: {var}. Maybe the file is L1B experimental?"
                    logger.error(message)
                    raise ValueError(message) from e

            # read the band angles and wavelengths
            try:
                data["view_angles"] = sensor_data.variables["sensor_view_angle"][:]
                data["intensity_wavelength"] = sensor_data.variables[
                    self.wavelengthsStr
                ][:]
                data["F0"] = sensor_data.variables["intensity_f0"][:]
            except KeyError as e:
                message = f"{filename} does not contain the required sensor variables"
                logger.error(message)
                raise ValueError(message) from e

            # FIXME: Polarization based F0 might be needed for SPEXone, since their spectral response is polarization dependent

            # close the netCDF file
            dataNC.close()

            return data

        except Exception as e:
            logger.error(f"Unexpected error reading {filename}: {str(e)}")
            if "dataNC" in locals():
                dataNC.close()
            raise


class L1beta:
    """Class for reading
    NASA PACE Level 1beta data files.

    """

    def __init__(self) -> None:
        """Initializes the class."""
        self.instrument = "GAPMAP"  # Default instrument
        self.product = "L1beta"  # Default product

    def read(self, filename: str) -> Dict:
        """Reads the data from the file."""
        logger.info(f"Reading {self.instrument} data from {filename}")

        try:
            dataNC = Dataset(filename, "r")

            # define the groups
            img_data = dataNC.groups["IMAGE_DATA"]
            nav_data = dataNC.groups["NAVIGATION"]

            # define the variables
            img_data_vars = [
                "image_0",
                "image_45",
                "image_90",
                "image_135",
                "Latitude",
                "Longitude",
                "Surface_Altitude",
            ]
            nav_data_vars = ["JD", "Date", "Time"]

            # define output dict
            data = {}

            # load the variables from the group img_data
            for key_ in img_data_vars:
                try:
                    data[key_] = img_data.variables[key_][:]
                except KeyError as e:
                    message = (
                        f"{filename} does not contain the required variable: {key_}"
                    )
                    logger.error(message)
                    raise ValueError(message) from e

            for key_ in nav_data_vars:
                try:
                    data[key_] = nav_data.variables[key_][:]
                except KeyError as e:
                    message = (
                        f"{filename} does not contain the required variable: {key_}"
                    )
                    logger.error(message)
                    raise ValueError(message) from e

            # close the netCDF file
            dataNC.close()

            return data

        except Exception as e:
            logger.error(f"Unexpected error reading {filename}: {str(e)}")
            if "dataNC" in locals():
                dataNC.close()
            raise
