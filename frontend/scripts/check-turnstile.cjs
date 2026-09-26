// Run with PLAYWRIGHT_MODULE and BROWSER_PATH, or locally installed Playwright.
// The component is bundled in memory. All browser requests are intercepted.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const { build } = require('esbuild');
const assert = require('node:assert/strict');
const path = require('node:path');

(async () => {
    const bundle = await build({
        absWorkingDir: path.resolve(__dirname, '..'),
        stdin: {
            contents: `
                import React, { useState } from 'react';
                import { createRoot } from 'react-dom/client';
                import Turnstile from './src/components/Turnstile';
                import { requiresTurnstile } from './src/utils/turnstile';
                window.requiresTurnstile = requiresTurnstile;
                function Test() {
                    const [token, setToken] = useState('');
                    const [reset, setReset] = useState(0);
                    const [mount, setMount] = useState(0);
                    return <>
                        <output>{token || 'none'}</output>
                        <button onClick={() => setReset(reset + 1)}>Reset</button>
                        <button onClick={() => setMount(mount + 1)}>Remount</button>
                        <Turnstile key={mount} siteKey="test-key" action="feedback"
                            onVerify={setToken} onExpire={() => setToken('')}
                            onError={() => setToken('')} resetKey={reset} />
                    </>;
                }
                createRoot(document.getElementById('root')).render(<Test />);
            `,
            loader: 'tsx',
            resolveDir: path.resolve(__dirname, '..'),
        },
        bundle: true,
        write: false,
        format: 'iife',
        define: { 'import.meta.env': '{}', 'process.env.NODE_ENV': '"production"' },
    });
    const browser = await chromium.launch({
        executablePath: process.env.BROWSER_PATH || undefined,
        headless: true,
    });
    try {
        const page = await browser.newPage();
        let failScript = false;
        let scriptRequests = 0;
        await page.route('**/*', route => {
            const url = new URL(route.request().url());
            if (url.hostname === 'challenges.cloudflare.com') {
                scriptRequests++;
                if (failScript) return route.abort();
                return route.fulfill({ contentType: 'text/javascript', body: `
                    window.widgets = [];
                    window.resetCount = 0;
                    window.removeCount = 0;
                    window.turnstile = {
                        render: (element, options) => {
                            window.widgets.push(options);
                            return String(window.widgets.length);
                        },
                        reset: () => window.resetCount++,
                        remove: () => window.removeCount++,
                    };
                ` });
            }
            if (url.pathname === '/test.js')
                return route.fulfill({ contentType: 'text/javascript', body: bundle.outputFiles[0].text });
            return route.fulfill({ contentType: 'text/html', body: '<div id="root"></div><script src="/test.js"></script>' });
        });
        await page.goto('https://kakusui.org');
        await page.waitForFunction(() => window.widgets?.length === 1);
        assert.equal(await page.evaluate(() => window.widgets[0].action), 'feedback');
        for (const callback of ['expired-callback', 'error-callback', 'timeout-callback']) {
            await page.evaluate(() => window.widgets[0].callback('test-token'));
            await page.waitForFunction(() => document.querySelector('output').textContent === 'test-token');
            await page.evaluate(key => window.widgets[0][key](), callback);
            await page.waitForFunction(() => document.querySelector('output').textContent === 'none');
        }
        assert.equal(await page.evaluate(() => window.widgets.length), 1, 'State updates recreated the widget');
        await page.getByRole('button', { name: 'Reset', exact: true }).click();
        await page.getByRole('button', { name: 'Reset', exact: true }).click();
        assert.equal(await page.evaluate(() => window.resetCount), 2);
        await page.getByRole('button', { name: 'Remount' }).click();
        await page.waitForFunction(() => window.widgets.length === 2);
        assert.equal(await page.evaluate(() => window.removeCount), 1);
        for (const [hostname, expected] of [
            ['kakusui.org', true], ['kakusui.org.', true], ['easytl.org', true],
            ['kakusui-org.pages.dev', true], ['easytl-frontend.pages.dev', true],
            ['preview.kakusui-org.pages.dev', true], ['localhost', false],
            ['kakusui.org.attacker.example', false], ['evil-kakusui-org.pages.dev', false],
        ]) {
            await page.goto('https://' + hostname);
            await page.waitForFunction(() => typeof window.requiresTurnstile === 'function');
            assert.equal(await page.evaluate(() => window.requiresTurnstile()), expected, hostname);
        }
        failScript = true;
        scriptRequests = 0;
        await page.goto('https://kakusui.org');
        await page.waitForFunction(() => document.querySelector('output'));
        await page.waitForFunction(() => !document.getElementById('cloudflare-turnstile-script'));
        assert.equal(scriptRequests, 1);
        await page.getByRole('button', { name: 'Remount' }).click();
        await page.waitForFunction(() => !document.getElementById('cloudflare-turnstile-script'));
        assert.equal(scriptRequests, 2, 'Failed script prevented retry');
        console.log('PASS: token expiry/error/timeout, repeat reset, cleanup, host matching, failed-script retry');
    } finally {
        await browser.close();
    }
})().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
