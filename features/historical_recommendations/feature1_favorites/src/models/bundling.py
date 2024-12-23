# src/models/bundling.py

"""
Module handling bundle construction logic.
"""

from .business_rules import category_score, business_score

class BundleBuilder:
    """
    A class to build product bundles based on scoring logic.
    """

    def __init__(self, gamma: float, delta: float):
        """
        Initializes BundleBuilder with business rule weights.

        Parameters
        ----------
        gamma : float
            Weight for category_score.
        delta : float
            Weight for business_score.
        """
        self.gamma = gamma
        self.delta = delta

    def score_candidates(self, candidates, bundle):
        """
        Calculates the composite score for candidates.

        Parameters
        ----------
        candidates : pd.DataFrame
            The candidate products.
        bundle : list
            Current bundle (list of dicts or rows).

        Returns
        -------
        pd.DataFrame
            Updated candidates DataFrame with a 'score' column.
        """
        candidates = candidates.copy()
        candidates['category_score'] = candidates.apply(lambda p: category_score(p, bundle), axis=1)
        candidates['business_score'] = candidates.apply(business_score, axis=1)
        candidates['score'] = self.gamma * candidates['category_score'] + self.delta * candidates['business_score']
        return candidates

    def build_bundle(self, df, anchor_product, purchasing_power, k, C_max, theta, n_categories):
        """
        Constructs the bundle starting with anchor_product.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing product information.
        anchor_product : pd.Series or dict
            The product chosen as the anchor.
        purchasing_power : float
            Unused in this example, but could factor into logic.
        k : int
            Max size of the bundle.
        C_max : float
            Maximum cost threshold for the bundle.
        theta : float
            Threshold multiplier for item price acceptance.
        n_categories : int
            Number of distinct categories allowed in the bundle.

        Returns
        -------
        list
            A list (bundle) containing the chosen products.
        """
        bundle = [anchor_product]
        current_total_cost = anchor_product['price']
        categories_in_bundle = {anchor_product['category']}

        # Exclude the anchor product from candidates
        candidates = df[df['product_id'] != anchor_product['product_id']]
        candidates = self.score_candidates(candidates, bundle)
        candidates = candidates[candidates['price'] <= theta * C_max].sort_values(by='score', ascending=False)

        for _, candidate in candidates.iterrows():
            if len(bundle) >= k:
                break
            if candidate['category'] in categories_in_bundle:
                # n_categories = 1 => do not add new categories
                if current_total_cost + candidate['price'] <= C_max:
                    bundle.append(candidate)
                    current_total_cost += candidate['price']
                    # We do not add a new category if n_categories=1
            else:
                # If your logic allows new category, incorporate that here
                pass

        return bundle
