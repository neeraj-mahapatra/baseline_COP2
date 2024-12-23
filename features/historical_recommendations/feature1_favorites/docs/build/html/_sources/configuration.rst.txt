
---

### `configuration.rst`
Details about `config.json`.

```rst
Configuration
=============

The `config.json` file defines key parameters for the feature. Below is an explanation of each section:

### Data Paths
- `input_csv`: Path to the input CSV file.
- `intermediate_csv`: Path for storing processed data.
- `output_csv`: Path for saving the final bundles.

### Parameters
- `alpha`, `beta`: Scoring weights for different metrics.
- `gamma`, `delta`: Weight parameters for bundling.
- `theta`: Threshold for selection.
- `C_max`: Maximum allowed cost for a bundle.
- `k`: Number of anchor products.
- `n_categories`: Number of product categories.
- `num_bundles`: Number of bundles to generate.

### Logging
- `level`: Logging verbosity (e.g., `INFO`, `DEBUG`).

