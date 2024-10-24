// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React, { useEffect, useRef } from "react";

declare global 
{
    interface Window 
    {
        turnstile: any;
    }
}

type TurnstileProps = 
{
    siteKey: string;
    onVerify: (token: string) => void;
    resetKey: boolean;
};

const Turnstile: React.FC<TurnstileProps> = ({ siteKey, onVerify, resetKey }) => 
{
    const turnstileRef = useRef<HTMLDivElement>(null);
    const widgetId = useRef<number>();

    useEffect(() => 
    {
        const loadTurnstile = () => 
        {
            if (!window.turnstile) 
            {
                const script = document.createElement("script");
                script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js";
                script.async = true;
                script.onload = () => renderTurnstile();
                document.body.appendChild(script);
            } 
            else 
            {
                renderTurnstile();
            }
        };

        const renderTurnstile = () => 
        {
            if (turnstileRef.current) 
            {
                // Store the widget ID for cleanup
                widgetId.current = window.turnstile.render(turnstileRef.current, 
                {
                    sitekey: siteKey,
                    callback: (token: string) => 
                    {
                        onVerify(token);
                    },
                });
            }
        };

        loadTurnstile();

        // Cleanup function
        return () => {
            if (widgetId.current !== undefined) {
                window.turnstile.remove(widgetId.current);
            }
        };
    }, [siteKey, onVerify]);

    useEffect(() => 
    {
        if (resetKey && widgetId.current !== undefined) 
        {
            window.turnstile.reset(widgetId.current);
        }
    }, [resetKey]);

    return <div ref={turnstileRef}></div>;
};

export default Turnstile;