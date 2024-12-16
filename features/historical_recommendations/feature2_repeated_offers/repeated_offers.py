import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def create_composite_key(row):
    """
    Generate a composite key by concatenating the specified attributes.
    """
    return f"{row['Tipo Subestrategia']}|{row['Tipo Group']}|{row['Producto BPCS']}|{row['Indicator Padre']}|{row['Indicator Gratis']}|{row['Factor De Repeticion']}"

def filter_offers(data):
    """
    Apply filters to the offer dataset.
    Conditions:
    1. OfferType = 'Event Based'
    2. Exclude offers in CAT, REV or DIG
    """
    return data[(data['OfferType'] == 'Event Based') & (~data['OfferCategory'].isin(['CAT', 'REV', 'DIG']))]

def normalize_metrics(df, column):
    """
    Normalize the given column using MinMaxScaler.
    """
    scaler = MinMaxScaler()
    df[f'Normalized_{column}'] = scaler.fit_transform(df[[column]])
    return df

def calculate_recency(reference_date, last_purchase_date):
    """
    Calculate recency as the difference between the reference date and the last purchase date.
    """
    return (reference_date - last_purchase_date).days

def compute_scores(df, alpha=0.5, beta=0.5):
    """
    Calculate composite scores using the formula:
    Score = alpha * Normalized Count + beta * Normalized Recency
    Ensure alpha + beta = 1.
    """
    df['Score'] = alpha * df['Normalized_Count'] + beta * df['Normalized_Recency']
    return df

def find_repeated_offers(df, threshold):
    """
    Identify offers that are repeated more than the threshold value.
    """
    return df[df['Count'] > threshold]

def process_consultora_data(consultora_history, offer_metadata, reference_date, threshold, alpha=0.5, beta=0.5):
    """
    Process the consultora purchase history and offer metadata to find repeated offers.
    """
    # Step 1: Filter the data
    filtered_data = filter_offers(offer_metadata)

    # Step 2: Create composite keys
    consultora_history['Composite_Key'] = consultora_history.apply(create_composite_key, axis=1)

    # Step 3: Join the datasets
    merged_data = pd.merge(consultora_history, filtered_data, on='Composite_Key', how='inner')

    # Step 4: Group and aggregate
    grouped_data = merged_data.groupby(['Consultora_ID', 'Composite_Key']).agg(
        Count=('Composite_Key', 'count'),
        Last_Purchased_Date=('PurchaseDate', 'max')
    ).reset_index()

    # Step 5: Compute recency
    grouped_data['Recency'] = grouped_data['Last_Purchased_Date'].apply(
        lambda x: calculate_recency(reference_date, x))

    # Step 6: Normalize metrics
    grouped_data = normalize_metrics(grouped_data, 'Count')
    grouped_data = normalize_metrics(grouped_data, 'Recency')


    # Step 7: Calculate scores
    grouped_data = compute_scores(grouped_data, alpha, beta)

    # Step 8: Find repeated offers
    repeated_offers = find_repeated_offers(grouped_data, threshold)

    # Step 9: Sort by scores
    repeated_offers = repeated_offers.sort_values(by='Score', ascending=False)

    return repeated_offers

# Example usage
if __name__ == "__main__":
    # Load datasets
    consultora_history = pd.DataFrame({  # Example schema
        'Consultora_ID': [1, 2],
        'Tipo Subestrategia': ['SET VARIABLE', 'SET VARIABLE'],
        'Tipo Group': [343, 344],
        'Producto BPCS': ['LB SPECIAL ANTIMAN DIA 30ML', 'LB BASE ANTIMANCHAS 9 G'],
        'Indicator Padre': [0, 0],
        'Indicator Gratis': [1, 1],
        'Factor De Repeticion': [1, 1],
        'PurchaseDate': [pd.Timestamp('2024-01-01'), pd.Timestamp('2024-01-05')]
    })

    offer_metadata = pd.DataFrame({  # Example schema
        'Composite_Key': ['SET VARIABLE|343|LB SPECIAL ANTIMAN DIA 30ML|0|1|1'],
        'OfferType': ['Event Based'],
        'OfferCategory': ['Normal']
    })

    reference_date = pd.Timestamp('2023-12-01')
    threshold = 1

    result = process_consultora_data(consultora_history, offer_metadata, reference_date, threshold)
    print(result)
