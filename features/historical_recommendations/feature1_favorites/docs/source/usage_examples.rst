Usage Examples
==============

This section shows how to use **Feature 1 Favorites** in your workflow.

### Example Pipeline

The following Python code demonstrates the complete workflow:

.. code-block:: python

    from src.services.favorite_service import FavoriteService

    def main():
        service = FavoriteService()
        df_bundles = service.run_recommendation()
        print(df_bundles)

    if __name__ == "__main__":
        main()

### Sample Data

Ensure the input CSV file is correctly formatted and placed as specified in `config.json`.

- Input: `/data/files/sample_data_1000_C.csv`
- Output: `/data/files/bundles_data_1000_C.csv`

### Run Recommendations

To execute the pipeline, run the `main.py` file:
```bash
python main.py
