const getURL = (path: string) => 
{
    let url;
    if(import.meta.env.MODE === "production") 
    {
        url = "https://api.kakusui.org";
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