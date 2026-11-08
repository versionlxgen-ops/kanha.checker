from flask import Flask, request, jsonify
from flask_cors import CORS
from services.steam import check_steam_account
from services.crunchyroll import check_crunchyroll_account
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/check', methods=['POST', 'OPTIONS'])
def check_route():
    if request.method == 'OPTIONS': return '', 200
    
    data = request.json
    service = data.get('service')
    combos = data.get('combos', [])
    results = []
    
    for combo in combos:
        if ':' not in combo: continue
        u, p = combo.split(':', 1)
        
        # ACÁ DERIVA EL TRABAJO AL ARCHIVO CORRESPONDIENTE
        if service == 'steam': 
            res = check_steam_account(u, p)
        elif service == 'crunchyroll': 
            res = check_crunchyroll_account(u, p)
        else: 
            res = {"valid": False, "reason": "Servicio no soportado"}

        results.append({"email": u, "valid": res["valid"], "reason": res["reason"]})
        
    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
