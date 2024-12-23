# src/data/transformations.py

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import minmax_scale

class Transformer:
    """
    A class for processing and transforming CSV data.
    """

    def __init__(self, 
                 column_rename_map,
                 composite_key_columns_list,
                 composite_key_seperator = '|', 
                 column_to_drop = None,
                 column_to_filter=None, 
                 column_to_filter_value=None,
                 group_by_columns_list=None,
                 group_by_offer_column = "offer_id",
                 explode_by_column = None,
                 frequency_column_name="frequency",
                 composite_key_column_name = "Composite_key", 
                 transaction_date_column=None,
                 reference_date = None,
                 recncy_column_name="recency"):
        """
        Initializes the Transformer with configuration parameters.
        """
        self.column_rename_map = column_rename_map
        self.composite_key_columns_list = composite_key_columns_list
        self.composite_key_seperator = composite_key_seperator
        self.column_to_drop = column_to_drop
        self.column_to_filter = column_to_filter
        self.column_to_filter_value = column_to_filter_value
        self.group_by_columns_list = group_by_columns_list or []
        self.group_by_offer_column = group_by_offer_column
        self.explode_by_column = explode_by_column
        self.frequency_column_name = frequency_column_name
        self.composite_key_column_name = composite_key_column_name
        self.transaction_date_column = transaction_date_column
        self.reference_date = reference_date
        self.recncy_column_name = recncy_column_name

    def process_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes the DataFrame:
        1. Renames columns
        2. Drops column
        3. Filters column
        4. Aggregates metrics
        5. Calculates frequency, recency, and normalizes them

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
        
        # Drop a column
        if self.column_to_drop and self.column_to_drop in df.columns:
             df.drop(self.column_to_drop, axis=1)

        # Filter a column
        if self.column_to_filter and self.column_to_filter in df.columns:
            df[df[self.column_to_filter] != self.column_to_filter_value]
    
        # Convert transaction date to datetime if provided
        if self.transaction_date_column and self.transaction_date_column in df.columns and self.reference_date != None:
            df[self.transaction_date_column] = pd.to_datetime(df[self.transaction_date_column], errors="coerce")
            reference_date = pd.to_datetime(reference_date)

         # Validate composite_key and group_by_columns
        if not all(col in df.columns for col in self.composite_key_columns) and not all(col in df.columns for col in self.group_by_columns):
            print(f"Warning: One or more columns in {self.group_by_columns} not found in the DataFrame.")
            return df
            
        # Step 1: Create Composite Key column
        df[self.composite_key_column_name] = df[self.composite_key_columns].astype(str).agg(self.composite_key_seperator.join, axis=1)

        # Step 2: Calculate recency
        if self.transaction_date_column in df.columns:
            current_date = datetime.now()
            df[self.recncy_column_name] = (current_date - df[self.transaction_date_column]).dt.days

        if self.reference_date == None:
            self.reference_date = datetime.now()

        df[self.recncy_column_name] = (1 / (self.reference_date - df[self.transaction_date_column]) + 1).dt.days

        # Step 3: aggregation based on offer_id
        df.groupby(self.group_by_offer_column)[[self.composite_key_column_name, self.explode_by_column, self.recncy_column_name]].agg(
            {
                self.explode_by_column: lambda x: x.dropna().tolist(),
                self.composite_key_column_name: lambda x: '|'.join(x),
                self.recncy_column_name: 'mean'  # Aggregating recency by mean
            }
        ).reset_index()

        # Step 4: explode a column
        if self.explode_by_column and self.explode_by_column in df.columns:
            df.explode(self.explode_by_column)

        # Step 5: Group by CODEBELISTA and Composite_key, aggregating ID_OFERTA into a list and calculating count
        df.groupby([item for item in self.group_by_columns_list if item != self.group_by_offer_column]).agg({
            self.group_by_offer_column: lambda x: x.tolist(),  # convert ID_OFERTA to list,
            self.recncy_column_name:'mean'
        }).reset_index()

        # Step 6: Add frequency column
        df[self.frequency_column_name] = df.groupby([item for item in self.group_by_columns_list if item != self.group_by_offer_column]).size().values

        # Normalize frequency
        if self.frequency_column_name in df.columns:
            df[self.frequency_column_name + "_normalized"] = minmax_scale(df[self.frequency_column_name])
        
        # Normalize recency
        if self.recncy_column_name in df.columns:
             df[self.recncy_column_name + "_normalized"] = minmax_scale(df[self.recncy_column_name])

        return df
