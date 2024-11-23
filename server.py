from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configuration de l'API CurseForge
CURSEFORGE_API_KEY = os.getenv("CURSEFORGE_API_KEY")
CURSEFORGE_API_BASE_URL = "https://api.curseforge.com/v1"

# En-têtes pour l'API CurseForge
HEADERS = {
    "x-api-key": CURSEFORGE_API_KEY
}

@app.route('/api/<path:endpoint>', methods=['GET'])
def proxy_to_curseforge(endpoint):
    """
    Proxy générique pour interagir avec l'API CurseForge.
    """
    # Construire l'URL cible
    url = f"{CURSEFORGE_API_BASE_URL}/{endpoint}"
    
    # Récupérer les paramètres de requête et le corps de la requête
    query_params = request.args.to_dict()
    data = request.json if request.is_json else None
    
    # Sélectionner la méthode HTTP
    method = request.method
    try:
        # Envoyer la requête correspondante à l'API CurseForge
        if method == "GET":
            response = requests.get(url, headers=HEADERS, params=query_params)
        else:
            return jsonify({"error": "Méthode HTTP non supportée"}), 405

        # Retourner la réponse de l'API CurseForge
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return "Serveur intermédiaire CurseForge opérationnel et prêt à recevoir des requêtes."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=36015)
