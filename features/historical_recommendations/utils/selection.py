# src/models/selection.py

"""
Module containing selection logic for picking an anchor product.
"""

class Selector:
    """
    A class for selecting products as anchors and generating candidate sets.
    """

    def select_anchor_product(self, df):
        """
        Selects the product with the maximum 'combined_score'.
        """
        return df.loc[df['combined_score'].idxmax()]

    def generate_candidates(self, bundle, df):
        """
        Returns products not already in the bundle.
        """
        bundle_product_ids = {p['product_id'] for p in bundle}
        return df[~df['product_id'].isin(bundle_product_ids)]
