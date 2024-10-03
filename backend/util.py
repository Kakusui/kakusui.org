## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

from constants import ENVIRONMENT

async def get_backend_url() -> str:

    """
    Returns the URL of the API based on the environment.
    """

    if(ENVIRONMENT == "development"):
        return "http://api.localhost:5000"
    
    return "https://api.kakusui.org"

async def get_frontend_url() -> str:

    """
    Returns the URL of the frontend based on the environment.
    """

    if(ENVIRONMENT == "development"):
        return "http://localhost:5173"
    
    return "https://kakusui.org"
