# src/data/transformations.py

"""
Module providing data transformations and preprocessing.
"""

import pandas as pd
import numpy as np
from datetime import datetime

class Transformer:
    """
    A class for processing and transforming CSV data.
    """

    def __init__(self, 
                 column_rename_map, 
                 column_to_replace=None, 
                 replacement_value=None, 
                 group_by_columns=None, 
                 frequency_column_name="purchase_frequency", 
                 transaction_date_column=None, 
                 recncy_column_name="recency"):
        """
        Initializes the Transformer with configuration parameters.
        """
        self.column_rename_map = column_rename_map
        self.column_to_replace = column_to_replace
        self.replacement_value = replacement_value
        self.group_by_columns = group_by_columns or []
        self.frequency_column_name = frequency_column_name
        self.transaction_date_column = transaction_date_column
        self.recncy_column_name = recncy_column_name

    def process_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes the DataFrame:
        1. Renames columns
        2. Replaces null values
        3. Aggregates daily metrics
        4. Calculates frequency, recency, and normalizes them

        Parameters
        ----------
        df : pd.DataFrame
            The input DataFrame.

        Returns
        -------
        pd.DataFrame
            Processed and transformed DataFrame.
        """
        # Rename columns
        df.rename(columns=self.column_rename_map, inplace=True)
        
        # Replace null or specified values in a column
        if self.column_to_replace and self.column_to_replace in df.columns:
            df[self.column_to_replace].fillna(self.replacement_value, inplace=True)  

        # Convert transaction date to datetime if provided
        if self.transaction_date_column and self.transaction_date_column in df.columns:
            df[self.transaction_date_column] = pd.to_datetime(df[self.transaction_date_column], errors="coerce")

        # Validate group_by_columns
        if not all(col in df.columns for col in self.group_by_columns):
            print(f"Warning: One or more columns in {self.group_by_columns} not found in the DataFrame.")
            return df

        # Step 1: Daily aggregation
        daily_agg = df.groupby(self.group_by_columns, as_index=False).agg({
            "product_id": "count",
            "price": "sum"
        })
        daily_agg.rename(columns={
            "product_id": self.frequency_column_name,
            "price": "daily_total_spent"
        }, inplace=True)

        # Step 2: IQR-based calculations
        Q1 = np.percentile(daily_agg["daily_total_spent"], 25)
        Q3 = np.percentile(daily_agg["daily_total_spent"], 75)
        IQR = Q3 - Q1

        # Just as an example: store the upper bound in case needed
        upper_bound = Q3 + 1.5 * IQR
        daily_agg["average_purchasing_power"] = Q3

        # Step 3: Merge daily aggregates back
        df = pd.merge(df, daily_agg, on=self.group_by_columns, how="left")

        # Calculate recency
        if self.transaction_date_column in df.columns:
            current_date = datetime.now()
            df[self.recncy_column_name] = (current_date - df[self.transaction_date_column]).dt.days

        # Normalize frequency
        if self.frequency_column_name in df.columns:
            freq_min = df[self.frequency_column_name].min()
            freq_max = df[self.frequency_column_name].max()
            if freq_min != freq_max:
                df[self.frequency_column_name + "_normalized"] = (
                    df[self.frequency_column_name] - freq_min
                ) / (freq_max - freq_min)
            else:
                df[self.frequency_column_name + "_normalized"] = 0.5

        # Normalize recency
        if self.recncy_column_name in df.columns:
            rec_min = df[self.recncy_column_name].min()
            rec_max = df[self.recncy_column_name].max()
            if rec_min != rec_max:
                df[self.recncy_column_name + "_normalized"] = (
                    df[self.recncy_column_name] - rec_min
                ) / (rec_max - rec_min)
            else:
                df[self.recncy_column_name + "_normalized"] = 0.5

        # Consultant-level metrics (optional)
        if "consultant_id" in df.columns and "price" in df.columns:
            df["total_spent"] = df.groupby("consultant_id")["price"].transform("sum")
            df["purchase_count"] = df.groupby("consultant_id")["product_id"].transform("count")
            df["unique_products"] = df.groupby("consultant_id")["product_id"].transform("nunique")

        return df
