/* 
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

const isLocal = " {{ is_local }}" ? 'true' : 'false';
const apiUrl = isLocal === 'true' ? "http://api.localhost:5000/v1/kairyou" : "https://api.kakusui.org/v1/kairyou";

function makeApiRequest(apiKey) {
    const textToPreprocess = document.getElementById('textToPreprocess').value;
    const replacementsJsonInput = document.getElementById('replacementsJson').value;
    const preprocessedText = document.getElementById('preprocessedText');
    const preprocessingLog = document.getElementById('preprocessingLog');
    const errorLog = document.getElementById('errorLog');
    
    // Clear old data
    preprocessedText.value = '';
    preprocessingLog.value = '';
    errorLog.value = '';

    let replacementsJson;

    try {
        if(replacementsJsonInput === "") {
            throw new Error('No JSON input');
        }

        replacementsJson = JSON.parse(replacementsJsonInput || "{}");
    } catch (error) {
        console.error('Invalid JSON:', error);
        errorLog.value = 'Invalid JSON. Please ensure that the JSON is correctly formatted.';
        return;
    }

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Authorization': apiKey,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({textToPreprocess, replacementsJson}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.preprocessedText) {
            preprocessedText.value = data.preprocessedText;
            preprocessingLog.value = data.preprocessingLog;
            errorLog.value = data.errorLog || '';
        } else {
            errorLog.value = data.message || 'An error occurred';
        }
    })
    .catch(error => {
        console.error('API error:', error);
        errorLog.value = error.message || 'An error occurred';
    });
}