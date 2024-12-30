# src/data/transformations.py

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import minmax_scale
from ..utils.variables import PROCESSED_CSV

class Transformer:
    """
    A class for processing and transforming CSV data.
    """

    def __init__(self, 
                 previous_data_rename_map,
                 future_data_rename_map,
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
                 recncy_column_name="recency",
                 campaign_column_name=None):
        """
        Initializes the Transformer with configuration parameters.
        """
        self.previous_data_rename_map = previous_data_rename_map
        self.future_data_rename_map = future_data_rename_map
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
        self.campaign_column_name = campaign_column_name

    def process_csv(self, df: pd.DataFrame, df_future: pd.DataFrame) -> pd.DataFrame:
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
        df.rename(columns=self.previous_data_rename_map, inplace=True)
        df_future.rename(columns=self.future_data_rename_map, inplace=True)
        
        # Drop a column
        if self.column_to_drop and self.column_to_drop in df.columns and self.column_to_drop in df_future.columns:
             df.drop(self.column_to_drop, axis=1, inplace=True)
             df_future.drop(self.column_to_drop, axis=1, inplace=True)
            

        # Filter a column
        if self.column_to_filter and self.column_to_filter in df.columns and self.column_to_filter in df_future.columns:
            # Get all ID_OFERTAs that have CODCUC as 'XXXXXXXXX'
            offer_ids_to_filter_in_df = df[df[self.column_to_filter] == self.column_to_filter_value][self.group_by_offer_column].unique()
            offer_ids_to_filter_in_df_future = df[df[self.column_to_filter] == self.column_to_filter_value][self.group_by_offer_column].unique()

            # Filter out all rows with these ID_OFERTAs
            df = df[~df[self.group_by_offer_column].isin(offer_ids_to_filter_in_df)]
            df_future = df_future[~df_future[self.group_by_offer_column].isin(offer_ids_to_filter_in_df_future)]

    
        # Convert transaction date to datetime if provided
        if self.transaction_date_column and self.transaction_date_column in df.columns and self.reference_date != None:
            df[self.transaction_date_column] = pd.to_datetime(df[self.transaction_date_column], errors="coerce")
            self.reference_date = pd.to_datetime(self.reference_date)

         # Validate composite_key and group_by_columns
        if not all(col in df.columns for col in self.composite_key_columns_list) and not all(col in df.columns for col in self.group_by_columns_list):
            print(f"Warning: One or more columns in {self.group_by_columns_list} not found in the DataFrame.")
            return df
        
        dfs = {campaign_id: df_subset for campaign_id, df_subset in df.groupby(self.campaign_column_name)}
        df_futures = {campaign_id: df_subset for campaign_id, df_subset in df_future.groupby(self.campaign_column_name)}

        all_dfs = []
        for campaign_id, sub_df in dfs.items():
            # Step 1: Create Composite Key column
            sub_df[self.composite_key_column_name] = sub_df[self.composite_key_columns_list].astype(str).agg(self.composite_key_seperator.join, axis=1)
            
            # Step 2: Calculate recency
            if self.reference_date == None:
                self.reference_date = datetime.now()

            sub_df[self.recncy_column_name] = 1 / ((self.reference_date - sub_df[self.transaction_date_column]).dt.days + 1)

            # Step 3: aggregation based on offer_id
            sub_df = sub_df.groupby(self.group_by_offer_column)[[self.composite_key_column_name, self.explode_by_column, self.recncy_column_name]].agg(
                {
                    self.explode_by_column: lambda x: x.dropna().tolist(),
                    self.composite_key_column_name: lambda x: '|'.join(x),
                    self.recncy_column_name: 'mean'  # Aggregating recency by mean
                }
            ).reset_index()

            # Step 4: explode a column
            if self.explode_by_column and self.explode_by_column in sub_df.columns:
                sub_df = sub_df.explode(self.explode_by_column)

            group_by_list = [item for item in self.group_by_columns_list if item != self.group_by_offer_column]

            # Step 5: Group by CODEBELISTA and Composite_key, aggregating ID_OFERTA into a list and calculating count
            sub_df = sub_df.groupby(group_by_list).agg({
                self.group_by_offer_column: lambda x: x.tolist(),  # convert ID_OFERTA to list,
                self.recncy_column_name: 'mean'
            }).reset_index()

            # Step 6: Add frequency column
            sub_df[self.frequency_column_name] = sub_df.groupby(group_by_list).size().values

            # Normalize frequency
            if self.frequency_column_name in sub_df.columns:
                sub_df[self.frequency_column_name + "_normalized"] = minmax_scale(sub_df[self.frequency_column_name])
            
            # Normalize recency
            if self.recncy_column_name in sub_df.columns:
                sub_df[self.recncy_column_name + "_normalized"] = minmax_scale(sub_df[self.recncy_column_name])

            if self.campaign_column_name not in sub_df.columns:
                sub_df[self.campaign_column_name] = campaign_id

            # Step 12: Append the result to the list
            all_dfs.append(sub_df)
            
        final_df = pd.concat(all_dfs, ignore_index=True)

        # Filtering duplicate offers from future planned campaigns
        all_future_dfs = []
        for campaign_id, sub_df in df_futures.items():
            sub_df[self.composite_key_column_name] = sub_df[self.composite_key_columns_list].astype(str).agg(self.composite_key_seperator.join, axis=1)
            sub_df = sub_df.groupby(self.group_by_offer_column)[[self.composite_key_column_name]].agg(
                {
                    self.composite_key_column_name: lambda x: '|'.join(x)
                }
            ).reset_index()

            if self.campaign_column_name not in sub_df.columns:
                sub_df[self.campaign_column_name] = campaign_id

            all_future_dfs.append(sub_df)

        final_future_df = pd.concat(all_future_dfs, ignore_index=True)
        final_future_df.to_csv("final_future_df.csv",index=False)

        duplicate_offers_count = final_future_df[self.composite_key_column_name].isin(final_df[self.composite_key_column_name]).sum()
        print(f"Number of matching Composite_key values: {duplicate_offers_count}")

        # Get the rows from final_df where Composite_key matches in final_future_df
        matching_rows_final_df = final_df[final_df[self.composite_key_column_name].isin(final_future_df[self.composite_key_column_name])]

        print("\nMatching rows in final_df:")
        print(matching_rows_final_df)
        matching_rows_final_df.to_csv("matching_rows_final_df.csv", index=False)

        final_df.to_csv(PROCESSED_CSV, index=False)

        return final_df
