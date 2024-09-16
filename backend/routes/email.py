## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

## custom imports
from routes.models import EmailRequest


from auth.util import check_internal_request
from auth.func import check_if_admin_user

from util import get_url

router = APIRouter()
