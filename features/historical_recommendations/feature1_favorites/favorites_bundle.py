import pandas as pd
import random

alpha = 0.5  
beta = 0.5   
purchasing_power = 100.0
k = 2  
C_max = 100.0  
theta = 1  
gamma = 0.6  
delta = 0.4  
n_categories = 2  
num_bundles = 2
input_csv = "/Users/mindstix/Documents/baseline_COP2/features/historical_recommendations/feature1_favorites/data/consultant_products.csv"  
output_csv = "/Users/mindstix/Documents/baseline_COP2/features/historical_recommendations/feature1_favorites/data/bundles.csv"  

def read_data_from_csv(csv_path):
    """Read product data from CSV."""
    return pd.read_csv(csv_path)

def save_bundle_to_csv(bundle, output_path):
    """Save the final bundle to a CSV file."""
    bundle_df = pd.DataFrame(bundle)
    bundle_df.to_csv(output_path, index=False)

def normalize(value, min_value, max_value):
    """Normalize the value to a common scale between 0 and 1."""
    if min_value == max_value:
        return 0  # or 1, depending on how you want to handle this case
    return (value - min_value) / (max_value - min_value)

# This function calculates a combined score for each product based on its purchase frequency and recency, 
# with weights applied to each factor. It normalizes both values to a scale of [0, 1] to ensure comparability, 
# and then uses the weights (alpha and beta) to create the combined score.
def calculate_combined_score(df, alpha, beta):
    """Calculate combined score using purchase frequency and recency."""
    min_f = df['purchase_frequency'].min()
    max_f = df['purchase_frequency'].max()
    min_r = df['recency'].min()
    max_r = df['recency'].max()
    
    df = df.copy()  # Ensure we're working with a copy here
    df['normalized_f'] = df['purchase_frequency'].apply(lambda x: normalize(x, min_f, max_f))
    df['normalized_r'] = df['recency'].apply(lambda x: normalize(x, min_r, max_r))
    
    df['combined_score'] = (alpha * df['normalized_f']) + (beta * df['normalized_r'])
    return df

def select_anchor_product(df):
    """Select the anchor product based on the highest combined score."""
    return df.loc[df['combined_score'].idxmax()]

def generate_candidates(bundle, df, n_categories):
    """Generate candidate products related to the bundle, ensuring diversity in categories."""
    
    # Extract the product IDs and categories from the bundle
    bundle_product_ids = [p['product_id'] for p in bundle]
    # bundle_categories = set(p['category'] for p in bundle)
    
    # Find related products based on categories
    related_products = set()
    for product in bundle:
        related_products.update(df[df['category'] == product['category']]['product_id'])
    
    # Allow for products from other categories if bundle is not diverse enough
    candidates = df[~df['product_id'].isin(bundle_product_ids) & df['product_id'].isin(related_products)]
    
    # Ensure diversity: we can add products from other categories if needed
    categories_in_bundle = set(p['category'] for p in bundle)
    if len(categories_in_bundle) < n_categories:
        additional_candidates = df[~df['product_id'].isin(bundle_product_ids)]
        candidates = pd.concat([candidates, additional_candidates])
    
    return candidates


def score_candidates(candidates, bundle, gamma, delta):
    """Score candidates based on category and business rules."""
    
    # Define the category score function to promote diversity
    def category_score(p):
        # If product's category is NOT in the bundle's categories, score 1 (promote diversity)
        return 1 if p['category'] not in [b['category'] for b in bundle] else 0
    
    # Define the business score function
    def business_score(p):
        # Use some business rule or logic for scoring. Here, we use random as a placeholder.
        return random.random()  # Replace with actual business logic or scoring

    # Ensure working with a copy of the DataFrame
    candidates = candidates.copy()
    
    # Apply the scoring functions
    candidates['category_score'] = candidates.apply(category_score, axis=1)
    candidates['business_score'] = candidates.apply(business_score, axis=1)
    
    # Calculate the final score as a weighted sum
    candidates['score'] = gamma * candidates['category_score'] + delta * candidates['business_score']
    
    return candidates


def build_bundle(df, anchor_product, purchasing_power, alpha, beta, k, C_max, theta, gamma, delta, n_categories):
    """Build the bundle for a consultant while ensuring diversity in categories."""
    bundle = [anchor_product]
    current_total_cost = anchor_product['price']
    
    # Track categories in the bundle
    categories_in_bundle = {anchor_product['category']}
    
    while len(bundle) < k:  # Ensure we don't exceed the desired bundle size 'k'
        # Generate candidate products, allowing for multiple categories
        candidates = generate_candidates(bundle, df, n_categories)
        
        # Calculate combined score for the candidates
        candidates = calculate_combined_score(candidates, alpha, beta)
        candidates = score_candidates(candidates, bundle, gamma, delta)
        
        # Filter candidates based on price constraint
        candidates = candidates[candidates['price'] <= theta * C_max]
        
        if not candidates.empty:
            # Select the product with the highest score
            next_product = candidates.loc[candidates['score'].idxmax()]
            next_product = next_product if isinstance(next_product, pd.Series) else next_product.iloc[0]
            price = next_product['price']
            
            # Check if adding this product respects the purchasing power and total cost
            if current_total_cost + price <= C_max:
                bundle.append(next_product)
                current_total_cost += price
                categories_in_bundle.add(next_product['category'])
        else:
            # Exit if no valid candidates are available
            break
    
    return bundle




# Read data from CSV
df = read_data_from_csv(input_csv)
bundles = []

# Iterate over each consultant
for consultant_id, group in df.groupby('consultant_id'):
    print(f"Generating bundles for Consultant {consultant_id}")
    
    for bundle_id in range(num_bundles):  # Generate 'num_bundles' bundles for each consultant
        unique_bundle_id = f"{consultant_id}_Bundle_{bundle_id + 1}"
        print(f"unique_bundle_id - {unique_bundle_id}")
        
        # Calculate combined score for each product in this group
        group = calculate_combined_score(group, alpha, beta)
        print(f"group - {group}")
        
        # Select the anchor product for the consultant
        anchor_product = select_anchor_product(group)
        print(f"anchor_product - {anchor_product}")
        
        # Build the bundle for the consultant
        bundle = build_bundle(group, anchor_product, purchasing_power, alpha, beta, k, C_max, theta, gamma, delta, n_categories)
        print(f"bundle - {bundle}")
        
        for idx, product in enumerate(bundle):
            product_copy = product.copy()  # Ensure that we are working with a copy
            product_copy['consultant_id'] = consultant_id
            product_copy['bundle_id'] = unique_bundle_id  # Add the unique bundle_id to the product
            
            # Mark the anchor product as 1, others as 0
            product_copy['is_anchor'] = 1 if idx == 0 else 0
            
            bundles.append(product_copy)

# Save the final bundles to CSV
save_bundle_to_csv(bundles, output_csv)