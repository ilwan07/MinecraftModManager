from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

apiKey = os.getenv("CURSEFORGE_API_KEY")  # environnement variable with API key
curseforgeApiUrl = "https://api.curseforge.com"  # curseforge api url

@app.route("/curseforge", methods=["GET"])
def query_curseforge():
    """curseforge proxy"""
    endpoint = request.args.get("endpoint")  # path to curseforge api
    params = request.args.to_dict()  # get arguments from request
    params.pop("endpoint", None)  # remove endpoint from arguments

    if not endpoint:
        return jsonify({"error": "Endpoint is required"}), 400

    # make request to curseforge api
    headers = {
        "x-api-key": apiKey,
    }
    try:
        response = requests.get(f"{curseforgeApiUrl}/{endpoint}", headers=headers, params=params)
        response.raise_for_status()
        return jsonify(response.json())  # return raw response
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=36015)  # open port
