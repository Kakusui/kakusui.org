// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

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

const fetchWithCsrf = async (url: string, options: RequestInit = {}) => {
    // Fetch CSRF token if not already in cookie
    if (!document.cookie.includes('fastapi-csrf-token')) {
        console.log('CSRF token not found in cookie, fetching new token');
        await fetch(`${getURL("/auth/csrf-token")}`, {
            method: 'GET',
            credentials: 'include',
        });
    }

    // Read CSRF token from cookie
    const csrfToken = getCookie('fastapi-csrf-token');
    console.log('CSRF token from cookie:', csrfToken);

    // Set headers
    const headers = new Headers(options.headers);
    if (csrfToken) {
        headers.set('X-CSRF-TOKEN', csrfToken);
        console.log('Setting X-CSRF-TOKEN header:', csrfToken);
    } else {
        console.warn('No CSRF token available to set in header');
    }
    headers.set('Content-Type', 'application/json');

    // Log all headers
    console.log('All request headers:');
    headers.forEach((value, key) => {
        console.log(`${key}: ${value}`);
    });

    // Make the actual request
    const response = await fetch(url, {
        ...options,
        headers,
        credentials: 'include',
    });

    if (!response.ok) {
        console.error('Request failed:', response.status, response.statusText);
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
};

function getCookie(name: string): string {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(';').shift() || '';
    return '';
}

export {getURL, getPublishableStripeKey, fetchWithCsrf, getCookie};

