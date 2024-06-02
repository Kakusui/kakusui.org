/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU Lesser General Public License v2.1
license that can be found in the LICENSE file.
*/

import React, { useEffect, useRef } from "react";

declare global {
    interface Window {
        turnstile: any;
    }
}

type TurnstileProps = {
    siteKey: string;
    onVerify: (token: string) => void;
};

const Turnstile: React.FC<TurnstileProps> = ({ siteKey, onVerify }) => {
    const turnstileRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const loadTurnstile = () => {
            if (!window.turnstile) {
                const script = document.createElement("script");
                script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js";
                script.async = true;
                script.onload = () => renderTurnstile();
                document.body.appendChild(script);
            } else {
                renderTurnstile();
            }
        };

        const renderTurnstile = () => {
            if (turnstileRef.current) {
                window.turnstile.render(turnstileRef.current, {
                    sitekey: siteKey,
                    callback: (token: string) => {
                        onVerify(token);
                    },
                });
            }
        };

        loadTurnstile();
    }, [siteKey, onVerify]);

    return <div ref={turnstileRef}></div>;
};

export default Turnstile;
