# Example API call
# curl -X POST \
#      -H "Content-Type: application/json" \
#      -d '{
#            "alpha": 0.45,
#            "beta": 0.55,
#            "gamma": 0.7,
#            "delta": 0.3,
#            "theta": 1.1,
#            "k": 5,
#            "n_categories": 2,
#            "num_bundles": 4
#          }' \
#      http://localhost:5000/recommend


from flask import Flask, request, jsonify
from feature1_favorites.src.services.favorite_service import FavoriteService
from feature1_favorites.src.utils.variables import VARIABLES

app = Flask(__name__)

@app.route("/recommend", methods=["POST"])
def recommend():
    """
    Endpoint to run the recommendation pipeline with most parameters
    taken from the POST request body, except `purchasing_power` which
    is loaded from `config.json`.
    """

    # Extract existing config from variables
    config_params = VARIABLES["parameters"]

    # Parse request JSON body
    # Example body might look like:
    # {
    #   "alpha": 0.5,
    #   "beta": 0.5,
    #   "gamma": 0.8,
    #   "delta": 0.2,
    #   "theta": 1.1,
    #   "k": 5,
    #   "n_categories": 2,
    #   "num_bundles": 3
    # }
    body = request.get_json() or {}

    # Update parameters from request body,
    # but preserve purchasing_power from config
    config_params["alpha"] = body.get("alpha", config_params["alpha"])
    config_params["beta"] = body.get("beta", config_params["beta"])
    config_params["gamma"] = body.get("gamma", config_params["gamma"])
    config_params["delta"] = body.get("delta", config_params["delta"])
    config_params["theta"] = body.get("theta", config_params["theta"])
    # config_params["C_max"] = body.get("C_max", config_params["C_max"])
    config_params["k"] = body.get("k", config_params["k"])
    config_params["n_categories"] = body.get("n_categories", config_params["n_categories"])
    config_params["num_bundles"] = body.get("num_bundles", config_params["num_bundles"])
    # DO NOT overwrite purchasing_power from request; always use config.
    # config_params["purchasing_power"] = config_params["purchasing_power"]

    try:
        # Now that config_params is updated, pass it into your 
        # RecommendationService or wherever needed.
        favorite_service = FavoriteService(custom_params=config_params)
        
        df_bundles = favorite_service.run_recommendation()
        
        return jsonify({
            "status": "success",
            "message": f"Recommendations generated. {len(df_bundles)} items in final output."
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
