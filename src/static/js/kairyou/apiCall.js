const isLocal = " {{ is_local }}" ? 'true' : 'false';
const apiUrl = isLocal === 'true' ? "http://api.localhost:5000/v1/kairyou" : "https://api.kakusui.org/v1/kairyou";

function makeApiRequest(apiKey) {
    const textToPreprocess = document.getElementById('textToPreprocess').value;
    let replacementsJson;

    try 
    {
        replacementsJson = JSON.parse(document.getElementById('replacementsJson').value || "{}");
    } catch (error) 
    {
        console.error('Invalid JSON:', error);
        document.getElementById('output').value = 'Invalid JSON. Please ensure that the JSON is valid.';
        return;
    }

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + apiKey,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({textToPreprocess, replacementsJson}),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('preprocessedText').value = data.preprocessedText;
        document.getElementById('preprocessingLog').value = data.preprocessingLog;
        document.getElementById('errorLog').value = data.errorLog;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

document.getElementById('submitButton').addEventListener('click', makeApiRequest);