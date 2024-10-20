// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

import CryptoJS from 'crypto-js';

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

// Yes I'm hardcoding these they're meant for client side, no amount of env bullshit can stop a determined bad actor and these are meant for client side code
const getPublishableStripeKey = () => 
{
    if(process.env.NODE_ENV === "production") 
    {
        return "pk_live_51Q3AYgDZ2ylTjcD0ZFhLKsEf5823gU7V9iPkMnJKdSuU7UykedTVWIKyNBO2J8JiI7W02FJUpMtRLFBosN8wL9j600lOZIB17M"
    } 


    return "pk_test_51Q3AYgDZ2ylTjcD0zUGifpIuZ5ydLy8zoU3BHfZt8sdDceeI8DeQ8NRZBzayf1U3hzc16JbDKZWtDQ2Dd1QNlRjW00tUWF4h84"
    
}

const encryptWithAccessToken = (text: string, accessToken: string): string => 
{
  return CryptoJS.AES.encrypt(text, accessToken).toString();
}

const decryptWithAccessToken = (ciphertext: string, accessToken: string): string => 
{
  const bytes = CryptoJS.AES.decrypt(ciphertext, accessToken);
  return bytes.toString(CryptoJS.enc.Utf8);
}

export {getURL, getPublishableStripeKey, encryptWithAccessToken, decryptWithAccessToken};

