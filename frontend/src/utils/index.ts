/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

const getURL = (path: string) => 
{
    let url;
    if(import.meta.env.MODE === "production") 
    {
        url = "http://api.localhost:3000";
    } 
    else if (import.meta.env.MODE === "development") 
    {
        url = "http://api.localhost:5000";
    } 
    else 
    {
        throw new Error(`Invalid environment: ${import.meta.env.MODE}`);
    }
    
    return url + path;
}

export {getURL};