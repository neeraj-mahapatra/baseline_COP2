# src/models/scoring.py

"""
Module providing scoring computations, e.g., combined frequency/recency scoring.
"""


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
        Calculates a combined score for each row based on pre-normalized frequency and recency.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with pre-normalized 'normalized_recency' and 'normalized_count' columns.

        Returns
        -------
        pd.DataFrame
            DataFrame including 'score' column with rows sorted in descending order of score.
        """
        df = df.copy()

        # Calculate the combined score using the pre-normalized columns
        df['score'] = (self.alpha * df['normalized_recency']) + (self.beta * df['normalized_count'])

        # Sort by the score in descending order
        df = df.sort_values('score', ascending=False).reset_index(drop=True)

        return df

