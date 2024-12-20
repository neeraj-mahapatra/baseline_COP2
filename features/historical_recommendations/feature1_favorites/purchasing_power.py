import numpy as np
import pandas as pd

def calculate_iqr_and_save(input_file, column_name, output_file):
    # Read the dataset from the input file
    df = pd.read_csv(input_file)
    
    # Check if the column exists in the dataset
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in the dataset.")

    # Extract the desired column as a numpy array
    data = df[column_name].dropna().values  # Drop NaN values

    # Calculate Q1 and Q3 (25th and 75th percentiles)
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)

    # Calculate IQR (Interquartile Range)
    IQR = Q3 - Q1

    # Calculate the upper bound based on IQR
    upper_bound = Q3 + 1.5 * IQR

    # Prepare the results to be saved in a dictionary
    results = {
        'Q1': Q1,
        'Q3': Q3,
        'IQR': IQR,
        'Upper Bound': upper_bound
    }

    # Save the results to a new CSV file (you can also use other formats like Excel)
    result_df = pd.DataFrame([results])
    result_df.to_csv(output_file, index=False)

    return results

# Example usage
input_file = 'C:/Users/athar/Documents/GitHub/baseline_COP2/features/historical_recommendations/feature1_favorites/data/F1_SAMPLE_DATA_WITH_OFFER_PRICE_OTHER_THAN_ZERO.csv'  # Path to the input CSV file
column_name = 'PRECIOOFERTA'      # price
output_file = 'C:/Users/athar/Documents/GitHub/baseline_COP2/features/historical_recommendations/feature1_favorites/data/IQR_Result.csv'  # Path to save the results

# Call the function
results = calculate_iqr_and_save(input_file, column_name, output_file)
print("IQR calculation results saved to:", output_file)
print(results)
