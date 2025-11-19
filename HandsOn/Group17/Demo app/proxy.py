from flask import Flask, request, jsonify
import requests
from flask_cors import CORS  # <--- Importar CORS

app = Flask(__name__)
CORS(app)  # <--- Permitir todas las peticiones cross-origin

GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/AppMadridParks"

@app.route("/sparql", methods=["GET", "POST"])
def sparql_proxy():
    try:
        query = request.args.get("query") or request.data.decode("utf-8")
        if not query:
            return jsonify({"error": "No SPARQL query provided"}), 400

        headers = {
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/sparql-query"
        }

        r = requests.post(GRAPHDB_ENDPOINT, data=query, headers=headers)
        r.raise_for_status()

        return r.json()

    except requests.exceptions.RequestException as e:
        print("RequestException:", e)
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print("Error inesperado:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
