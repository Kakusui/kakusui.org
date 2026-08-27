// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

import { useEffect, useRef } from "react";

type TurnstileWidgetOptions =
{
    sitekey: string;
    action?: string;
    callback: (token: string) => void;
    "expired-callback": () => void;
    "error-callback": () => void;
};

type TurnstileApi =
{
    render: (container: HTMLElement, options: TurnstileWidgetOptions) => string;
    remove: (widgetId: string) => void;
    reset: (widgetId: string) => void;
};

declare global
{
    interface Window
    {
        turnstile?: TurnstileApi;
    }
}

type TurnstileProps =
{
    siteKey: string;
    action?: string;
    onVerify: (token: string) => void;
    onExpire?: () => void;
    onError?: () => void;
    resetKey?: number | boolean;
};

const SCRIPT_ID = "cloudflare-turnstile-script";
const SCRIPT_URL = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";

const Turnstile = ({ siteKey, action, onVerify, onExpire, onError, resetKey = 0 }: TurnstileProps) =>
{
    const containerRef = useRef<HTMLDivElement>(null);
    const widgetIdRef = useRef<string>();
    const previousResetKeyRef = useRef(resetKey);
    const onVerifyRef = useRef(onVerify);
    const onExpireRef = useRef(onExpire);
    const onErrorRef = useRef(onError);

    onVerifyRef.current = onVerify;
    onExpireRef.current = onExpire;
    onErrorRef.current = onError;

    useEffect(() =>
    {
        let cancelled = false;

        const renderWidget = () =>
        {
            if(cancelled || !containerRef.current || !window.turnstile || widgetIdRef.current)
            {
                return;
            }

            widgetIdRef.current = window.turnstile.render(containerRef.current,
            {
                sitekey: siteKey,
                action,
                callback: (token: string) => onVerifyRef.current(token),
                "expired-callback": () => onExpireRef.current?.(),
                "error-callback": () => onErrorRef.current?.(),
            });
        };

        const handleScriptError = () => onErrorRef.current?.();

        if(window.turnstile)
        {
            renderWidget();
        }
        else
        {
            let script = document.getElementById(SCRIPT_ID) as HTMLScriptElement | null;
            if(!script)
            {
                script = document.createElement("script");
                script.id = SCRIPT_ID;
                script.src = SCRIPT_URL;
                script.async = true;
                script.defer = true;
                document.head.appendChild(script);
            }

            script.addEventListener("load", renderWidget);
            script.addEventListener("error", handleScriptError);
        }

        return () =>
        {
            cancelled = true;
            const script = document.getElementById(SCRIPT_ID);
            script?.removeEventListener("load", renderWidget);
            script?.removeEventListener("error", handleScriptError);

            if(widgetIdRef.current && window.turnstile)
            {
                window.turnstile.remove(widgetIdRef.current);
                widgetIdRef.current = undefined;
            }
        };
    }, [siteKey, action]);

    useEffect(() =>
    {
        if(previousResetKeyRef.current === resetKey)
        {
            return;
        }

        previousResetKeyRef.current = resetKey;
        if(widgetIdRef.current && window.turnstile)
        {
            window.turnstile.reset(widgetIdRef.current);
        }
    }, [resetKey]);

    return <div ref={containerRef}></div>;
};

export default Turnstile;
