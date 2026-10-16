"""Public entry point: hosted services are closed unless explicitly self-hosted."""

import os

# Fail closed, including for missing or misspelled configuration. Do not import
# providers, authentication, databases or scheduled jobs in retirement mode.
if os.environ.get("HOSTED_SERVICE_CLOSED", "true").lower() == "false":
    from operational_app import app
else:
    from service_closed import app
