const getURL = (path: string) => {
    let url;
    switch (import.meta.env.MODE) {
        case "PRODUCTION":
            url = "https://api.kakusui.org";
            break;
        case "DEVELOPMENT":
        default:
            url = "http://api.localhost:5000"
    }
    return url + path;
}

export {getURL};