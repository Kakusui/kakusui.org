import './ServiceClosed.css';

export default function ServiceClosed()
{
    return (
        <main>
            <h1>Kakusui has shut down</h1>
            <p>
                I'm shutting down Kakusui and EasyTL's hosted services, effective
                immediately. I no longer have time to run them.
            </p>
            <p>
                Translations, API access, sign-in, and new purchases are no longer
                available.
            </p>
            <p>
                Everything remains open source. You can use the code or host it
                yourself. See the repositories below for setup instructions and licenses.
            </p>
            <p className="signature">Kaden Bilyeu</p>

            <h2>Source code</h2>
            <ul>
                <li><a href="https://github.com/ktbilyeu/EasyTL">EasyTL library</a></li>
                <li><a href="https://github.com/Kakusui/EasyTL-Frontend">EasyTL frontend</a></li>
                <li><a href="https://github.com/Kakusui/kakusui.org">Kakusui website and shared backend</a></li>
                <li><a href="https://github.com/ktbilyeu/Kairyou">Kairyou</a></li>
                <li><a href="https://github.com/Kakusui/Elucidate">Elucidate</a></li>
                <li><a href="https://github.com/ktbilyeu/Kudasai">Kudasai</a></li>
            </ul>

            <p className="contact">
                For questions about your account or a past purchase, email{' '}
                <a href="mailto:community@kakusui.org">community@kakusui.org</a>.
            </p>
        </main>
    );
}
