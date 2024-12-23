# Example API call
# curl -X POST \
#      -H "Content-Type: application/json" \
#      -d '{
#            "alpha": 0.45,
#            "beta": 0.55,
#            "k": 5,
#            "composite_key_separator": |,
#          }' \
#      http://localhost:5000/repeated_offers


from flask import Flask, request, jsonify
from src.services.repeated_offers_service import RepeatedOfferService
from src.utils.variables import VARIABLES

app = Flask(__name__)

@app.route("/repeated_offers", methods=["POST"])
def repeat_offers():

    # Extract existing config from variables
    config_params = VARIABLES["parameters"]

    # Parse request JSON body
    # Example body might look like:
    # {
    #   "alpha": 0.5,
    #   "beta": 0.5,
    #   "k": 5,
    #   "composite_key_separator": |,
    # }
    body = request.get_json() or {}

    # Update parameters from request body,
    # but preserve purchasing_power from config
    config_params["alpha"] = body.get("alpha", config_params["alpha"])
    config_params["beta"] = body.get("beta", config_params["beta"])
    config_params["k"] = body.get("k", config_params["k"])
    config_params["composite_key_separator"] = body.get("composite_key_separator", config_params["composite_key_separator"])

    try:
        # Now that config_params is updated, pass it into your 
        # RepeatedOfferService or wherever needed.
        repeated_offers_service = RepeatedOfferService(custom_params=config_params)
        
        df_offers = repeated_offers_service.run_repeated_offers()
        
        return jsonify({
            "status": "success",
            "message": f"Repeated offers. {len(df_offers)} Offers in final output."
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
