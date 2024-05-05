/* 
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

var kudasaiKeys = ["kutouten", "unicode", "phrases", "single_words", "enhanced_check_whitelist", "full_names", "single_names", "name_like", "honorifics"];
var fukuinKeys = ["specials", "basic", "names", "single-names", "full-names", "name-like", "honorifics"];

function validateJsonKeys(jsonInput) 
{
    var jsonKeys = Object.keys(jsonInput);
    var isValidKudasai = kudasaiKeys.every(key => jsonKeys.includes(key));
    var isValidFukuin = fukuinKeys.every(key => jsonKeys.includes(key));

    if (!isValidKudasai && !isValidFukuin) 
    {
        document.getElementById('errorLog').value = 'JSON input does not match required key sets. Please see https://github.com/Bikatr7/Kairyou?tab=readme-ov-file#usage for more information.';
        return false;
    }
    return true;
}

function validateInputs() 
{
    var textInput = document.getElementById('textToPreprocess').value;
    var jsonInput = document.getElementById('replacementsJson').value;
    var jsonParsed;
    document.getElementById('errorLog').value = ''; // Clear previous errors

    if (!textInput.trim()) 
    {
        document.getElementById('errorLog').value = 'Text input cannot be empty.';
        return false;
    }

    try
    {
        jsonParsed = JSON.parse(jsonInput);
    } 
    catch (e) 
    {
        document.getElementById('errorLog').value = 'Invalid JSON input: ' + e.message;
        return false;
    }

    if(!validateJsonKeys(jsonParsed)) 
        {
        return false;
    }

    return true; // Only returns true if all validations are passed
}
