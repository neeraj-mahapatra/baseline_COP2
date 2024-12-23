# src/services/recommendation_service.py

import pandas as pd
from ..data.io import DataIO
from ..data.transformations import Transformer

from ..models.scoring import Scorer

from ..utils.variables import * # The default config

class RepeatedOfferService:
    """
    Main service that coordinates the repeated offers pipeline.
    """

    def __init__(self, custom_params=None):
        """
        Optionally override the default config params with provided ones.
        """
        self.data_io = DataIO()

        # Merge defaults with any custom params
        merged_params = {**PARAMS, **(custom_params or {})}

        self.transformer = Transformer(
            column_rename_map={
                "DES_TIPO_SUBESTRATEGIA": "sub_stratergy",
                "DES_TIPO_GRUPO": "group_type",
                "CODCUC": "product_cuc",
                "ES_PADRE": "is_father",
                "ES_GRATIS": "is_free",
                "FACTOR_REPETICION": "factor_repetition",
                "CODEBELISTA": "consultant_id",
                "FECHAPROCESO": "date",
                "ID_OFERTA": "offer_id"
            },
            composite_key_columns_list=["sub_stratergy","group_type","product_cuc","is_father","is_free","factor_repetition"],
            composite_key_seperator = '|', 
            column_to_drop = "COMPOSITE_PRIMARY_KEY",
            column_to_filter= "product_cuc", 
            column_to_filter_value= "XXXXXXXXX",
            group_by_columns_list= ["offer_id", "consultant_id", "Composite_key"],
            group_by_offer_column = "offer_id",
            explode_by_column = "consultant_id",
            frequency_column_name="frequency",
            composite_key_column_name = "Composite_key", 
            transaction_date_column= "date",
            reference_date = "2024-12-29",
            recncy_column_name="recency")

        self.scorer = Scorer(
            alpha=merged_params["alpha"],
            beta=merged_params["beta"]
        )


        # Keep other params
        self.k = merged_params["k"]
        self.composite_key_separator = merged_params["composite_key_separator"]

    def run_repeated_offers(self) -> pd.DataFrame:
        """
        Runs the full repeated offers pipeline and returns a DataFrame of offers.
        """
        df_raw = self.data_io.read_data_from_csv(INPUT_CSV)
        df_processed = self.transformer.process_csv(df_raw)
        df_scored = self.scorer.calculate_combined_score(df_processed)

        offers = df_scored[REQUIRED_OUTPUT_FIELDS].head(self.k).values.tolist()
        df_scored.to_csv(OUTPUT_CSV)

        return pd.DataFrame(offers)
