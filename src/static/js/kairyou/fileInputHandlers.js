/* 
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

function handleFileInput(event, outputElementId) 
{
    var file = event.target.files[0];
    if(!file) 
    {
        return;
    }

    var reader = new FileReader();

    reader.onload = function(e) 
    {
        var content = e.target.result;
        document.getElementById(outputElementId).value = content;
    };
    reader.readAsText(file);

    // Clear the input file after reading
    event.target.value = '';
}

window.addEventListener('load', function() 
{
    document.getElementById('textFileInput').addEventListener('change', function(event) 
    {
        handleFileInput(event, 'textToPreprocess');
    });

    document.getElementById('jsonFileInput').addEventListener('change', function(event) 
    {
        handleFileInput(event, 'replacementsJson');
    });
});
