import pandas as pd 
import numpy as np
from datetime import datetime

def process_csv(file_path, column_rename_map, column_to_replace=None, replacement_value=None, group_by_columns=None, frequency_column_name="purchase_frequency", transaction_date_column = None, recncy_column_name="recency", save_path=None):
    try:    
        df = pd.read_csv(file_path)
        print("\nOriginal Columns:")
        print(df.columns.tolist())

        df.rename(columns=column_rename_map, inplace=True)
        print("\nUpdated Columns:")
        print(df.columns.tolist())

        # Replace null or specific values in the specified column
        if column_to_replace and column_to_replace in df.columns:
            df[column_to_replace].fillna(replacement_value, inplace=True)  
            print(f"\nNull values in column '{column_to_replace}' have been replaced with '{replacement_value}'.")
        else:
            print("\nNo column replacement specified or column not found.")

        if group_by_columns:
            # Ensure the columns exist in the DataFrame
            if all(col in df.columns for col in group_by_columns):
                df[frequency_column_name] = df.groupby(group_by_columns)[group_by_columns[0]].transform("count")
            else:
                print(f"One or more columns in {group_by_columns} do not exist in the DataFrame.")
    
        # Add a new column for recency
        
        if transaction_date_column and transaction_date_column in df.columns:
            # Convert transaction_date_column to datetime
            df[transaction_date_column] = pd.to_datetime(df[transaction_date_column], errors="coerce")

            # Calculate recency (days since the transaction date)
            current_date = datetime.now()
            df[recncy_column_name] = (current_date - df[transaction_date_column]).dt.days
        else:
            print(f"\nTransaction date column '{transaction_date_column}' not found in the DataFrame.")


        if save_path is None:
            save_path = "F1_test.csv"

        df.to_csv(save_path, index=False)
        print(f"\nProcessed file saved as: {save_path}")

        return df
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

if __name__ == "__main__":
    # Provide the path to your CSV file
    input_file = "C:/Users/athar/Documents/GitHub/baseline_COP2/features/historical_recommendations/feature1_favorites/data/F1_sample_data_1000_consultora_with_date.csv" 


    column_mapping = {
        "CODEBELISTA": "consultant_id",
        "CODPRODUCTOSAP": "product_id",
        "DESCATEGORIA": "category", 
        "DESMARCA": "brand", 
        "PRECIONORMALMN": "price",
        "FECHAPROCESO" : "date"
    }

    # Define the column and replacement value for nulls or other values
    column_to_replace = "category"  # Replace with your column name after renaming
    replacement_value = "Others"            # Value to replace nulls with

    group_by = ["consultant_id", "product_id"]  

    save_file = "C:/Users/athar/Documents/GitHub/baseline_COP2/features/historical_recommendations/feature1_favorites/data/F1_test.csv"
    # Process the file
    process_csv(input_file, column_mapping, column_to_replace, replacement_value, group_by, "purchase_frequency", "date", "recency", save_file)