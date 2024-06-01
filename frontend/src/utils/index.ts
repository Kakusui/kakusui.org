/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

const getURL = (path: string) => 
{
    let url;

    if(process.env.NODE_ENV === "production") 
    {
        url = "https://api.kakusui.org";
    } 
    else if (process.env.NODE_ENV === "development") 
    {
        url = "http://api.localhost:5000";
    } 
    
    return url + path;
}

export {getURL};