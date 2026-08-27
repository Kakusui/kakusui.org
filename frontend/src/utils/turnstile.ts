// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

const DEFAULT_TURNSTILE_SITE_KEY = "0x4AAAAAAAbu-SlGyNF03684";

const TURNSTILE_SITE_KEY = import.meta.env.VITE_TURNSTILE_SITE_KEY || DEFAULT_TURNSTILE_SITE_KEY;

const requiresTurnstile = () =>
{
    const hostname = window.location.hostname;
    return hostname === "kakusui.org" ||
        hostname === "kakusui-org.pages.dev" ||
        hostname.endsWith(".kakusui-org.pages.dev");
};

export { TURNSTILE_SITE_KEY, requiresTurnstile };
