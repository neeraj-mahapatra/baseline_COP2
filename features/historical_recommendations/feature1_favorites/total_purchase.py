import numpy as np
import pandas as pd

def calculate_total_price(input_file, output_file):
    """
    Calculate the total price of products a user has purchased on a particular date.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: A DataFrame with user_id, date, and total_price columns.
    """
    # Load the CSV file
    df = pd.read_csv(input_file)

    # Ensure the 'date' column is in datetime format
    df['Date'] = pd.to_datetime(df['FECHAPROCESO'])

    # Group by user_id and date, then sum the prices
    result = df.groupby(['CODEBELISTA', 'FECHAPROCESO'], as_index=False).agg({
        'PRECIOOFERTA': 'sum',       # Sum the price column
        'PRECIOOFERTA': 'first'      # Keep the first value of COLUMN2
        # Add more columns here as needed
    })

    result.rename(columns={'PRECIOOFERTA': 'total_price'}, inplace=True)

    # Save the results to a new CSV file
    result.to_csv(output_file, index=False)
    return result

# Example usage
input_file = 'C:/Users/athar/Documents/GitHub/baseline_COP2/features/historical_recommendations/feature1_favorites/data/F1_SAMPLE_DATA_WITH_OFFER_PRICE_OTHER_THAN_ZERO.csv'  # Path to the input CSV file
column_name = 'PRECIOOFERTA'      # price
output_file = 'C:/Users/athar/Documents/GitHub/baseline_COP2/features/historical_recommendations/feature1_favorites/data/Total_purchase.csv'  # Path to save the results

# Call the function
results = calculate_total_price(input_file, output_file)
print("Total purchase calculation results saved to:", output_file)
print(results)
