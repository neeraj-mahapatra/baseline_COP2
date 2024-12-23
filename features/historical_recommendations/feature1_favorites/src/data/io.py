# src/data/io.py

"""
IO module handling data input/output operations.
"""

import pandas as pd

class DataIO:
    """
    A class to handle reading and saving CSV data.
    """

    def __init__(self):
        """
        Initializes the DataIO class.
        """
        pass

    def read_data_from_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Reads CSV data from the given path.

        Parameters
        ----------
        csv_path : str
            Path to the CSV file.

        Returns
        -------
        pd.DataFrame
            DataFrame loaded with CSV content.
        """
        return pd.read_csv(csv_path)

    def save_bundle_to_csv(self, bundle: list, output_path: str) -> None:
        """
        Saves a list of dictionaries (bundle) to a CSV.

        Parameters
        ----------
        bundle : list
            List of product dictionaries to be saved.
        output_path : str
            Path to the output CSV file.
        """
        pd.DataFrame(bundle).to_csv(output_path, index=False)
