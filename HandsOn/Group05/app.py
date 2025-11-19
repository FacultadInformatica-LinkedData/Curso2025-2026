from flask import Flask, render_template, request, jsonify
from rdflib import Graph

app = Flask(__name__)
g = Graph()
g.parse("rdf/res.ttl", format="turtle")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def run_sparql_query():
    query_text = request.json.get('query')
    
    if not query_text:
        return jsonify({'error': 'No se ha proporcionado consulta'}), 400
    
    try:
        results = g.query(query_text)
        processed_results = []
        for row in results:
            processed_results.append(row.asdict())
            
        return jsonify({'results': processed_results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)