from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import os

app = Flask(__name__)

# load environnement variables
ENV_PATH = "/home/ilwan/.env"
load_dotenv(ENV_PATH)

# configuring curseforge api
CURSEFORGE_API_BASE_URL = "https://api.curseforge.com/v1"
HEADERS = {"x-api-key": os.getenv("CURSEFORGE_API_KEY")}

@app.route("/curseforge/<path:endpoint>", methods=["GET"])
def proxyToCurseforge(endpoint):
    """interact with the curseforge api using the key"""
    # target url
    url = f"{CURSEFORGE_API_BASE_URL}/{endpoint}"
    # query parameters
    query_params = request.args.to_dict()
    # get http method
    method = request.method

    try:
        # send request to curseforge
        if method == "GET":
            response = requests.get(url, headers=HEADERS, params=query_params)
        else:
            return jsonify({"error": "HTTP method not supported"}), 405
        # return query results to the client
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        # send an error if needed
        try:
            return jsonify({"error": str(e)}), response.status_code
        except :
            return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # run the app
    app.run(host="0.0.0.0", port=os.getenv("CURSEFORGE_PROXY_PORT"))
