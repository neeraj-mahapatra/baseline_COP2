# src/models/scoring.py

"""
Module providing scoring computations, e.g., combined frequency/recency scoring.
"""

from .normalization import normalize

class Scorer:
    """
    A class for computing combined scores based on purchase frequency and recency.
    """

    def __init__(self, alpha, beta):
        """
        Initializes Scorer with weighting parameters.
        """
        self.alpha = alpha
        self.beta = beta

    def calculate_combined_score(self, df):
        """
        Calculates a combined score for each row based on normalized frequency and recency.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with 'purchase_frequency' and 'recency' columns.

        Returns
        -------
        pd.DataFrame
            DataFrame including 'combined_score' column.
        """
        df = df.copy()
        min_f = df['purchase_frequency'].min()
        max_f = df['purchase_frequency'].max()
        min_r = df['recency'].min()
        max_r = df['recency'].max()

        df['normalized_f'] = df['purchase_frequency'].apply(lambda x: normalize(x, min_f, max_f))
        df['normalized_r'] = df['recency'].apply(lambda x: normalize(x, min_r, max_r))
        df['combined_score'] = (self.alpha * df['normalized_f']) + (self.beta * df['normalized_r'])

        return df
