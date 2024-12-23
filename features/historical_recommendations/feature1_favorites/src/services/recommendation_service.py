# src/services/recommendation_service.py

import pandas as pd
from ..data.io import DataIO
from ..data.transformations import Transformer
from utils.bundling import BundleBuilder
from utils.scoring import Scorer
from utils.selection import Selector
from ..utils.variables import INPUT_CSV, INTERMEDIATE_CSV, OUTPUT_CSV, PARAMS  # The default config

class RecommendationService:
    """
    Main service that coordinates the recommendation pipeline.
    """

    def __init__(self, custom_params=None):
        """
        Optionally override the default config params with provided ones.
        """
        self.data_io = DataIO()

        # Merge defaults with any custom params
        merged_params = {**PARAMS, **(custom_params or {})}

        # We still keep `purchasing_power` from `PARAMS`, which is presumably
        # included in `merged_params` if not overwritten.
        # (If you never want to allow it to be overwritten, then just do not
        #  override it in the dictionary merge.)

        self.transformer = Transformer(
            column_rename_map={
                "CODEBELISTA": "consultant_id",
                "CODPRODUCTOSAP": "product_id",
                "DESCATEGORIA": "category",
                "DESMARCA": "brand",
                "PRECIOOFERTA": "price",
                "FECHAPROCESO": "date"
            },
            column_to_replace="category",
            replacement_value="Others",
            group_by_columns=["consultant_id", "date"],
            frequency_column_name="purchase_frequency",
            transaction_date_column="date",
            recncy_column_name="recency"
        )

        self.scorer = Scorer(
            alpha=merged_params["alpha"],
            beta=merged_params["beta"]
        )
        self.selector = Selector()
        self.bundle_builder = BundleBuilder(
            gamma=merged_params["gamma"],
            delta=merged_params["delta"]
        )

        # Keep other params
        self.purchasing_power = merged_params["purchasing_power"]
        self.k = merged_params["k"]
        self.C_max = merged_params["C_max"]
        self.theta = merged_params["theta"]
        self.n_categories = merged_params["n_categories"]
        self.num_bundles = merged_params["num_bundles"]

    def run_recommendation(self) -> pd.DataFrame:
        """
        Runs the full recommendation pipeline and returns a DataFrame of bundles.
        """
        df_raw = self.data_io.read_data_from_csv(INPUT_CSV)
        df_processed = self.transformer.process_csv(df_raw)
        df_processed.to_csv(INTERMEDIATE_CSV, index=False)
        df_scored = self.scorer.calculate_combined_score(df_processed)

        bundles = []
        for consultant_id, group in df_scored.groupby("consultant_id"):
            for bundle_index in range(self.num_bundles):
                anchor_product = self.selector.select_anchor_product(group)
                bundle = self.bundle_builder.build_bundle(
                    df=group,
                    anchor_product=anchor_product,
                    purchasing_power=self.purchasing_power,  # from config
                    k=self.k,
                    C_max=self.C_max,
                    theta=self.theta,
                    n_categories=self.n_categories
                )
                unique_bundle_id = f"{consultant_id}_Bundle_{bundle_index+1}"
                for idx, product in enumerate(bundle):
                    product_copy = product.copy()
                    product_copy["consultant_id"] = consultant_id
                    product_copy["bundle_id"] = unique_bundle_id
                    product_copy["is_anchor"] = 1 if idx == 0 else 0
                    bundles.append(product_copy)

        # Save output CSV
        self.data_io.save_bundle_to_csv(bundles, OUTPUT_CSV)
        return pd.DataFrame(bundles)
