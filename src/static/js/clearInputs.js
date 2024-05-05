/* 
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

function clearElements(elementIds) 
{
    elementIds.forEach(function(id) 
    {
        var element = document.getElementById(id);
        if(element) 
        {
            element.value = '';
        }
    });
}