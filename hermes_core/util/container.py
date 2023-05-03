"""
Data Container class for Heliophysics Science Data.
"""

import os
from typing import OrderedDict
from astropy.timeseries import TimeSeries
from astropy.table import Table
from astropy import units as u
from hermes_core.util.validation import CDFValidator, NetCDFValidator, FITSValidator
from hermes_core.util.io import ScienceDataIOHandler, CDFHandler, NetCDFHandler, FITSHandler


def read(filename):
    # Determine the file type
    file_extension = os.path.splitext(filename)[1]

    # Create the appropriate handler object based on file type
    if file_extension == ".cdf":
        handler = CDFHandler()
    elif file_extension == ".nc":
        handler = NetCDFHandler()
    elif file_extension == ".fits":
        handler = FITSHandler()
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

    # Load data using the handler and return a ScienceData object
    return ScienceData.load(filename, handler=handler)


def validate(filename):
    # Determine the file type
    file_extension = os.path.splitext(filename)[1]

    # Create the appropriate validator object based on file type
    if file_extension == ".cdf":
        validator = CDFValidator()
    elif file_extension == ".nc":
        validator = NetCDFValidator()
    elif file_extension == ".fits":
        validator = FITSValidator()
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

    # Call the validate method of the validator object
    return validator.validate(filename)


class ScienceData:
    """
    A class for storing and manipulating science data.

    Parameters:
        data (TimeSeries): The science data stored as a TimeSeries object.
        handler (ScienceDataIOHandler, optional): The handler for input/output operations. Defaults to None.

    Attributes:
        meta (dict): Metadata associated with the science data.
        handler (ScienceDataIOHandler): The handler for input/output operations.

    """

    def __init__(self, data, handler=None):
        """
        Initialize a ScienceData object.

        Parameters:
            data (TimeSeries): The science data stored as a TimeSeries object.
            handler (ScienceDataIOHandler, optional): The handler for input/output operations. Defaults to None.

        Raises:
            ValueError: If the number of columns is less than 2, the required 'time' column is missing,
                        or any column, excluding 'time', is not an astropy.Quantity object with units.

        """
        if isinstance(data, TimeSeries):
            if len(data.columns) < 2:
                raise ValueError("Science data must have at least 2 columns")
            if "time" not in data.columns:
                raise ValueError("Science data must have a 'time' column")
            self.data = TimeSeries(data, copy=True)
        elif isinstance(data, Table):
            if len(data.columns) < 2:
                raise ValueError("Science data must have at least 2 columns")
            if "time" not in data.columns:
                raise ValueError("Science data must have a 'time' column")
            self.data = TimeSeries(data, time_column="time", copy=True)
        else:
            raise ValueError("Invalid data type. Must be a TimeSeries or Table object.")

        for colname in self.data.columns:
            if colname != "time" and not isinstance(self.data[colname], u.Quantity):
                raise ValueError(f"Column '{colname}' must be an astropy.Quantity object")

        # Add any Metadata from the original TimeSeries
        self.data.time.meta = OrderedDict()
        if hasattr(data["time"], "meta"):
            self.data.time.meta.update(data["time"].meta)
        for col in self.data.columns:
            if col != "time":
                self.data[col].meta = OrderedDict()
                if hasattr(data[col], "meta"):
                    self.data[col].meta.update(data[col].meta)

        self.handler = handler

    @property
    def meta(self):
        """
        Metadata associated with the science data.

        Returns:
            dict: The metadata associated with the science data.

        """
        return self.data.meta

    @meta.setter
    def meta(self, value):
        """
        Set the metadata associated with the science data.

        Parameters:
            value (dict): The metadata to set.

        """
        self.data.meta = value

    @property
    def handler(self):
        """
        The handler for input/output operations.

        Returns:
            ScienceDataIOHandler: The handler for input/output operations.

        """
        return self._handler

    @handler.setter
    def handler(self, value):
        """
        Set the handler for input/output operations.

        Parameters:
            value (ScienceDataIOHandler): The handler to set.

        Raises:
            ValueError: If the handler is not an instance of ScienceDataIOHandler.

        """
        if value is not None and not isinstance(value, ScienceDataIOHandler):
            raise ValueError("Handler must be an instance of ScienceDataIOHandler")
        self._handler = value

    @property
    def units(self):
        """
        (OrderedDict), returns the units of the columns of data
        """
        units = {}
        for name in self.data.columns:
            var_data = self.data[name]
            # Get the Unit
            if hasattr(var_data, "unit"):
                unit = var_data.unit
            elif "UNITS" in var_data.meta and var_data.meta["UNITS"]:
                unit = var_data.meta["UNITS"]
            else:
                unit = None
            units[name] = unit
        return OrderedDict(units)

    @property
    def columns(self):
        """
        (OrderedDict), returns columns from data.columns
        """
        return self.data.columns

    @property
    def time(self):
        """
        returns the time array from data.time
        """
        if "time" in self.data.columns:
            return self.data.time
        else:
            return None

    @property
    def shape(self):
        """
        The shape of the data, a tuple (nrows, ncols)
        """
        if "time" in self.data.columns:
            nrows = self.data.time.shape[0]
        else:
            nrows = 0
        ncols = len(self.data.columns)
        return (nrows, ncols)

    def __repr__(self):
        """
        Returns a representation of the CDFWriter class.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns a string representation of the CDFWriter class.
        """
        str_repr = f"ScienceData() Object:\n"
        # Global Attributes/Metedata
        str_repr += f"Global Attrs:\n"
        for attr_name, attr_value in self.data.meta.items():
            str_repr += f"\t{attr_name}: {attr_value}\n"
        # Variable Data
        str_repr += f"Variable Data:\n{self.data}\n"
        # Variable Attributes
        str_repr += f"Variable Attributes:\n"
        for col_name in self.data.columns:
            str_repr += f"\tVar: {col_name}\n"
            # for attr_name, attr_value in self.data[col_name].meta.items():
            #     str_repr += f"\t\t{attr_name}: {attr_value}\n"
        return str_repr

    def __len__(self):
        """
        Function to get the number of variable data members in the CDFWriter class.
        """
        return len(self.data.keys())

    def __getitem__(self, name):
        """
        Function to get a data variable contained in the CDFWriter class.
        """
        if name not in self.data.colnames:
            raise KeyError(f"CDFWriter does not contain data variable {name}")
        # Get the Data and Attrs for the named variable
        var_data = self.data[name]
        return var_data

    def __setitem__(self, name, data):
        """
        Function to set a data variable conained in the CDFWriter class.
        """
        # Set the Data for the named variable
        self._add_variable(var_name=name, var_data=data, var_attrs={})

    def __contains__(self, name):
        """
        Function to see whether a data variable is in the CDFWriter class.
        """
        return name in self.data.columns

    def __iter__(self):
        """
        Function to iterate over data variables and attributes in the CDFWriter class.
        """
        for name in self.data.columns:
            var_data = self.data[name]
            yield (name, var_data)

    def _add_variable(self, var_name: str, var_data: u.Quantity, var_attrs: dict):
        """
        Function to add variable data to the ScienceData class. Variable data here is assumed
        to be array-like or matrix-like to be stored in the ScienceData. Additionally, varaible
        attributes can be added though a native python `dict` of `(key, value)` pairs that
        are added to the ScienceData variable.

        Parameters
        ----------
        var_name: `str`
            Name of the variable to add to the CDFWriter.

        var_data: `Quantity`
                the data added to the internal `TimeSeries` with the `var_name` as the
                column name and `var_attrs` as the column metadata. Data contained in the
                `Quantity.info` member is combined with the `var_attrs` to add additional
                attributes or update and override existing attributes.

        var_attrs: `dict`
            A collection of `(key,value)` pairs to add as attributes of the CDF varaible.

        """
        # Verify that all columns are `Quantity`
        if (not isinstance(var_data, u.Quantity)) or (not var_data.unit):
            raise TypeError(
                f"Column {var_name} must be type `astropy.units.Quantity` and have `unit` assigned."
            )

        self.data[var_name] = var_data
        # Add any Metadata from the original TimeSeries
        self.data[var_name].meta = OrderedDict()
        if hasattr(var_data, "meta"):
            self.data[var_name].meta.update(var_attrs)

    def save(self, output_path):
        """
        Save the science data to a file using the specified handler.

        Parameters:
            output_path (str): A string path to the directory where file is to be saved.

        Raises:
            ValueError: If no handler is specified for saving data.

        """
        if self.handler is None:
            raise ValueError("No handler specified for saving data")
        self.handler.save_data(data=self, file_path=output_path)

    @classmethod
    def load(cls, filename, handler):
        """
        Load science data from a file using the specified handler.

        Parameters:
            filename (str): The name of the file to load the data from.
            handler (ScienceDataIOHandler): The handler for input/output operations.

        Returns:
            ScienceData: A ScienceData object containing the loaded data.

        Raises:
            ValueError: If the handler is not an instance of ScienceDataIOHandler.

        """
        if not isinstance(handler, ScienceDataIOHandler):
            raise ValueError("Handler must be an instance of ScienceDataIOHandler")
        data = handler.load_data(filename)
        return cls(data, handler)
